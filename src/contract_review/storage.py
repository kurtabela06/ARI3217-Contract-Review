"""Persist review results without storing contract or passage text."""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def save_review(result):
    """Commit one review record before the API returns success."""
    path = Path(os.environ.get(
        "REVIEW_DB_PATH", "var/reviews.sqlite3"
    ))
    path.parent.mkdir(parents=True, exist_ok=True)

    stored_result = {
        **result,
        "highlights": [
            {
                key: value
                for key, value in highlight.items()
                if key != "text"
            }
            for highlight in result["highlights"]
        ],
    }

    with sqlite3.connect(path, timeout=5) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                request_id TEXT PRIMARY KEY,
                created_at_utc TEXT NOT NULL,
                model_version TEXT NOT NULL,
                result_json TEXT NOT NULL
            )
        """)
        connection.execute(
            """
            INSERT INTO reviews (
                request_id, created_at_utc, model_version, result_json
            ) VALUES (?, ?, ?, ?)
            """,
            (
                result["request_id"],
                datetime.now(timezone.utc).isoformat(),
                result["model_version"],
                json.dumps(stored_result, allow_nan=False),
            ),
        )
