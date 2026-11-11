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
