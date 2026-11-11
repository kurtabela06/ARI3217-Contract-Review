from contract_review.data import mask_same_length


def test_mask_preserves_length_and_clause_location():
    text = (
        "Contact counsel@example.com or 212-555-0199. "
        "Liability shall not exceed the agreed amount."
    )
    clause = "Liability shall not exceed the agreed amount."
    start = text.index(clause)
    end = start + len(clause)

    masked, count = mask_same_length(text)

    assert count == 2
    assert len(masked) == len(text)
    assert "counsel@example.com" not in masked
    assert "212-555-0199" not in masked
    assert masked[start:end] == clause


def test_text_without_contacts_is_unchanged():
    text = "This agreement may be terminated with notice."

    masked, count = mask_same_length(text)

    assert masked == text
    assert count == 0
