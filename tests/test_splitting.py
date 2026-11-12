import pandas as pd

from contract_review.splitting import group_contract_families


def test_duplicate_contracts_share_a_family_without_mutating_input():
    contracts = pd.DataFrame({
        "contract_id": [0, 1, 2],
        "text": [
            "alpha beta shared",
            "alpha beta shared",
            "gamma delta shared",
        ],
    })
    original = contracts.copy(deep=True)

    grouped, pairs, _ = group_contract_families(contracts)

    assert grouped.loc[0, "family"] == grouped.loc[1, "family"]
    assert grouped.loc[0, "family"] != grouped.loc[2, "family"]
    assert (0, 1) in pairs
    pd.testing.assert_frame_equal(contracts, original)


def example_split_data():
    """Small artificial records for testing partition behaviour."""
    contracts = pd.DataFrame({
        "contract_id": list(range(12)),
        "title": [f"Example contract {i}" for i in range(12)],
        "family": [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "ctype": ["Service"] * 11 + ["Franchise"],
    })
    spans = pd.DataFrame({
        "contract_id": list(range(12)),
        "category": ["Example"] * 12,
        "start": [0] * 12,
        "end": [10] * 12,
        "exact": [True] * 12,
    })
    return contracts, spans


def test_split_is_repeatable_preserves_families_and_holds_out_franchise():
    from contract_review.splitting import split_contracts

    contracts, spans = example_split_data()
    original = contracts.copy(deep=True)

    first, fingerprint_a = split_contracts(contracts, spans)
    second, fingerprint_b = split_contracts(contracts, spans)

    pd.testing.assert_frame_equal(first, second)
    pd.testing.assert_frame_equal(contracts, original)
    assert fingerprint_a == fingerprint_b
    assert first.groupby("family")["split"].nunique().max() == 1
    assert (
        first.loc[first.ctype == "Franchise", "split"]
        == "held-out type"
    ).all()
    assert (
        first.loc[first.ctype != "Franchise", "split"]
        != "held-out type"
    ).all()
    assert {"train", "valid", "test"} <= set(first["split"])


def test_holdout_fingerprint_detects_changed_test_annotation():
    from contract_review.splitting import split_contracts

    contracts, spans = example_split_data()
    result, original_fingerprint = split_contracts(contracts, spans)

    test_id = result.loc[
        result["split"] == "test", "contract_id"
    ].iloc[0]

    changed_spans = spans.copy(deep=True)
    changed_spans.loc[
        changed_spans.contract_id == test_id, "end"
    ] += 1

    _, changed_fingerprint = split_contracts(contracts, changed_spans)

    assert changed_fingerprint != original_fingerprint


def temporal_example_data():
    import numpy as np

    contracts = pd.DataFrame({
        "contract_id": list(range(8)),
        "title": [f"Example {i}" for i in range(8)],
        "family": [0, 0, 1, 2, 3, 3, 4, 5],
        "ctype": ["Service"] * 7 + ["Franchise"],
        "year": [2005, 2006, 2012, 2018, 2009, 2011, np.nan, 2019],
    })
    spans = pd.DataFrame({
        "contract_id": list(range(8)),
        "category": ["Example"] * 8,
        "start": [0] * 8,
        "end": [10] * 8,
        "exact": [True] * 8,
    })
    return contracts, spans


def test_temporal_split_preserves_chronology_and_excludes_families():
    from contract_review.splitting import split_contracts_temporally

    contracts, spans = temporal_example_data()
    original = contracts.copy(deep=True)

    result, fingerprint = split_contracts_temporally(contracts, spans)
    repeated, repeated_fingerprint = split_contracts_temporally(
        contracts, spans
    )

    assert result["split"].tolist() == [
        "train", "train", "valid", "test",
        "excluded_crossing_boundary", "excluded_crossing_boundary",
        "excluded_missing_year", "excluded_franchise_family",
    ]
    assert result.groupby("family")["split"].nunique().max() == 1
    assert fingerprint == repeated_fingerprint
    pd.testing.assert_frame_equal(result, repeated)
    pd.testing.assert_frame_equal(contracts, original)


def test_missing_year_excludes_the_whole_family():
    from contract_review.splitting import split_contracts_temporally

    contracts, spans = temporal_example_data()
    contracts.loc[0, "year"] = float("nan")

    result, _ = split_contracts_temporally(contracts, spans)

    assert (
        result.loc[result.family == 0, "split"]
        == "excluded_missing_year"
    ).all()
