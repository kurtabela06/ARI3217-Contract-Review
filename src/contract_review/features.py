"""Text representations used by the supplied clause extractor."""

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
