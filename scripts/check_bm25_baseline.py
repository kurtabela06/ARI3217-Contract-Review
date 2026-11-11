"""Compare extracted BM25 evaluation with recorded notebook results."""

from pathlib import Path

import numpy as np
import pandas as pd

from contract_review.chunking import make_chunks
from contract_review.data import load_cuad
from contract_review.evaluation import eval_scores
from contract_review.features import (
    bm25_matrix,
    build_counts,
    details,
    query_matrix,
)
from contract_review.labelling import label_chunks
from contract_review.metadata import contract_type
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
    train = (chunks["split"] == "train").to_numpy()
    test = (chunks["split"] == "test").to_numpy()

    counts, vocabulary, vectorizer = build_counts(chunks, train)
    weighted = bm25_matrix(counts, train)

    queries = [
        f"{category} {details(question)}"
        for category, question in zip(
            questions.category, questions.question
        )
    ]
    query_vectors = query_matrix(
        queries, vectorizer, vocabulary
    )
    scores = np.asarray(
        (weighted @ query_vectors.T).todense()
    )

    actual = eval_scores(
        scores, test, chunks, labels, categories
    )

    recorded = pd.read_csv(
        evidence / "baseline-category-evaluation.csv"
    )
    expected = (
        recorded.loc[
            (recorded["method"] == "BM25, dataset question")
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

    actual.to_csv(evidence / "packaged-bm25-category-results.csv")

    print("Holdout fingerprint matches.")
    print("All category evaluation results match the baseline.")
    print(actual[["AUPR", "P@3", "R@3"]].mean().round(3))
    print("Aggregate evaluation evidence saved.")


if __name__ == "__main__":
    main()
