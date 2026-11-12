"""Checks that stop processing when data assumptions are violated."""

import numpy as np


def validate_clause_coverage(coverage, maximum_cut_share=0.07):
    """Reject excessive clause cutting under the notebook's 90% rule."""
    coverage = np.asarray(coverage)

    if coverage.size == 0:
        raise ValueError("Cannot validate coverage without annotated spans.")

    if (
        not np.isfinite(coverage).all()
        or (coverage < 0).any()
        or (coverage > 1).any()
    ):
        raise ValueError("Coverage values must be finite and between 0 and 1.")

    cut_share = float((coverage < 0.9).mean())

    if cut_share > maximum_cut_share:
        raise ValueError(
            f"Clause-cut share {cut_share:.2%} exceeds "
            f"the limit {maximum_cut_share:.2%}."
        )

    return cut_share
