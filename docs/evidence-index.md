# RD1 evidence index

Evidence snapshot: [`282cf23093d0d5cf9683987e991f2bfc2d6b7e34`](https://github.com/kurtabela06/ARI3217-Contract-Review/commit/282cf23093d0d5cf9683987e991f2bfc2d6b7e34),
17 November 2026. This commit contains the implementation and extended-workload
records. It is a stable snapshot reference, not a claim that every earlier
measurement was first made in that commit. Original `source_commit`, timestamp,
requirements hash and dirty-tree fields inside evidence remain as recorded.

## Main measurements

| Claim | Recorded measurement | Evidence in the snapshot |
|---|---|---|
| Given classifier baseline | Test macro AUPR 0.48908511 | [Headline metrics](../evidence/baseline-headline-metrics.csv), [run metadata](../evidence/baseline-run-metadata.json) |
| Full-data classifier plus supplied KB blend | Test macro AUPR 0.49900236; weight 0.25 | [Packaged summary](../evidence/packaged-combined-summary.csv) |
| Fresh-copy reproduction | Same macro AUPR, weight and primary holdout fingerprint; 27.22 s command scope | [Verification](../evidence/fresh-copy-verification.json), [training measurements](../evidence/fresh-copy-training-measurements.json) |
| Timing scopes | Packaged classifier fit 4.45 s; packaged training/evaluation/saving command 20.73 s | [Classifier fit](../evidence/packaged-classifier-measurements.json), [training command](../evidence/packaged-training-command.json) |
| Three supplied data issues | 5/41 rare categories; 14,208/20,910 no-answer pairs; 895/13,823 cut spans | [Counts](../evidence/data-quality-summary.csv), [findings and guards](data-findings.md) |
| Additional annotation checks | Zero exact duplicate rows and zero invalid offsets | [Counts](../evidence/data-quality-summary.csv) |
| Serving equivalence | 114 contracts: 99 regular test + 15 franchise; all selections match; maximum probability difference 0 | [Summary](../evidence/serving-equivalence-summary.json), [per-contract results](../evidence/serving-equivalence-results.csv) |
| Review quality at 20 passages | Regular-test recall 88.02%; held-out franchise recall 53.33% | [Operating point](../evidence/baseline-operating-point-results.csv), [packaged budget results](../evidence/packaged-review-budget-results.csv) |
| Supplementary filing-year evaluation | Test macro AUPR 0.48958940; recall 677/792 = 85.48% | [Summary](../evidence/temporal-evaluation-summary.json), [protocol](decisions/001-evaluation-protocol.md) |
| Historical SQLite persistence | Before/after replacement count 2; identical record fingerprint | [Replacement evidence](../evidence/storage-replacement-summary.json) |
| Historical storage failure | HTTP 503 for an invalid database path | [Failure evidence](../evidence/storage-failure-summary.json) |
| Current input-feature check | One valid 84-character submission adds one observation and 84 characters; a blank submission adds neither | [Metric check](../evidence/input-metrics-check-summary.json), [script](../scripts/check_input_metrics.py) |
| Python base pin | Python 3.14.10, Linux/arm64, digest recorded | [Base-image details](../evidence/python-base-image-summary.json), [Dockerfile](../Dockerfile) |
| Extended workload and image | Model `0.1.0:eef20dbe2aca`; API image `contract-review:0.5`, 328,175,166 bytes | [Workload](../evidence/review-sustained-load-summary.json), [deployment](../evidence/sustained-load-deployment-summary.json) |

The serving-equivalence artifact identifies the particular host bundle tested.
New image builds have separate bundle fingerprints. A different fingerprint is
not, by itself, evidence of changed predictions; do not relabel the earlier
bundle check as a new equivalence test of every rebuilt image.

## RD1 service-results reference table

| Measure | Value | Scope |
|---|---:|---|
| Combined baseline test macro AUPR | 0.49900236 | Primary grouped split |
| Fresh-copy test macro AUPR | 0.49900236 | New checkout/environment; shared download cache may be reused |
| Latest measured API image size | 312.97 MiB | 328,175,166 bytes, local uncompressed image size |
| Sequential client p95 | 96.10 ms | 2,000 successful requests, concurrency 1 |
| Concurrent client p95 | 142.92 ms | 2,000 successful requests, concurrency 2 |
| Sequential throughput | 26.42 reviews/s | 75.69-second phase |
| Concurrent throughput | 28.64 reviews/s | 69.83-second phase |
| Failed measured requests | 0/4,000 | Three warm-ups excluded |
| VM resources | 2 CPUs; about 5.26 GiB available to Docker | Client and three services share VM |

These values come from the files above and the two request-level CSVs:
[sequential](../evidence/sustained-load-sequential-requests.csv) and
[concurrent](../evidence/sustained-load-burst-requests.csv).
The 40 unique contracts are repeated 50 times per phase. This is a controlled
capacity run, not independent replicated trials, a production arrival-rate
simulation or a long-duration soak test. Client timing includes receiving and
parsing responses, inference and database saving; it excludes startup/training.

## Dashboard and historical checkpoints

Current measurement evidence:
- [Input-feature dashboard screenshot](../evidence/rd1-dashboard-input-feature.png).
- [Metrics snapshot](../evidence/monitoring-metrics-input-feature.txt).
- [Current API smoke summary](../evidence/api-smoke-test-summary.json).

The screenshot shows the original dashboard colouring; presentation changes in
the documentation-alignment branch do not alter the historical screenshot.
Dashboard histogram quantiles and five-minute rates should not be substituted
for the per-phase client measurements.

Retained older records:
- Image 0.1: `container-image-summary.json`, training measurements and container
  API smoke summary.
- Storage image 0.2: `storage-container-summary.json` and storage API checks.
- Short image-0.3 benchmark: `review-load-summary.json`, `load-*-requests.csv`,
  `monitoring-deployment-summary.json` and `rd1-dashboard.png`.

These are historical runs with their own bundle/image identities. Do not pair
an older image's size or fingerprint with the latest workload as one run.

## Reproduction and remaining verification

The scripts and setup commands are linked from the [README](../README.md).
The extended workload's `git_head` records its pre-commit parent and
`working_tree_dirty` is true: its producing implementation/script and results
were subsequently committed together in `282cf23093d0d5cf9683987e991f2bfc2d6b7e34`.

The reusable `scripts/check_storage.py` passed on Ubuntu on 17 November
2026. Its result is in [the storage recheck summary](../evidence/storage-recheck-summary.json):
all five checks passed on image 0.5, and temporary resources were removed.
Earlier manual evidence remains separate. Architecture, the pattern/cost comparison, legal classification,
reflection and final deliverables remain separate RD1 work.
