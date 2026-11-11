"""Evaluation measures from the supplied notebook."""

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score


def eval_scores(scores, mask, chunks, labels, categories, k=3):
    """Evaluate each category using the supplied passage-level protocol."""
    rows = []
    contract_ids = chunks.contract_id.values[mask]

    for j, category in enumerate(categories):
        y = labels[mask, j]
        s = scores[mask, j]

        ranked = pd.DataFrame({
            "cid": contract_ids,
            "s": s,
            "y": y,
        }).sort_values(
            ["cid", "s"],
            ascending=[True, False],
        )

        top = (
            ranked.groupby("cid")
            .head(k)
            .groupby("cid")
            .y.agg(["sum", "size"])
        )
        present = ranked.groupby("cid").y.max()

        rows.append({
            "category": category,
            "contracts with clause": int(present.sum()),
            "AUPR": (
                average_precision_score(y, s)
                if y.sum() else np.nan
            ),
            f"P@{k}": top["sum"].sum() / top["size"].sum(),
            f"R@{k}": (
                (top["sum"] > 0)[present > 0].mean()
                if present.sum() else np.nan
            ),
        })

    return pd.DataFrame(rows).set_index("category")
