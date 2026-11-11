"""Match passage locations with the supplied clause annotations."""

import numpy as np


def label_chunks(chunks, spans, categories):
    """Return passage labels and best single-passage coverage per span."""
    labels = np.zeros(
        (len(chunks), len(categories)),
        dtype=np.int8,
    )
    best_cover = np.zeros(len(spans))
    category_index = {
        category: j for j, category in enumerate(categories)
    }

    groups = {
        contract_id: (
            group.index.values,
            group.start.values,
            group.end.values,
        )
        for contract_id, group in chunks.groupby("contract_id")
    }

    for n, (contract_id, category, start, end) in enumerate(
        zip(
            spans.contract_id,
            spans.category,
            spans.start,
            spans.end,
        )
    ):
        indices, passage_starts, passage_ends = groups[contract_id]
        overlap = (
            np.minimum(passage_ends, end)
            - np.maximum(passage_starts, start)
        )

        best_cover[n] = max(overlap.max(), 0) / max(end - start, 1)

        labels[
            indices[overlap >= min(10, end - start)],
            category_index[category],
        ] = 1

    return labels, best_cover
