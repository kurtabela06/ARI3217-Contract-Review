"""Check the running API using synthetic text and standard-library HTTP."""

import json
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://localhost:8888"


def call(path, payload=None):
    body = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        BASE + path,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        with error:
            return error.code, json.load(error)


def main():
    status, health = call("/health")
    assert status == 200
    assert health["status"] == "ok"

    text = (
        "Contact counsel@example.com. "
        "The company may terminate this agreement for any reason "
        "by providing thirty days of written notice. "
        "The consultant shall not assign this agreement without "
        "the company's prior written consent."
    )
    expected_masked = text.replace(
        "counsel@example.com.",
        "x" * len("counsel@example.com."),
    )

    status, result = call("/review", {"text": text})
    assert status == 200
    assert result["model_version"] == health["model_version"]

    highlights = result["highlights"]
    assert 0 < len(highlights) <= result["review_budget"]

    for highlight in highlights:
        start, end = highlight["start"], highlight["end"]
        assert 0 <= start < end <= len(text)
        assert highlight["text"] == expected_masked[start:end]
        assert highlight["citation"] == (
            f'[{result["request_id"]}:{start}-{end}]'
        )
        for category in highlight["categories"]:
            assert 0 <= category["probability"] <= 1

    assert "counsel@example.com" not in json.dumps(result)

    invalid_cases = [
        ("missing_text", {}),
        ("empty_text", {"text": ""}),
        ("whitespace_text", {"text": "   "}),
    ]
    invalid_results = {}

    for name, payload in invalid_cases:
        status, _ = call("/review", payload)
        assert status == 422, f"{name} returned {status}"
        invalid_results[name] = status

    summary = {
        "health_status": 200,
        "review_status": 200,
        "model_version": result["model_version"],
        "highlights_returned": len(highlights),
        "citation_locations_match": True,
        "email_masking_verified": True,
        "invalid_request_statuses": invalid_results,
        "scope": (
            "Synthetic HTTP smoke test; not a measure of extraction accuracy "
            "or real-workload performance."
        ),
    }

    root = Path(__file__).resolve().parents[1]
    (root / "evidence/api-smoke-test-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print("API checks passed.")


if __name__ == "__main__":
    main()
