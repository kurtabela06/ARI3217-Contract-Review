import numpy as np
import pandas as pd
import pytest

from contract_review.evaluation import eval_scores


def test_precision_includes_contracts_without_the_category():
    chunks = pd.DataFrame({
        "contract_id": [0, 0, 1, 1],
    })
    labels = np.array([[1], [0], [0], [0]])
    scores = np.array([[0.9], [0.1], [0.8], [0.2]])
    mask = np.array([True, True, True, True])

    result = eval_scores(
        scores, mask, chunks, labels, ["Example"], k=1
    )
    row = result.loc["Example"]

    assert row["contracts with clause"] == 1
    assert row["AUPR"] == pytest.approx(1.0)
    assert row["P@1"] == pytest.approx(0.5)
    assert row["R@1"] == pytest.approx(1.0)
