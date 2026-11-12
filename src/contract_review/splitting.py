"""Contract-family grouping and evaluation partitioning."""

import networkx as nx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def group_contract_families(contracts, duplicate_cosine=0.80):
    """Return contracts with family IDs, duplicate pairs and text vectors."""
    result = contracts.copy()

    vectors = TfidfVectorizer(
        min_df=2,
        max_features=100_000,
        sublinear_tf=True,
        dtype=np.float32,
    ).fit_transform(result.text)

    similarity = (vectors @ vectors.T).tocoo()
    pairs = [
        (i, j)
        for i, j, value in zip(
            similarity.row,
            similarity.col,
            similarity.data,
        )
        if i < j and value >= duplicate_cosine
    ]

    graph = nx.Graph()
    graph.add_nodes_from(result.contract_id)
    graph.add_edges_from(pairs)

    family = {
        node: family_id
        for family_id, component in enumerate(
            nx.connected_components(graph)
        )
        for node in component
    }
    result["family"] = result.contract_id.map(family)

    return result, pairs, vectors


def split_contracts(
    contracts,
    spans,
    seed=3217,
    split=(0.6, 0.2, 0.2),
    held_out_type="Franchise",
):
    """Apply the supplied family split and return its holdout fingerprint."""
    import hashlib

    import pandas as pd

    result = contracts.copy()
    held = result.ctype == held_out_type

    families = result.loc[~held, "family"].unique()
    rng = np.random.default_rng(seed)
    rng.shuffle(families)

    family_sizes = (
        result.loc[~held]
        .groupby("family")
        .size()
        .reindex(families)
    )
    cumulative = family_sizes.cumsum() / family_sizes.sum()

    split_of_family = pd.Series(
        np.where(
            cumulative <= split[0],
            "train",
            np.where(
                cumulative <= split[0] + split[1],
                "valid",
                "test",
            ),
        ),
        index=families,
    )

    result["split"] = np.where(
        held,
        "held-out type",
        result.family.map(split_of_family),
    )

    test_ids = result.loc[result.split == "test", "contract_id"]
    fingerprint_spans = (
        spans[spans.contract_id.isin(test_ids)]
        .sort_values(["contract_id", "category", "start"])
    )
    fingerprint = hashlib.sha256(
        (
            ",".join(result.loc[test_ids.index, "title"])
            + fingerprint_spans.to_csv(index=False)
        ).encode()
    ).hexdigest()

    return result, fingerprint


def split_contracts_temporally(
    contracts,
    spans,
    validation_start=2010,
    test_start=2015,
    held_out_type="Franchise",
):
    """Assign complete families to chronological periods or exclusions."""
    import hashlib

    if validation_start >= test_start:
        raise ValueError("Validation must begin before the test period.")

    result = contracts.copy()
    families = result.groupby("family").agg(
        first_year=("year", "min"),
        last_year=("year", "max"),
        missing_year=("year", lambda s: s.isna().any()),
        held_out_type=("ctype", lambda s: (s == held_out_type).any()),
    )

    def assign(row):
        if row["held_out_type"]:
            return "excluded_franchise_family"
        if row["missing_year"]:
            return "excluded_missing_year"
        if row["last_year"] < validation_start:
            return "train"
        if (
            row["first_year"] >= validation_start
            and row["last_year"] < test_start
        ):
            return "valid"
        if row["first_year"] >= test_start:
            return "test"
        return "excluded_crossing_boundary"

    assignments = families.apply(assign, axis=1)
    result["split"] = result.family.map(assignments)

    test_rows = result.loc[result.split == "test"]
    test_spans = spans[
        spans.contract_id.isin(test_rows.contract_id)
    ].sort_values(["contract_id", "category", "start"])

    fingerprint = hashlib.sha256(
        (
            ",".join(test_rows.title)
            + test_spans.to_csv(index=False)
        ).encode()
    ).hexdigest()

    return result, fingerprint
