# ADR 003 — SQLite review metadata on a persistent Docker volume

Status: implemented choice; rationale documented on 17 November 2026.

## Context

RD1 requires logging predictions with model versions and locating the database
in the architecture. The repository's reference workflow proposes PostgreSQL.
The implemented service instead uses SQLite; the general reflective-diary
instructions do not name a required database engine. This ADR records that
workflow deviation explicitly. A more specific VLE or lecturer requirement for
PostgreSQL would need to be satisfied or clarified separately.

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

Historical evidence:
- `evidence/storage-failure-summary.json`: invalid path produces HTTP 503.
- `evidence/storage-replacement-summary.json`: record count and fingerprint match
  before and after replacement.
- `evidence/storage-api-smoke-test-summary.json`: replacement serves reviews.

The source for these records is preserved in snapshot
`282cf23093d0d5cf9683987e991f2bfc2d6b7e34`. The extended image-0.5 benchmark is a
separate workload, with its own model version and deployment evidence.

`tests/test_storage.py` checks minimisation, UTC/model traceability, parent-path
failure and duplicate-ID protection without a model. `scripts/check_storage.py`
replays persistence/restart/replacement/failure scenarios on disposable Docker
resources. Its Docker recheck passed on Ubuntu on 17 November 2026, recorded in
`evidence/storage-recheck-summary.json`. Historical results remain separate.
