import numpy as np
import pytest

from contract_review.validation import validate_clause_coverage


def test_ninety_percent_coverage_is_accepted():
    assert validate_clause_coverage([1.0, 0.9, 0.95]) == 0.0


def test_excessive_clause_cutting_fails_loudly():
    with pytest.raises(ValueError, match="Clause-cut share"):
        validate_clause_coverage([1.0, 0.89])


@pytest.mark.parametrize("coverage", [[], [np.nan], [-0.1], [1.1]])
def test_invalid_or_missing_coverage_is_rejected(coverage):
    with pytest.raises(ValueError):
        validate_clause_coverage(coverage)
