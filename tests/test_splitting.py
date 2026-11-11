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
