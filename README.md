# Contract Review Assistant — ARI3217, Task 29

A human-in-the-loop clause-highlighting service for lawyers. The supplied
non-LLM extractor ranks passages; a lawyer owns the review and signing decision.
The response supports review and does not constitute legal advice.

**Current checkpoint:** the baseline, supplementary chronological experiment,
loaded-bundle equivalence, Docker API, persistent records, input-feature metrics,
and extended local workload have recorded evidence. Architecture, the capability-
pattern comparison, governance reasoning, reflection, and final RD1 submission
materials remain in progress. See [project status](docs/project-overview.md), the
[checklist](docs/entry1-checklist.md), and the [evidence index](docs/evidence-index.md).

## Dataset, attribution and evaluation

This project uses **CUAD v1**, by **The Atticus Project**, described in Hendrycks
et al. (2021), *CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review*.
Source: [CUAD project](https://www.atticusprojectai.org/cuad) and the
[Kaggle mirror used by the notebook](https://www.kaggle.com/datasets/konradb/atticus-open-contract-dataset-aok-beta).
The dataset is attributed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The underlying agreements are public SEC EDGAR filings; CUAD's README makes no
representation about the contracts' own licensing. Dataset licensing is distinct
from a licence for this project's code.

The dataset contains 510 contracts and 41 clause categories. Near-duplicate
filings are grouped into families. The primary protocol uses 297 training,
99 validation, and 99 test contracts; 15 franchise agreements are held out as
simulated new business. Families stay together in the regular split. Classifiers
fit training data; weight selection and calibration use validation data.

The separate filing-year experiment trains before 2010, validates on 2010–2014,
and tests from 2015. Its populations differ from the primary baseline, so its
metrics must not be treated as a causal comparison. Details and exclusions are
in [ADR 001](docs/decisions/001-evaluation-protocol.md).

Working-tree policy excludes datasets, processed contract text, credentials and
trained bundles. Emails and phones are masked with equal-length replacements;
this is partial masking, not anonymisation. The supplied email regex can consume
trailing punctuation. The current reference notebook has cleared outputs; an
older public commit retains supplied example outputs, as documented in
[ADR 002](docs/decisions/002-notebook-output-policy.md).

## Install from a fresh checkout

The recorded host runs used Python 3.14.4; the pinned Docker base uses 3.14.10.
The measured deployment is Linux/arm64. Timings are hardware-specific.

```bash
git clone https://github.com/kurtabela06/ARI3217-Contract-Review.git
cd ARI3217-Contract-Review
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install --no-deps -e .
python -m pytest tests/ -q
```

Use the pinned requirements first; `pip install -e ".[dev]"` alone can resolve
new dependency versions. `pyproject.toml` declares package compatibility rather
than the exact measured environment. The full pinned environment includes
notebook and development dependencies.

Run commands from the project root. Optional local settings:

```bash
cp env.example .env
```

Edit `.env` only if the defaults need changing. It is Git-ignored. Shared model
settings are in `config/config.yaml`, with the red-flag list in
`config/red_flags.json`. Supported local overrides are `DATA_PATH`, `MODEL_PATH`,
and `LOG_LEVEL`; `CONFIG_PATH` selects a different YAML file. `REVIEW_DB_PATH`
controls the review database independently.

## Train and evaluate

```bash
contract-train
```

The command obtains CUAD through Kaggle when local inputs are absent. It can
reuse downloaded or processed caches. Preserve provenance when substituting
local data; a cache-backed run is not a new raw-data validation.

It runs the configured pipeline, evaluates test macro AUPR, and replaces
`models/model.joblib` by default. It saves measurements alongside the bundle as
`model.joblib.metrics.json`. Elapsed time includes the pipeline, evaluation and
saving; it is different from classifier-fitting time alone. Success exits with
code 0; failure logs a traceback and exits non-zero. It does not output a lawyer
review pack. The thin client is `notebooks/contract_review.ipynb`.

Run `python scripts/check_data_quality.py` for the measured data checks and
`python scripts/check_serving_equivalence.py` to compare a fitted saved bundle
against a reference pipeline. The latter retrains the reference in memory;
it does not replace the serving bundle.

## Current Docker and monitoring deployment

The current measured API image is **`contract-review:0.5`**. Earlier `0.1`–`0.3`
image measurements are historical checkpoints, retained under `evidence/`.

Build and prepare the external database volume:

```bash
docker build --progress=plain -t contract-review:0.5 .
docker volume create contract-review-records
```

When its layer is rebuilt, the Dockerfile runs `contract-train` and removes the
training data and Kaggle cache in that same layer. Starting the container loads
its fitted bundle and does not train. The Python base is pinned by digest in
`Dockerfile`; its recorded details are in
`evidence/python-base-image-summary.json`. Prometheus and Grafana digest
references are committed in `monitoring/images.env`.

Validate and start the stack, with host port 8888 available:

```bash
docker compose --env-file monitoring/images.env \
  -f compose.monitoring.yaml -f compose.grafana.yaml \
  -p contract-review config --quiet

docker compose --env-file monitoring/images.env \
  -f compose.monitoring.yaml -f compose.grafana.yaml \
  -p contract-review up -d
```

Check state and API logs:

```bash
docker compose --env-file monitoring/images.env \
  -f compose.monitoring.yaml -f compose.grafana.yaml \
  -p contract-review ps -a

docker compose --env-file monitoring/images.env \
  -f compose.monitoring.yaml -f compose.grafana.yaml \
  -p contract-review logs --tail 60 api

curl http://127.0.0.1:8888/health
```

Wait for health to return `"status":"ok"` before HTTP checks. If port 8888 is
occupied, identify its listener with `ss -ltnp 'sport = :8888'`; stop the host
Uvicorn process or the known earlier API container before retrying.

Endpoints on the Ubuntu VM:

| Service | URL |
|---|---|
| API health | http://localhost:8888/health |
| Interactive API documentation | http://localhost:8888/docs |
| Metrics | http://localhost:8888/metrics/ |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

Prometheus and Grafana are published on VM loopback only. From a Mac terminal,
with the VM's SSH forwarding available, substitute the Ubuntu username:

```bash
ssh -p 2222 -N -L 3000:127.0.0.1:3000 YOUR_UBUNTU_USER@127.0.0.1
```

Keep that terminal open, sign in to Grafana with the configured credentials,
and open **Dashboards → RD1 → Contract Review — RD1 Operations**. A fresh
Grafana installation initially uses `admin`/`admin` and prompts for a new password.
The dashboard and data source are provisioned from `monitoring/grafana/`.
Closing the browser or SSH tunnel does not stop Prometheus collection. Select
the benchmark's historical time range to inspect an earlier run.

Stop the stack without deleting its persistent data:

```bash
docker compose --env-file monitoring/images.env \
  -f compose.monitoring.yaml -f compose.grafana.yaml \
  -p contract-review stop
```

Prometheus retains collected metrics for three days. Review records and Grafana
configuration use separate persistent volumes. The local application tag is
not a published registry image; a fresh machine must build it. Check pinned
image availability when reproducing on a different processor architecture.

## Review requests and persistence

Synthetic example:

```bash
curl -X POST http://127.0.0.1:8888/review \
  -H 'Content-Type: application/json' \
  -d '{"text":"The company may terminate this agreement with thirty days of notice."}'
```

The response includes a request ID, bundle-derived model version, up to the
configured number of passages, category probabilities, start/end offsets,
citations and red-flag categories not found in the selected highlights.
**Not found in highlights does not establish absence.** Restart the API after
replacing its bundle. Requests do not train or recalibrate the model.

For host-only development, with Compose's API stopped and a fitted host bundle:

```bash
uvicorn contract_review.api:app --host 0.0.0.0 --port 8888
```

Keep one worker for the current metrics implementation. Host-only testing does
not make the API reachable at Prometheus's Compose target `api:8888`.

Successful review requests commit a SQLite record before HTTP 200 returns.
Records include request ID, UTC timestamp, model version, passage locations,
citations and category scores. Contract and passage text are excluded from the
database. `REVIEW_DB_PATH` defaults to `var/reviews.sqlite3`; Compose sets
`/app/var/reviews.sqlite3` on the external volume `contract-review-records`.
Mounting that same volume preserves history across container replacement.

An unwritable database yields HTTP 503. `/health` checks process availability,
not database writes. Invalid requests are not stored as successful reviews.
The SQLite choice and its limits are recorded in
[ADR 003](docs/decisions/003-review-storage.md); the reference workflow's
PostgreSQL step is a documented deviation, not an implemented PostgreSQL service.

Records currently persist until deliberately deleted. Automatic expiry and
backups are not implemented. The operator must define retention and backups
before operational use, restrict host/database access, and stop volume users
before maintenance. Deleting the named review volume removes its records.

## Verification and monitoring semantics

With the local API running:

```bash
python scripts/check_review_api.py
python scripts/check_input_metrics.py
```

Run the input-metric check without concurrent review submissions because it
compares exact before/after values. These commands create synthetic review
records and refresh their evidence summaries. Preserve earlier evidence before
rerunning if it is needed for a historical comparison.

The unit suite includes SQLite minimisation, failure and duplicate-request
checks. A separate end-to-end Docker recheck uses only temporary containers and
a disposable volume; it publishes no ports and never mounts the live records:

```bash
python scripts/check_storage.py --image contract-review:0.5
```

This checks successful persistence, restart, replacement, another write after
replacement, and HTTP 503 on an invalid storage path. It removes its temporary
resources and writes `evidence/storage-recheck-summary.json`. Use another
`--output` path for a subsequent run. Historical Docker checks retain their original evidence. The reusable
recheck passed on Ubuntu on 17 November 2026; its result is recorded in
`evidence/storage-recheck-summary.json`.

The dashboard shows request status counts, processing latency, scrape
availability, and contract-length mean/p95. Length observations count nonblank
validated submissions, including those that later fail; rejected inputs are
excluded. Metrics contain no contract text or request IDs. Counters reset when
the API process restarts. A green availability panel does not establish correct
predictions or successful database writes.

Dashboard p95 values are histogram estimates over rolling five-minute windows.
Input-length bucket estimates can differ from exact percentiles. Successful
client timings in the CSVs include receiving/parsing the response; server
processing timings stop at response preparation. Failed requests are reported
separately. These measurements exclude training and startup.

## Extended local workload — 17 November 2026

```bash
python scripts/check_review_load.py --repeats 50 --output-prefix sustained-load
```

That prefix already has committed evidence. To run another experiment, choose
an unused prefix, for example `--output-prefix sustained-load-recheck`; the
script refuses to overwrite existing non-default-prefix outputs. For explicit
data selection, add `--dataset /path/to/CUAD_v1.json`.

The test selects 40 complete contracts at evenly spaced length ranks, including
the shortest and longest, shuffles with seed 42 and repeats each 50 times per
phase. Three warm-ups are excluded. It creates 4,003 records if all requests
succeed. The unique-input lengths are minimum 645, median 33,391, p95 about
163,466, and maximum 338,211 characters.

| Measure | Sequential | Concurrency 2 |
|---|---:|---:|
| Successful measured requests | 2,000/2,000 | 2,000/2,000 |
| Failed measured requests | 0 | 0 |
| Phase duration | 75.69 s | 69.83 s |
| Client p50 | 29.70 ms | 62.63 ms |
| Client p95 | 96.10 ms | 142.92 ms |
| Maximum client latency | 150.65 ms | 266.61 ms |
| Observed successful throughput | 26.42 reviews/s | 28.64 reviews/s |

The Linux/arm64 VM made two CPUs and 5,646,544,896 bytes (about 5.26 GiB) available
to Docker. The client, API, Prometheus and Grafana shared it. Host/client Python
was 3.14.4; the API's pinned base was 3.14.10. The measured API image size was
328,175,166 bytes (312.97 MiB, local uncompressed size).

Concurrency two increased observed throughput by about 8.4% and p95 latency by
about 49%. This is one sequential-then-concurrent experiment on repeated inputs,
not independent replicated trials, a normal 40-contracts-per-month arrival
simulation, a long-running soak test or an accuracy evaluation. Order/cache
and shared-resource effects were not isolated. The original 40-request-per-phase
short experiment is retained separately; do not mix its values with this run.

## Evidence and remaining RD1 work

See the [evidence index](docs/evidence-index.md) for the baseline, fresh-copy,
chronological, serving, storage, image and load records with commit references.
The supplied notebook's worked outputs are comparison targets, not the student's
own measurements.

The baseline regular-test red-flag recall at 20 passages is 88.02%; held-out
franchise recall is 53.33%. A healthy service cannot reveal this quality gap
without labels or corrections. Contract-type and delayed-recall monitoring
remain wider-project work.

The four-layer architecture, pattern comparison (including daily cost and
failure ownership), supported AI Act position, reflection, AI-use disclosure,
and 400–600-word PDF, 5–8 content slides and at-most-five-minute video remain to
be completed. CI/MLflow, later knowledge tasks and local-model GenAI are tracked
separately; the current operational checkpoint does not complete all notebook
tasks. See [audit follow-up](docs/repository-audit-followup.md).
