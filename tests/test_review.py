import numpy as np
import pandas as pd

from contract_review.review import pack_eval, review_pack


def test_review_budget_counts_distinct_passages_not_tags():
    chunks = pd.DataFrame({"contract_id": [0, 0, 0]})
    probabilities = np.array([
        [0.90, 0.85],
        [0.80, 0.10],
        [0.70, 0.60],
    ])
    categories = ["Example A", "Example B"]

    pack = review_pack(
        probabilities, chunks, 0, categories, categories, budget=2
    )

    assert set(pack) == {0, 1}
    assert pack[0] == {0, 1}
    assert pack[1] == {0}


def test_pack_evaluation_records_a_present_but_missed_category():
    contracts = pd.DataFrame({
        "contract_id": [0],
        "split": ["test"],
    })
    chunks = pd.DataFrame({"contract_id": [0, 0]})
    labels = np.array([[0], [1]])
    probabilities = np.array([[0.9], [0.2]])

    result = pack_eval(
        probabilities, contracts, chunks, labels,
        ["Example"], ["Example"], "test", budgets=(1,),
    ).iloc[0]

    assert result["present"] == 1
    assert result["found"] == 0
    assert result["highlights"] == 1
    assert result["on target"] == 0
