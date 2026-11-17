"""Measure local review latency on complete CUAD contracts."""

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

BASE = "http://127.0.0.1:8888"


def locate_dataset(explicit):
    if explicit:
        return Path(explicit)

    candidates = set()
    for root in [Path("data"), Path.home() / ".cache/kagglehub"]:
        if root.exists():
            candidates.update(
                path.resolve()
                for path in root.rglob("CUAD_v1.json")
            )

    if not candidates:
        raise RuntimeError(
            "CUAD_v1.json not found. Supply --dataset /path/to/CUAD_v1.json"
        )

    hashes = {
        hashlib.sha256(path.read_bytes()).hexdigest()
        for path in candidates
    }
    if len(hashes) != 1:
        raise RuntimeError(
            "Different CUAD files found. Select one with --dataset."
        )
    return sorted(candidates)[0]


def review(item, expected_version):
    index, text = item
    request = urllib.request.Request(
        BASE + "/review",
        data=json.dumps({"text": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    started = time.perf_counter()
    status = 0
    ok = False
    request_id = ""
    error_type = ""

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            status = response.status
            result = json.load(response)

        request_id = result.get("request_id", "")
        ok = (
            status == 200
            and result.get("model_version") == expected_version
            and bool(request_id)
            and isinstance(result.get("highlights"), list)
        )
        if not ok:
            error_type = "UnexpectedResponse"
    except urllib.error.HTTPError as error:
        status = error.code
        error_type = "HTTPError"
        error.close()
    except Exception as error:
        error_type = type(error).__name__

    elapsed = time.perf_counter() - started
    return {
        "source_index": index,
        "input_characters": len(text),
        "status": status,
        "ok": ok,
        "seconds": elapsed,
        "request_id": request_id,
        "error_type": error_type,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset")
    args = parser.parse_args()

    dataset = locate_dataset(args.dataset)
    raw_bytes = dataset.read_bytes()
    raw = json.loads(raw_bytes)

    contracts = [
        (index, entry["paragraphs"][0]["context"])
        for index, entry in enumerate(raw["data"])
    ]
    assert len(contracts) >= 40
    assert all(isinstance(text, str) and text.strip()
               for _, text in contracts)

    ordered = sorted(contracts, key=lambda item: len(item[1]))
    positions = np.linspace(
        0, len(ordered) - 1, 40, dtype=int
    )
    selected = [ordered[int(position)] for position in positions]

    # Same deterministic shuffled order in both phases.
    rng = np.random.default_rng(42)
    selected = [selected[int(i)] for i in rng.permutation(40)]

    with urllib.request.urlopen(
        BASE + "/health", timeout=10
    ) as response:
        health = json.load(response)
    assert health["status"] == "ok"
    version = health["model_version"]

    # Warm-up is excluded from the reported measurements.
    middle = len(ordered) // 2
    for item in ordered[middle:middle + 3]:
        result = review(item, version)
        assert result["ok"], result
    print("Three warm-up requests passed.", flush=True)

    evidence = Path("evidence")
    evidence.mkdir(exist_ok=True)
    summaries = {}

    for name, workers in [("sequential", 1), ("burst", 2)]:
        print(f"Starting {name}: concurrency={workers}", flush=True)
        started = time.perf_counter()

        with ThreadPoolExecutor(max_workers=workers) as executor:
            rows = list(executor.map(
                lambda item: review(item, version), selected
            ))

        wall_seconds = time.perf_counter() - started
        successful = [row["seconds"] for row in rows if row["ok"]]

        with (evidence / f"load-{name}-requests.csv").open(
            "w", newline="", encoding="utf-8"
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "requests": len(rows),
            "concurrency": workers,
            "successful_requests": len(successful),
            "failed_requests": len(rows) - len(successful),
            "wall_seconds": wall_seconds,
            "successful_requests_per_second": (
                len(successful) / wall_seconds
            ),
            "successful_latency_seconds": (
                {
                    "p50": float(np.percentile(successful, 50)),
                    "p95": float(np.percentile(successful, 95)),
                    "maximum": float(max(successful)),
                }
                if successful else None
            ),
        }
        summaries[name] = summary
        print(json.dumps(summary, indent=2), flush=True)

    lengths = [len(text) for _, text in selected]
    summary = {
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_version": version,
        "dataset_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "dataset_contracts": len(contracts),
        "selection": (
            "40 evenly spaced ranks by complete-contract character "
            "length, including shortest and longest; shuffled with seed 42."
        ),
        "selected_input_characters": {
            "minimum": min(lengths),
            "median": float(np.median(lengths)),
            "p95": float(np.percentile(lengths, 95)),
            "maximum": max(lengths),
        },
        "warmup_requests_excluded": 3,
        "client_python": platform.python_version(),
        "git_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "working_tree_dirty": bool(subprocess.check_output(
            ["git", "status", "--porcelain"], text=True
        ).strip()),
        "timing_scope": (
            "Client elapsed time from opening the HTTP request through "
            "receiving and parsing its response, including database saving."
        ),
        "limitations": (
            "Local VM capacity test with 40 inputs per phase. "
            "Not a production arrival-rate simulation or accuracy evaluation. "
            "Successful-request latency excludes failed requests; failures "
            "are reported separately. Client and services share the VM."
        ),
        "phases": summaries,
    }

    (evidence / "review-load-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Load-test evidence saved.", flush=True)

    assert all(
        phase["failed_requests"] == 0
        for phase in summaries.values()
    ), "Some requests failed. Inspect the CSVs; do not discard the failures."


if __name__ == "__main__":
    main()
