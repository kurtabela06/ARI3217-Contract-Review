import numpy as np

from contract_review.metadata import contract_type, filing_year


def test_contract_type_recognises_franchise_and_preserves_unknown():
    assert contract_type("Example - Franchise Agreement") == "Franchise"
    assert contract_type("Unclassified document") == "Other"


def test_filing_year_extracts_date_and_preserves_missing():
    assert filing_year("Example_01_31_2010") == 2010
    assert np.isnan(filing_year("Example without a date"))
