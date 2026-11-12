"""Inspect chronological partitions without training a model."""

from pathlib import Path

import pandas as pd

from contract_review.data import load_cuad
from contract_review.metadata import contract_type, filing_year
from contract_review.splitting import group_contract_families


def main():
    root = Path(__file__).resolve().parents[1]
    evidence = root / "evidence"

    contracts, spans, questions = load_cuad(root / "data")
    contracts["ctype"] = contracts.title.map(contract_type)
    contracts["year"] = contracts.title.map(filing_year)
    contracts, _, _ = group_contract_families(contracts)

    families = contracts.groupby("family").agg(
        contracts=("contract_id", "size"),
        first_year=("year", "min"),
        last_year=("year", "max"),
        missing_year=("year", lambda s: s.isna().any()),
        has_franchise=("ctype", lambda s: (s == "Franchise").any()),
    )

    def assign(row):
        if row["has_franchise"]:
            return "excluded_franchise_family"
        if row["missing_year"]:
            return "excluded_missing_year"
        if row["last_year"] < 2010:
            return "train"
        if row["first_year"] >= 2010 and row["last_year"] < 2015:
            return "valid"
        if row["first_year"] >= 2015:
            return "test"
        return "excluded_crossing_boundary"

    families["temporal_split"] = families.apply(assign, axis=1)
    contracts["temporal_split"] = contracts.family.map(
        families.temporal_split
    )

    summary = contracts.groupby("temporal_split").agg(
        contracts=("contract_id", "size"),
        families=("family", "nunique"),
    )

    year_counts = (
        contracts.groupby("year", dropna=False)
        .size()
        .rename("contracts")
        .reset_index()
    )

    presence = (
        spans[["contract_id", "category"]].drop_duplicates()
        .merge(
            contracts[["contract_id", "temporal_split"]],
            on="contract_id",
            validate="many_to_one",
        )
    )
    support = (
        presence.groupby(["category", "temporal_split"])
        .size()
        .unstack(fill_value=0)
        .reindex(questions.category, fill_value=0)
        .reindex(columns=["train", "valid", "test"], fill_value=0)
    )

    summary.to_csv(evidence / "temporal-feasibility-summary.csv")
    year_counts.to_csv(evidence / "temporal-year-counts.csv", index=False)
    support.to_csv(evidence / "temporal-category-support.csv")

    print("Provisional partition counts:")
    print(summary.to_string())
    print("\nCategories with no positive training contracts:",
          int((support["train"] == 0).sum()))
    print("Categories with no positive validation contracts:",
          int((support["valid"] == 0).sum()))
    print("Categories with fewer than 5 positive test contracts:",
          int((support["test"] < 5).sum()))
    print("\nCounts saved; no model trained.")


if __name__ == "__main__":
    main()
