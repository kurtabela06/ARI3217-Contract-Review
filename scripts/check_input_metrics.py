"""Verify valid inputs affect length metrics and blank inputs do not."""

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from prometheus_client.parser import text_string_to_metric_families

BASE = "http://127.0.0.1:8888"


def snapshot():
    with urllib.request.urlopen(BASE + "/metrics/", timeout=10) as response:
        text = response.read().decode()

    samples = {
        sample.name: sample.value
        for family in text_string_to_metric_families(text)
        for sample in family.samples
        if sample.name in {
            "contract_review_input_characters_count",
            "contract_review_input_characters_sum",
        }
    }
    return {
        "count": samples["contract_review_input_characters_count"],
        "sum": samples["contract_review_input_characters_sum"],
    }


def submit(text):
    request = urllib.request.Request(
        BASE + "/review",
        data=json.dumps({"text": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        with error:
            return error.code, json.load(error)


def main():
    before = snapshot()
    text = (
        "The company may terminate this agreement "
        "by providing thirty days of written notice."
    )

    status, result = submit(text)
    assert status == 200, (status, result)
    after_valid = snapshot()

    assert after_valid["count"] == before["count"] + 1
    assert after_valid["sum"] == before["sum"] + len(text)

    status, _ = submit("   ")
    assert status == 422, status
    after_invalid = snapshot()
    assert after_invalid == after_valid

    summary = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_version": result["model_version"],
        "before": before,
        "after_valid": after_valid,
        "after_invalid": after_invalid,
        "valid_input_characters": len(text),
        "valid_submission_recorded_once": True,
        "blank_submission_excluded": True,
        "scope": "Local HTTP verification using synthetic text.",
    }

    root = Path(__file__).resolve().parents[1]
    path = root / "evidence/input-metrics-check-summary.json"
    path.write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print("Input-feature monitoring checks passed.")


if __name__ == "__main__":
    main()
