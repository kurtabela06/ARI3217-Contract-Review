"""Measure documented quirks and inspect additional annotation issues."""

from pathlib import Path

import pandas as pd

from contract_review.chunking import make_chunks
from contract_review.data import load_cuad
from contract_review.labelling import label_chunks


def main():
    root = Path(__file__).resolve().parents[1]
    contracts, spans, questions = load_cuad(root / "data")
    categories = questions.category.tolist()

    category_counts = (
        spans.groupby("category").contract_id.nunique()
        .reindex(categories, fill_value=0)
    )
    present_pairs = spans[
        ["contract_id", "category"]
    ].drop_duplicates()
    total_pairs = len(contracts) * len(categories)
    absent_pairs = total_pairs - len(present_pairs)

    chunks = make_chunks(contracts)
    _, coverage = label_chunks(chunks, spans, categories)
    cut_spans = int((coverage < 0.9).sum())
    cut_share = cut_spans / len(spans)

    duplicate_rows = int(spans.duplicated(
        ["contract_id", "category", "start", "end"]
    ).sum())

    text_lengths = contracts.set_index("contract_id").text.str.len()
    invalid_offsets = (
        (spans.start < 0)
        | (spans.end <= spans.start)
        | (spans.end > spans.contract_id.map(text_lengths))
    )

    findings = pd.DataFrame([
        {
            "check": "Categories appearing in fewer than 30 contracts",
            "count": int((category_counts < 30).sum()),
            "denominator": len(categories),
        },
        {
            "check": "Contract-category pairs without annotations",
            "count": absent_pairs,
            "denominator": total_pairs,
        },
        {
            "check": "Annotated spans with less than 90% in one chunk",
            "count": cut_spans,
            "denominator": len(spans),
        },
        {
            "check": "Excess exact duplicate annotation rows",
            "count": duplicate_rows,
            "denominator": len(spans),
        },
        {
            "check": "Invalid annotation offsets",
            "count": int(invalid_offsets.sum()),
            "denominator": len(spans),
        },
    ])

    findings["share"] = findings["count"] / findings["denominator"]
    findings.to_csv(
        root / "evidence/data-quality-summary.csv",
        index=False,
    )
    print(findings.to_string(index=False))

    if cut_share > 0.07:
        raise ValueError(
            f"Clause-cut share {cut_share:.2%} exceeds the 7% limit."
        )
    if invalid_offsets.any():
        raise ValueError("Annotations contain invalid character offsets.")

    print("Clause-coverage and offset checks passed.")


if __name__ == "__main__":
    main()
