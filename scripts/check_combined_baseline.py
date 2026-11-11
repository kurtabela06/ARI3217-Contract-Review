"""Verify the classifier, knowledge blend and calibration together."""

from pathlib import Path

import numpy as np
import pandas as pd

from contract_review.chunking import make_chunks
from contract_review.data import load_cuad
from contract_review.evaluation import eval_scores
from contract_review.features import (
    bm25_matrix,
    build_classifier_features,
    build_counts,
    query_matrix,
)
from contract_review.knowledge import knowledge_queries
from contract_review.labelling import label_chunks
from contract_review.metadata import contract_type
from contract_review.model import (
    apply_calibration,
    calibrate,
    fit_linear,
)
from contract_review.scoring import select_knowledge_weight
from contract_review.splitting import (
    group_contract_families,
    split_contracts,
)


def main():
    root = Path(__file__).resolve().parents[1]
    evidence = root / "evidence"

    contracts, spans, questions = load_cuad(root / "data")
    categories = questions.category.tolist()
    contracts["ctype"] = contracts.title.map(contract_type)
    contracts, _, _ = group_contract_families(contracts)
    contracts, fingerprint = split_contracts(contracts, spans)

    expected_fingerprint = (
        evidence / "baseline-holdout-sha256.txt"
    ).read_text().strip()
    if fingerprint != expected_fingerprint:
        raise ValueError("Holdout fingerprint differs from baseline.")

    chunks = make_chunks(contracts)
    lookup = contracts.set_index("contract_id")
    chunks["split"] = chunks.contract_id.map(lookup["split"])
    chunks["text"] = [
        lookup.loc[cid, "text"][start:end]
        for cid, start, end in zip(
            chunks.contract_id, chunks.start, chunks.end
        )
    ]

    labels, _ = label_chunks(chunks, spans, categories)
    training = (chunks["split"] == "train").to_numpy()
    validation = (chunks["split"] == "valid").to_numpy()
    test = (chunks["split"] == "test").to_numpy()

    counts, vocabulary, vectorizer = build_counts(chunks, training)
    features, _ = build_classifier_features(
        counts, chunks, training
    )
    classifier_scores, _, _ = fit_linear(
        features, training, labels, categories
    )

    weighted = bm25_matrix(counts, training)
    queries = query_matrix(
        knowledge_queries(questions), vectorizer, vocabulary
    )
    knowledge_scores = np.asarray(
        (weighted @ queries.T).todense()
    )

    combined, weight, _ = select_knowledge_weight(
        classifier_scores,
        knowledge_scores,
        training,
        validation,
        chunks,
        labels,
        categories,
    )

    evaluation = eval_scores(
        combined, test, chunks, labels, categories
    )
    macro_aupr = float(evaluation.AUPR.mean())

    if weight != 0.25:
        raise ValueError(f"Unexpected validation-selected weight: {weight}")
    if not np.isclose(macro_aupr, 0.499, rtol=0, atol=0.0005):
        raise ValueError(f"Combined AUPR differs: {macro_aupr}")

    probabilities, parameters = calibrate(
        combined, validation, labels
    )
    np.testing.assert_allclose(
        probabilities,
        apply_calibration(combined, parameters),
    )
    if not np.isfinite(probabilities).all():
        raise ValueError("Calibration produced non-finite values.")

    evaluation.to_csv(
        evidence / "packaged-combined-category-results.csv"
    )
    pd.DataFrame([{
        "selected_weight": weight,
        "test_macro_aupr": macro_aupr,
        "holdout_sha256": fingerprint,
    }]).to_csv(
        evidence / "packaged-combined-summary.csv",
        index=False,
    )

    print("Holdout fingerprint matches.")
    print("Validation-selected knowledge weight:", weight)
    print(f"Combined test macro AUPR: {macro_aupr:.6f}")
    print("Reapplying saved calibration reproduces probabilities.")
    print("All calibrated values are finite.")
    print("Aggregate comparison evidence saved.")


if __name__ == "__main__":
    main()
