"""Verify the extracted classifier against recorded notebook results."""

import json
from pathlib import Path
from time import perf_counter

import pandas as pd

from contract_review.chunking import make_chunks
from contract_review.data import load_cuad
from contract_review.evaluation import eval_scores
from contract_review.features import (
    build_classifier_features,
    build_counts,
)
from contract_review.labelling import label_chunks
from contract_review.metadata import contract_type
from contract_review.model import fit_linear
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
    test = (chunks["split"] == "test").to_numpy()

    counts, vocabulary, vectorizer = build_counts(chunks, training)
    features, transformer = build_classifier_features(
        counts, chunks, training
    )

    started = perf_counter()
    scores, fitted_rows, models = fit_linear(
        features, training, labels, categories
    )
    fitting_seconds = perf_counter() - started

    actual = eval_scores(
        scores, test, chunks, labels, categories
    )

    recorded = pd.read_csv(
        evidence / "baseline-category-evaluation.csv"
    )
    expected = (
        recorded.loc[
            (recorded["method"] == "TF-IDF + linear SVM")
            & (recorded["split"] == "test")
        ]
        .drop(columns=["method", "split"])
        .set_index("category")
    )

    pd.testing.assert_frame_equal(
        actual.sort_index(),
        expected.sort_index(),
        check_dtype=False,
        check_exact=False,
        rtol=1e-9,
        atol=1e-12,
    )

    actual.to_csv(
        evidence / "packaged-classifier-category-results.csv"
    )

    measurements = {
        "classifier_fitting_seconds": fitting_seconds,
        "fitted_training_passages": fitted_rows,
        "feature_columns": features.shape[1],
        "fitted_classifiers": len(models),
        "holdout_sha256": fingerprint,
    }
    (evidence / "packaged-classifier-measurements.json").write_text(
        json.dumps(measurements, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Holdout fingerprint matches.")
    print("All category evaluation results match the baseline.")
    print("Feature columns:", features.shape[1])
    print("Fitted training passages:", fitted_rows)
    print("Fitted classifiers:", len(models))
    print(f"Classifier fitting time: {fitting_seconds:.2f} seconds")
    print(actual[["AUPR", "P@3", "R@3"]].mean().round(3))
    print("Aggregate results and measurements saved.")


if __name__ == "__main__":
    main()
