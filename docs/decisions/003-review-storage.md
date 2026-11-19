# ADR 003 — SQLite review metadata on a persistent Docker volume

Status: implemented choice; rationale documented on 17 November 2026.

## Context

The RD1 diary guidelines require prediction logging with model versions and an
architecture that identifies the database. Stage 10 of the
[archived workflow](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/7bcddbdf02cf0c5497c619929cbeed0d2dd5675d/ARI3217%20-%20Reflective%20Diary%20Entry%201%20Workflow.pdf)
specifies PostgreSQL. SQLite is the documented implementation choice for the
single-VM prototype.

## Decision and rationale

Use SQLite for the current single-VM, single-API-process demonstration, with
`REVIEW_DB_PATH=/app/var/reviews.sqlite3` on `contract-review-records`.
This keeps deployment small while permitting direct evidence that successful
review records survive process restart and container replacement.

Commit one record before HTTP 200 returns. Store request ID, UTC timestamp,
bundle-derived model version, passage locations, citations and category scores.
Omit submitted contract text and returned passage text. Invalid requests are
not logged as successful reviews. A database write failure returns HTTP 503.
The API's liveness check is separate from database-write readiness.

## Alternatives and limits

PostgreSQL offers a separately managed database service and is a candidate for
shared access, more concurrent writers, or stronger operational requirements.
Adopting it requires connection configuration, schema/migration and backup
arrangements, and fresh persistence/failure evidence. It remains an alternative;
no PostgreSQL deployment or comparative database benchmark is claimed.

The current SQLite connection timeout is five seconds. It is not configured
with a WAL policy or a backup/retention scheduler. The recorded two-concurrent-
request workload is evidence for those conditions, not proof of arbitrary
concurrent-write capacity. A future multi-instance deployment must revisit the
storage choice and locking behaviour.

Stored metadata can still be sensitive. The operator must define retention,
access and backups before operational use. Records currently persist until
manually deleted; deleting the named volume deletes its history.

## Evidence and verification

The [storage unit tests](../../tests/test_storage.py) check minimisation,
UTC and model traceability, parent-path failure and duplicate-ID protection.
The [Docker recheck](../../scripts/check_storage.py) exercises restart,
replacement, another write after replacement and HTTP 503 on failed storage.
It uses disposable containers and a disposable volume.

- [Image-0.5 recheck at `22152bf`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/22152bfae9ee2537a2c6c967f3b9e8347f861451/evidence/storage-recheck-summary.json), run on 17 November 2026.
- [Earlier replacement evidence at `50d3227`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/50d3227377e08608b4ebf0b9981f47cd9cc4d4f1/evidence/storage-replacement-summary.json) and [earlier write failure](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/50d3227377e08608b4ebf0b9981f47cd9cc4d4f1/evidence/storage-failure-summary.json).
