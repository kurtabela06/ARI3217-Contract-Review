"""Recheck storage in temporary Docker containers and a disposable volume.

Uses the existing fitted image; never trains or mounts the live review volume.
"""

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

READY = '''
import json, time, urllib.error, urllib.request
for attempt in range(120):
    try:
        with urllib.request.urlopen("http://127.0.0.1:8888/health", timeout=2) as response:
            result = json.load(response)
        assert result["status"] == "ok"
        print(json.dumps(result))
        break
    except (urllib.error.URLError, TimeoutError):
        time.sleep(0.5)
else:
    raise RuntimeError("API did not become ready")
'''

SUBMIT = '''
import json, urllib.error, urllib.request
text = "The company may terminate this agreement with thirty days of notice."
request = urllib.request.Request(
    "http://127.0.0.1:8888/review",
    data=json.dumps({"text": text}).encode(),
    headers={"Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(request, timeout=60) as response:
        status, result = response.status, json.load(response)
except urllib.error.HTTPError as error:
    with error:
        status, result = error.code, json.load(error)
assert status == expected_status, status
if status == 200:
    assert result["request_id"]
    print(json.dumps({"status": status, "request_id": result["request_id"],
                      "model_version": result["model_version"]}))
else:
    assert result == {"detail": "Review storage unavailable. Please retry later."}
    print(json.dumps({"status": status, "expected_error_verified": True}))
'''

SNAPSHOT = '''
import hashlib, json, sqlite3
with sqlite3.connect("file:/app/var/reviews.sqlite3?mode=ro", uri=True) as connection:
    rows = connection.execute(
        "SELECT request_id, created_at_utc, model_version, result_json "
        "FROM reviews ORDER BY request_id"
    ).fetchall()
assert rows, "No reviews were stored"
for request_id, created_at, version, payload in rows:
    result = json.loads(payload)
    assert result["request_id"] == request_id
    assert result["model_version"] == version
    assert "text" not in result
    assert all("text" not in item for item in result["highlights"])
print(json.dumps({
    "review_count": len(rows),
    "request_ids": [row[0] for row in rows],
    "records_sha256": hashlib.sha256(json.dumps(rows).encode()).hexdigest(),
    "passage_text_excluded": True,
}))
'''


def docker(*arguments, script=None, check=True):
    return subprocess.run(
        ["docker", *arguments], input=script, capture_output=True,
        text=True, check=check, timeout=90,
    )


def inside(name, script):
    return json.loads(docker("exec", "-i", name, "python", "-", script=script).stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default="contract-review:0.5")
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "evidence/storage-recheck-summary.json",
    )
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output exists; choose a new --output to preserve earlier evidence.")

    image = json.loads(docker("image", "inspect", args.image).stdout)[0]
    image_id = image["Id"]
    prefix = "contract-review-storage-check-" + uuid.uuid4().hex[:12]
    volume = prefix + "-records"
    first, replacement, failure = [prefix + suffix for suffix in ("-first", "-replacement", "-failure")]
    names = [first, replacement, failure]
    volume_created = False
    checks = {}
    error = None
    summary = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "image_reference": args.image,
        "image_id": image_id,
        "scope": "Synthetic checks in isolated temporary containers and a disposable volume.",
        "live_review_volume_mounted": False,
        "checks": checks,
    }

    def start(name, bad_path=False):
        arguments = ["run", "-d", "--network", "none", "--name", name,
                     "-e", "REVIEW_DB_PATH=" + (
                         "/dev/null/reviews.sqlite3" if bad_path
                         else "/app/var/reviews.sqlite3")]
        if not bad_path:
            arguments += ["-v", volume + ":/app/var"]
        docker(*arguments, image_id)
        return inside(name, READY)

    try:
        docker("volume", "create", volume)
        volume_created = True
        health = start(first)
        summary["model_version"] = health["model_version"]
        submitted = inside(first, "expected_status = 200\n" + SUBMIT)
        assert submitted["model_version"] == health["model_version"]
        before = inside(first, SNAPSHOT)
        assert before["review_count"] == 1
        assert submitted["request_id"] in before["request_ids"]
        checks["successful_review_persisted_without_text"] = True

        docker("restart", "--time", "30", first)
        assert inside(first, READY)["model_version"] == health["model_version"]
        assert inside(first, SNAPSHOT) == before
        checks["restart_preserves_all_records"] = True

        docker("stop", "--time", "30", first)
        docker("rm", first)
        assert start(replacement)["model_version"] == health["model_version"]
        assert inside(replacement, SNAPSHOT) == before
        checks["replacement_preserves_all_records"] = True
        inside(replacement, "expected_status = 200\n" + SUBMIT)
        after = inside(replacement, SNAPSHOT)
        assert after["review_count"] == 2
        checks["replacement_can_save_new_review"] = True
        summary["before_replacement"] = before
        summary["after_new_review"] = after

        assert start(failure, bad_path=True)["model_version"] == health["model_version"]
        inside(failure, "expected_status = 503\n" + SUBMIT)
        checks["unwritable_storage_returns_503"] = True
    except Exception as exc:
        error = exc
        summary["error_type"] = type(exc).__name__
        summary["error"] = str(exc)
        if isinstance(exc, subprocess.CalledProcessError):
            summary["command_stderr"] = exc.stderr
    finally:
        cleanup_failures = []
        for name in names:
            if docker("inspect", name, check=False).returncode == 0:
                if docker("rm", "-f", name, check=False).returncode != 0:
                    cleanup_failures.append(name)
        if volume_created:
            if docker("volume", "rm", volume, check=False).returncode != 0:
                cleanup_failures.append(volume)
        summary["cleanup_complete"] = not cleanup_failures
        summary["cleanup_failures"] = cleanup_failures
        summary["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        summary["status"] = "passed" if error is None and not cleanup_failures else "failed"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2))

    if summary["status"] != "passed":
        sys.exit(1)
    print("Storage rechecks passed; temporary resources removed.")


if __name__ == "__main__":
    main()
