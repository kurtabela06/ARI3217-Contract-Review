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
