import numpy as np
import pandas as pd

from contract_review.labelling import label_chunks


def test_ten_character_overlap_labels_but_reports_partial_coverage():
    chunks = pd.DataFrame({
        "contract_id": [0, 0],
        "start": [0, 20],
        "end": [20, 40],
    })
    spans = pd.DataFrame({
        "contract_id": [0],
        "category": ["Example"],
        "start": [10],
        "end": [30],
    })

    labels, coverage = label_chunks(chunks, spans, ["Example"])

    np.testing.assert_array_equal(labels, [[1], [1]])
    np.testing.assert_allclose(coverage, [0.5])


def test_short_annotation_requires_full_overlap():
    chunks = pd.DataFrame({
        "contract_id": [0, 0],
        "start": [0, 5],
        "end": [5, 10],
    })
    spans = pd.DataFrame({
        "contract_id": [0, 0],
        "category": ["Complete", "Crossing"],
        "start": [1, 4],
        "end": [4, 7],
    })

    labels, coverage = label_chunks(
        chunks, spans, ["Complete", "Crossing"]
    )

    np.testing.assert_array_equal(labels, [[1, 0], [0, 0]])
    np.testing.assert_allclose(coverage, [1.0, 2.0 / 3.0])
