"""Score new contracts using a fitted serving bundle."""

import numpy as np
import pandas as pd

from contract_review.chunking import make_chunks
from contract_review.data import mask_same_length
from contract_review.features import apply_bm25, build_classifier_features
from contract_review.model import apply_calibration
from contract_review.scoring import apply_standardisation


def score_contract(text, bundle):
    """Return passage locations and probabilities without fitting."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Contract text must be a non-empty string.")

    masked_text, masked_count = mask_same_length(text)
    contracts = pd.DataFrame({
        "contract_id": [0],
        "text": [masked_text],
    })
    chunks = make_chunks(contracts)
    chunks["text"] = [
        masked_text[start:end]
        for start, end in zip(chunks.start, chunks.end)
    ]

    counts = bundle["vectorizer"].transform(
        chunks.text
    )[:, bundle["selected_columns"]].tocsr()

    features, _ = build_classifier_features(
        counts,
        chunks,
        transformer=bundle["tfidf"],
    )

    classifier_scores = np.zeros(
        (len(chunks), len(bundle["categories"])),
        dtype=np.float32,
    )
    for j, category in enumerate(bundle["categories"]):
        model = bundle["classifiers"].get(category)
        if model is not None:
            classifier_scores[:, j] = model.decision_function(features)

    weighted = apply_bm25(counts, bundle["bm25"])
    knowledge_scores = np.asarray(
        (weighted @ bundle["knowledge_query_vectors"].T).todense()
    )

    combined = (
        apply_standardisation(
            classifier_scores, bundle["scaling"]["classifier"]
        )
        + bundle["knowledge_weight"] * apply_standardisation(
            knowledge_scores, bundle["scaling"]["knowledge"]
        )
    )
    probabilities = apply_calibration(
        combined, bundle["calibration"]
    )

    return {
        "masked_text": masked_text,
        "masked_matches": masked_count,
        "chunks": chunks,
        "probabilities": probabilities,
    }
