"""Exercise minimisation and transaction behaviour without a running model."""

import copy
import json
import sqlite3
from datetime import datetime, timedelta

import pytest

from contract_review.storage import save_review


def example_review():
    return {
        "request_id": "synthetic-request",
        "model_version": "test:synthetic-bundle",
        "highlights": [{
            "start": 0,
            "end": 26,
            "text": "Synthetic private passage.",
            "citation": "[synthetic-request:0-26]",
            "categories": [{"category": "Example", "probability": 0.8}],
        }],
    }


def test_stored_review_minimises_text_and_preserves_traceability(tmp_path, monkeypatch):
    database = tmp_path / "records" / "reviews.sqlite3"
    monkeypatch.setenv("REVIEW_DB_PATH", str(database))
    result = example_review()
    unchanged = copy.deepcopy(result)
    save_review(result)

    with sqlite3.connect(database) as connection:
        request_id, timestamp, version, payload = connection.execute(
            "SELECT request_id, created_at_utc, model_version, result_json FROM reviews"
        ).fetchone()

    stored = json.loads(payload)
    assert request_id == result["request_id"]
    assert version == result["model_version"]
    assert datetime.fromisoformat(timestamp).utcoffset() == timedelta(0)
    assert result["highlights"][0]["text"] not in payload
    assert "text" not in stored["highlights"][0]
    assert stored["highlights"][0]["citation"] == result["highlights"][0]["citation"]
    assert stored["highlights"][0]["categories"] == result["highlights"][0]["categories"]
    assert result == unchanged


def test_unwritable_parent_fails_instead_of_silently_losing_review(tmp_path, monkeypatch):
    parent = tmp_path / "a-file"
    parent.write_text("not a directory")
    monkeypatch.setenv("REVIEW_DB_PATH", str(parent / "reviews.sqlite3"))
    with pytest.raises(OSError):
        save_review(example_review())


def test_duplicate_request_does_not_overwrite_existing_record(tmp_path, monkeypatch):
    database = tmp_path / "reviews.sqlite3"
    monkeypatch.setenv("REVIEW_DB_PATH", str(database))
    save_review(example_review())
    changed = example_review()
    changed["model_version"] = "different-model"
    with pytest.raises(sqlite3.IntegrityError):
        save_review(changed)
    with sqlite3.connect(database) as connection:
        rows = connection.execute("SELECT request_id, model_version FROM reviews").fetchall()
    assert rows == [("synthetic-request", "test:synthetic-bundle")]
