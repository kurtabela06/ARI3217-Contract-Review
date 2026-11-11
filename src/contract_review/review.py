"""Review-pack selection and evaluation from the supplied notebook."""

import numpy as np
import pandas as pd


def review_pack(
    probabilities, chunks, contract_id, categories, red_flags, budget=20
):
    """Return selected passage indices and their category-index tags."""
    flag_indices = [categories.index(c) for c in red_flags]
    indices = chunks.index[
        chunks.contract_id == contract_id
    ].to_numpy()

    scores = probabilities[indices][:, flag_indices]
    chosen = {}

    for a, b in zip(
        *np.unravel_index(
            np.argsort(-scores, axis=None), scores.shape
        )
    ):
        if indices[a] not in chosen:
            if len(chosen) == budget:
                break
            chosen[indices[a]] = set()

        chosen[indices[a]].add(flag_indices[b])

    return chosen


def pack_eval(
    probabilities,
    contracts,
    chunks,
    labels,
    categories,
    red_flags,
    split,
    budgets=(5, 10, 15, 20, 25, 30, 40, 50, 60),
):
    """Measure red-flag category coverage for each contract and budget."""
    flag_indices = [categories.index(c) for c in red_flags]
    rows = []

    for contract_id in contracts.loc[
        contracts.split == split, "contract_id"
    ]:
        indices = chunks.index[
            chunks.contract_id == contract_id
        ].to_numpy()
        present = labels[indices][:, flag_indices].any(axis=0)

        for budget in budgets:
            pack = review_pack(
                probabilities, chunks, contract_id,
                categories, red_flags, budget,
            )
            found = np.zeros(len(flag_indices), dtype=bool)
            on_target = 0

            for i, tags in pack.items():
                hits = [
                    flag_indices.index(tag)
                    for tag in tags
                    if labels[i, tag]
                ]
                found[hits] = True
                on_target += bool(hits)

            rows.append({
                "contract_id": contract_id,
                "split": split,
                "budget": budget,
                "present": int(present.sum()),
                "found": int((found & present).sum()),
                "highlights": len(pack),
                "on target": on_target,
            })

    return pd.DataFrame(rows)
