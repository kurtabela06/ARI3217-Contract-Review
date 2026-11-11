import numpy as np
import scipy.sparse as sp
from sklearn.feature_extraction.text import CountVectorizer

from contract_review.features import bm25_matrix, query_matrix


def test_queries_ignore_unknown_terms_and_do_not_count_repetitions():
    vectorizer = CountVectorizer(ngram_range=(1, 2))
    vocabulary = np.array(["alpha", "beta gamma"])

    result = query_matrix(
        ["alpha alpha unknown", "beta gamma"],
        vectorizer,
        vocabulary,
    )

    np.testing.assert_array_equal(
        result.toarray(),
        [[1, 0], [0, 1]],
    )


def test_bm25_training_weights_ignore_changes_to_nontraining_rows():
    counts = sp.csr_matrix(
        [[2, 0], [0, 1], [9, 9]],
        dtype=np.float32,
    )
    original = counts.copy()
    training = np.array([True, True, False])

    first = bm25_matrix(counts, training)

    changed = counts.toarray()
    changed[2] = [900, 1]
    second = bm25_matrix(sp.csr_matrix(changed), training)

    np.testing.assert_allclose(
        first[:2].toarray(),
        second[:2].toarray(),
    )
    np.testing.assert_array_equal(
        counts.toarray(),
        original.toarray(),
    )
