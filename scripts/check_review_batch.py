"""Compare immediate and on-demand batch publication using the same review API."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def command(*args):
    return subprocess.check_output(args, text=True).strip()


def select_workload(dataset):
    raw = dataset.read_bytes()
    contracts = [
        (index, entry["paragraphs"][0]["context"])
        for index, entry in enumerate(json.loads(raw)["data"])
    ]
    if len(contracts) < 40 or any(not text.strip() for _, text in contracts):
        raise ValueError("Expected at least 40 non-blank CUAD contracts.")
    ordered = sorted(contracts, key=lambda item: len(item[1]))
    ranks = np.linspace(0, len(ordered) - 1, 40, dtype=int)
    selected = [ordered[index] for index in ranks]
    order = np.random.default_rng(42).permutation(40)
    shuffled = [selected[index] for index in order]
    middle = len(ordered) // 2
    return hashlib.sha256(raw).hexdigest(), shuffled, ordered[middle:middle + 3]


def wait_for_health(base):
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            with urlopen(f"{base}/health", timeout=3) as response:
                health = json.load(response)
            if health.get("status") == "ok" and health.get("model_version"):
                return health["model_version"]
        except (OSError, ValueError):
            pass
        time.sleep(1)
    raise RuntimeError("The isolated API did not become healthy within 60 seconds.")


def review(base, model_version, item):
    source_index, text = item
    request = Request(
        f"{base}/review",
        data=json.dumps({"text": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    start = time.perf_counter()
    status = 0
    try:
        with urlopen(request, timeout=120) as response:
            status = response.status
            result = json.load(response)
        if (
            status == 200
            and isinstance(result, dict)
            and result.get("model_version") == model_version
            and bool(result.get("request_id"))
            and isinstance(result.get("highlights"), list)
        ):
            return source_index, time.perf_counter() - start, result, None
        failure = "UnexpectedResponse"
    except HTTPError as error:
        status = error.code
        failure = "HTTPError"
        error.close()
    except (URLError, OSError, ValueError) as error:
        failure = type(error).__name__
    return source_index, time.perf_counter() - start, None, {
        "status": status,
        "error": failure,
    }


def run_phase(name, workload, request_review, output):
    """Deliver online responses individually or publish one complete batch file."""
    print(f"{name}: starting {len(workload)} reviews with two workers", flush=True)
    latencies = []
    failures = {}
    started_at = utc_now()
    started = time.perf_counter()
    ready_at = None
    with ThreadPoolExecutor(max_workers=2) as pool:
        # Executor.map uses the same input order and worker count as the online benchmark.
        for number, (source_index, elapsed, pack, error) in enumerate(
            pool.map(request_review, workload), start=1
        ):
            if error:
                label = f"{error['error']}:{error['status']}"
                failures[label] = failures.get(label, 0) + 1
            else:
                latencies.append(elapsed)
            if output is not None:
                output.write(json.dumps({
                    "job_item": number, "source_index": source_index,
                    "review_pack": pack, "failure": error,
                }) + "\n")
            if number % 250 == 0:
                print(f"{name}: {number}/{len(workload)} processed", flush=True)
    if output is not None:
        output.flush()
        os.fsync(output.fileno())
        temporary_path = Path(output.name)
        os.replace(temporary_path, temporary_path.with_name("batch-review-packs.jsonl"))
        ready_at = utc_now()
    seconds = time.perf_counter() - started
    return {
        "started_at_utc": started_at,
        "finished_at_utc": ready_at or utc_now(),
        "requests": len(workload),
        "successful_reviews": len(latencies),
        "failed_reviews": len(workload) - len(latencies),
        "failure_counts": failures,
        "successful_api_latency_p95_seconds": (
            float(np.percentile(latencies, 95)) if latencies else None
        ),
        "elapsed_seconds": seconds,
        "successful_reviews_per_second": len(latencies) / seconds,
        "timing_scope": (
            "Job start through publishing all outcomes in one local JSONL file."
            if output is not None
            else "Online phase start through last response received and parsed."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset")
    parser.add_argument("--image", default="contract-review:0.5")
    parser.add_argument("--repeats", type=int, default=50)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    dest = args.output_dir.resolve()
    dest.mkdir(mode=0o700, parents=True, exist_ok=True)
    if any(dest.iterdir()) or dest.stat().st_mode & 0o077:
        parser.error("--output-dir must be empty and private (chmod 700).")

    locate_dataset = runpy.run_path("scripts/check_review_load.py")["locate_dataset"]
    dataset_hash, selected, warmups = select_workload(locate_dataset(args.dataset))
    reference = json.loads(Path("evidence/review-sustained-load-summary.json").read_text())
    if dataset_hash != reference["dataset_sha256"]:
        parser.error("CUAD SHA-256 differs from the committed extended workload.")
    workload = selected * args.repeats
    commit = command("git", "rev-parse", "HEAD")
    dirty = bool(command("git", "status", "--porcelain"))
    cpus, memory_bytes = command("docker", "info", "--format", "{{.NCPU}} {{.MemTotal}}").split()
    container = command(
        "docker", "run", "--rm", "--detach", "--publish", "127.0.0.1::8888",
        "--env", "REVIEW_DB_PATH=/tmp/rd1-reviews.sqlite3", args.image,
    )
    try:
        image_id = command("docker", "inspect", "--format", "{{.Image}}", container)
        address = command("docker", "port", container, "8888/tcp")
        if not address.startswith("127.0.0.1:") or "\n" in address:
            raise RuntimeError(f"Unexpected API port mapping: {address}")
        base = f"http://{address}"
        version = wait_for_health(base)
        print(f"Isolated API ready: {version}", flush=True)

        def request_review(item):
            return review(base, version, item)

        for item in warmups:
            _, _, _, error = request_review(item)
            if error:
                raise RuntimeError(f"API warm-up failed: {error}")
        online = run_phase("online", workload, request_review, None)
        with (dest / "batch-review-packs.partial").open("x", encoding="utf-8") as output:
            batch = run_phase("batch", workload, request_review, output)
        failed = online["failed_reviews"] or batch["failed_reviews"]
        summary = {
            "status": "failures_recorded" if failed else "passed",
            "completed_at_utc": utc_now(),
            "model_version": version,
            "matches_previous_model": version == reference["model_version"],
            "image_reference": args.image,
            "image_id": image_id,
            "docker_cpus": int(cpus),
            "docker_memory_bytes": int(memory_bytes),
            "machine": platform.machine(),
            "client_python": platform.python_version(),
            "git_head": commit,
            "working_tree_dirty": dirty,
            "benchmark_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "dataset_sha256": dataset_hash,
            "selected_source_indexes": [index for index, _ in selected],
            "unique_contract_inputs": len(selected),
            "repetitions_per_input_per_phase": args.repeats,
            "workers_per_phase": 2,
            "warmup_requests_excluded": len(warmups),
            "live_review_volume_mounted": False,
            "scheduled_wait_seconds": None,
            "limitations": (
                "One on-demand run per mode, with the client and API sharing the VM. "
                "Batch uses the same HTTP service and includes publication of the local pack file. "
                "API startup and waiting for a daily schedule are outside the timing."
            ),
            "phases": {"online": online, "batch": batch},
        }
        rendered = json.dumps(summary, indent=2) + "\n"
        (dest / "review-batch-summary.json").write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        print(f"Share only: {dest / 'review-batch-summary.json'}", flush=True)
        return int(bool(failed))
    except (OSError, RuntimeError, subprocess.CalledProcessError):
        subprocess.run(["docker", "logs", "--tail", "30", container], check=False)
        raise
    finally:
        subprocess.run(["docker", "stop", container], stdout=subprocess.DEVNULL, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
