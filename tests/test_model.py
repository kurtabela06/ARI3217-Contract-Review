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
