"""Text representations used by the supplied clause extractor."""

import scipy.sparse as sp
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer


TOKEN = r"(?u)\b[a-zA-Z][a-zA-Z-]+\b"


def build_counts(chunks, train_mask, max_features=150_000):
    """Return passage counts, selected vocabulary and fitted vectorizer."""
    vectorizer = CountVectorizer(
        ngram_range=(1, 2),
        min_df=3,
        token_pattern=TOKEN,
        dtype=np.float32,
    )

    counts = vectorizer.fit_transform(chunks.text).tocsc()

    training_frequency = np.asarray(
        (counts[train_mask] > 0).sum(0)
    ).ravel()

    keep = np.argsort(-training_frequency)[:max_features]
    keep = np.sort(keep[training_frequency[keep] >= 3])

    counts = counts[:, keep].tocsr()
    vocabulary = vectorizer.get_feature_names_out()[keep]

    return counts, vocabulary, vectorizer


def bm25_matrix(counts, fit_rows, k1=1.5, b=0.75):
    """Weight passage counts using training-partition statistics."""
    n = fit_rows.sum()
    frequency = np.asarray(
        (counts[fit_rows] > 0).sum(0)
    ).ravel()

    idf = np.log(
        (n - frequency + 0.5) / (frequency + 0.5) + 1
    ).astype(np.float32)

    lengths = np.asarray(counts.sum(1)).ravel()
    average_length = lengths[fit_rows].mean()

    weighted = counts.copy()
    rows = np.repeat(
        np.arange(weighted.shape[0]),
        np.diff(weighted.indptr),
    )

    weighted.data = (
        weighted.data * (k1 + 1)
        / (
            weighted.data
            + k1 * (
                1 - b + b * lengths[rows] / average_length
            )
        )
        * idf[weighted.indices]
    )
    return weighted


def query_matrix(queries, vectorizer, vocabulary):
    """Represent category queries using the selected passage vocabulary."""
    analyse = vectorizer.build_analyzer()
    columns = {
        term: i for i, term in enumerate(vocabulary)
    }
    matrix = np.zeros(
        (len(queries), len(vocabulary)),
        dtype=np.float32,
    )

    for i, query in enumerate(queries):
        for term in set(analyse(query)):
            if term in columns:
                matrix[i, columns[term]] = 1

    return sp.csr_matrix(matrix)


def details(question):
    """Extract the descriptive part of a supplied category question."""
    return question.split("Details:")[-1].strip()


def build_classifier_features(counts, chunks, train_mask):
    """Apply the notebook's TF-IDF and passage-position features."""
    from sklearn.feature_extraction.text import TfidfTransformer

    transformer = TfidfTransformer(
        sublinear_tf=True
    ).fit(counts[train_mask])

    relative_position = chunks.relpos.values
    position_features = sp.csr_matrix(
        np.c_[
            relative_position,
            relative_position < 0.02,
            relative_position < 0.1,
            relative_position > 0.9,
        ].astype(np.float32)
    )

    features = sp.hstack([
        transformer.transform(counts),
        position_features,
    ]).tocsr()

    return features, transformer
