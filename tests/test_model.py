import numpy as np
import scipy.sparse as sp

from contract_review.model import fit_linear


def test_training_is_repeatable_and_returns_usable_models():
    features = sp.csr_matrix(
        [[2, 0], [0, 2], [3, 0], [0, 3], [1, 0], [0, 1]],
        dtype=np.float32,
    )
    labels = np.array([[1], [0], [1], [0], [1], [0]])
    training = np.array([True, True, True, True, False, False])

    a, count_a, models_a = fit_linear(
        features, training, labels, ["Example"],
        negative_sample=1.0,
    )
    b, count_b, _ = fit_linear(
        features, training, labels, ["Example"],
        negative_sample=1.0,
    )

    assert count_a == count_b == 4
    assert a.shape == (6, 1)
    assert np.isfinite(a).all()
    np.testing.assert_allclose(a, b)
    np.testing.assert_allclose(
        a[:, 0],
        models_a["Example"].decision_function(features),
        rtol=1e-6,
        atol=1e-6,
    )


def test_calibration_uses_only_selected_labels_and_can_be_reapplied():
    from contract_review.model import calibrate, apply_calibration

    scores = np.array(
        [[-2], [-1], [1], [2], [-0.5], [0.5]],
        dtype=np.float32,
    )
    labels = np.array([[0], [0], [1], [1], [0], [1]])
    validation = np.array([True, True, True, True, False, False])

    probabilities, parameters = calibrate(
        scores, validation, labels
    )

    changed_labels = labels.copy()
    changed_labels[~validation] = 1 - changed_labels[~validation]
    _, other_parameters = calibrate(
        scores, validation, changed_labels
    )

    np.testing.assert_allclose(parameters, other_parameters)
    np.testing.assert_allclose(
        probabilities,
        apply_calibration(scores, parameters),
    )
    assert np.isfinite(probabilities).all()
    assert ((probabilities >= 0) & (probabilities <= 1)).all()


def test_zero_calibration_parameters_produce_half_probability():
    from contract_review.model import apply_calibration

    scores = np.array([[-10], [0], [10]], dtype=np.float32)
    parameters = np.array([[0.0, 0.0]])

    np.testing.assert_allclose(
        apply_calibration(scores, parameters),
        [[0.5], [0.5], [0.5]],
    )
