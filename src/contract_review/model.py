"""Training functions for the supplied clause classifier."""

import numpy as np
from sklearn.svm import LinearSVC


def fit_linear(
    features,
    train_mask,
    labels,
    categories,
    seed=3217,
    negative_sample=0.25,
    C=0.3,
):
    """Train the supplied per-category SVMs and return scores and models."""
    keep = train_mask & (
        labels.any(axis=1)
        | (
            np.random.default_rng(seed).random(len(labels))
            < negative_sample
        )
    )

    scores = np.zeros(
        (features.shape[0], len(categories)),
        dtype=np.float32,
    )
    models = {}

    for j, category in enumerate(categories):
        if labels[keep, j].sum():
            model = LinearSVC(
                C=C,
                class_weight="balanced",
                tol=1e-2,
                random_state=seed,
            ).fit(features[keep], labels[keep, j])

            scores[:, j] = model.decision_function(features)
            models[category] = model

    return scores, int(keep.sum()), models


def calibrate(scores, fit_mask, labels):
    """Fit the notebook's calibration and return probabilities and parameters."""
    probabilities = np.zeros_like(scores)
    parameters = np.zeros((scores.shape[1], 2))

    for j in range(scores.shape[1]):
        y = labels[fit_mask, j]
        s = scores[fit_mask, j]
        a, b = 1.0, 0.0

        for _ in range(25):
            p = 1 / (1 + np.exp(-(a * s + b)))
            w = p * (1 - p)

            gradient = np.array([
                ((p - y) * s).sum() + 1e-3 * a,
                (p - y).sum(),
            ])
            hessian = np.array([
                [
                    (w * s * s).sum() + 1e-3,
                    (w * s).sum(),
                ],
                [
                    (w * s).sum(),
                    w.sum() + 1e-9,
                ],
            ])

            a, b = np.array([a, b]) - np.linalg.solve(
                hessian, gradient
            )

        probabilities[:, j] = 1 / (
            1 + np.exp(-(a * scores[:, j] + b))
        )
        parameters[j] = [a, b]

    return probabilities, parameters


def apply_calibration(scores, parameters):
    """Apply saved calibration without fitting on incoming data."""
    probabilities = np.zeros_like(scores)

    for j, (a, b) in enumerate(parameters):
        probabilities[:, j] = 1 / (
            1 + np.exp(-(a * scores[:, j] + b))
        )

    return probabilities
