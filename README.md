# Contract Review Assistant

ARI3217, Task 29 · Reflective Diary Entry 1

The service highlights clauses in commercial contracts for pre-signing review.
The supplied extractor scores passages, the API returns cited highlights, and
lawyers decide how to proceed. The prototype runs on Ubuntu with Docker,
SQLite, Prometheus and Grafana.

[RD1 evidence index](docs/evidence-index.md) · [Architecture](docs/architecture.md) ·
[Online and batch comparison](docs/capability-pattern-comparison.md) ·
[AI Act assessment](docs/ai-act-classification.md)

## Reproduce the baseline

The project uses [CUAD v1](https://www.atticusprojectai.org/cuad) by The Atticus
Project (Hendrycks et al., 2021), via the [Kaggle mirror](https://www.kaggle.com/datasets/konradb/atticus-open-contract-dataset-aok-beta).
CUAD is attributed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The underlying agreements are public SEC filings with separate licensing
considerations. The original [cleared Task 29 notebook](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/10cc10ad543143bf383344d62280b62a816d254c/29_contract_review.ipynb)
is the source for the supplied model and dataset card.

The recorded fresh-copy run used Python 3.14.4 on Ubuntu. From the repository root:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install --no-deps -e .
python -m pytest tests/ -q
contract-train
```

`contract-train` loads CUAD from the local cache or Kaggle, evaluates the
configured extractor, and writes the fitted bundle and metrics under `models/`.
The [thin notebook client](notebooks/contract_review.ipynb) imports the same
package. Settings are in [config.yaml](config/config.yaml) and
[red_flags.json](config/red_flags.json). Optional local overrides are documented
in [env.example](env.example) and [the configuration loader](src/contract_review/config.py).

The packaged and fresh-copy combined test macro AUPR both measured 0.499002.
The grouped baseline preserves contract families and the franchise holdout.
The forward-time experiment trains on filings before 2010, validates on
2010–2014 and tests on 2015 onward under a separate [evaluation protocol](docs/decisions/001-evaluation-protocol.md).
Run these checks from the same pinned environment:

```bash
python scripts/check_data_quality.py
python scripts/check_combined_baseline.py
python scripts/check_serving_equivalence.py
python scripts/run_temporal_evaluation.py
```

The serving-equivalence check compares a fitted host bundle with the reference
pipeline on pre-masked inputs. The [data findings](docs/data-findings.md) record
three supplied quirks or traps, two additional checks, and the safeguards.

## Run the Docker service

Build the local image and bring up the stack from the repository root. An uncached
build trains the bundle. The API loads that fitted bundle at startup.

```bash
docker build --progress=plain -t contract-review:0.5 .
docker volume create contract-review-records
docker compose --env-file monitoring/images.env \
  -f compose.monitoring.yaml -f compose.grafana.yaml -p contract-review up -d
curl --retry 15 --retry-connrefused --fail http://127.0.0.1:8888/health
```

The health response includes the loaded model version. This synthetic request
exercises the review endpoint:

```bash
curl --fail -X POST http://127.0.0.1:8888/review \
  -H 'Content-Type: application/json' \
  -d '{"text":"The company may terminate this agreement with thirty days of notice."}'
```

The response contains cited highlights, offsets and category scores within the
configured review budget. Absence from the highlights does not establish absence
from the contract. Successful requests commit minimised review metadata before
HTTP 200 returns. An unwritable database returns HTTP 503. The external named
volume retains records across container replacement. See [ADR 003](docs/decisions/003-review-storage.md)
for the SQLite choice and persistence evidence.

## Verify and monitor

With the API running on port 8888:

```bash
python scripts/check_review_api.py
python scripts/check_input_metrics.py
python scripts/check_review_load.py --repeats 50 --output-prefix sustained-load-recheck
```

Run the input metric check without parallel submissions. The first two scripts
refresh their evidence summaries. Use a new prefix for each load run to preserve
previous evidence. For an isolated Docker storage check, use:

```bash
python scripts/check_storage.py --image contract-review:0.5 --output /tmp/rd1-storage-recheck.json
```

Prometheus scrapes `/metrics/` and Grafana shows status counts, processing latency
and submitted contract length. On the VM, Grafana is at `http://127.0.0.1:3000`
and Prometheus at `http://127.0.0.1:9090`. With SSH forwarded to host port 2222,
open Grafana through the tunnel:

```bash
ssh -p 2222 -N -L 3000:127.0.0.1:3000 YOUR_UBUNTU_USER@127.0.0.1
```

In Grafana, open **Dashboards → RD1 → Contract Review — RD1 Operations**. The
[recorded panel](evidence/rd1-dashboard-input-feature.png) shows the 17 November
window. Grafana estimates rolling server latency. The load script records
per-phase client latency, including response transfer and parsing. Neither
metric measures clause recall. The [architecture notes](docs/architecture.md)
explain why the held-out franchise results matter despite a healthy dashboard.

Stop the stack while keeping the volumes:

```bash
docker compose --env-file monitoring/images.env \
  -f compose.monitoring.yaml -f compose.grafana.yaml -p contract-review stop
```

## Reproduce the matched online and batch test

With Docker running and `contract-review:0.5` built, use the same pinned Python
environment. The runner checks the CUAD fingerprint, uses an isolated API
container and launches two workers for each phase.

```bash
batch_run=$(mktemp -d)
python scripts/check_review_batch.py --output-dir "$batch_run"
cat "$batch_run/review-batch-summary.json"
```

The [18 November summary](evidence/review-batch-summary.json) records 2,000
successful reviews per mode. Online client p95 was 130.81 ms and the online
phase finished in 63.74 s. The on-demand batch published the packs in 63.69 s.
The batch ran against the same API, and daily schedule wait and running cost
are unmeasured. The results file can contain contract excerpts, so keep it local
and share the metadata-only summary.

## Submission evidence

The [evidence index](docs/evidence-index.md) maps the report’s figures and
measurements to their files and commits. Cite the same measurements across the
written PDF, slides PDF and video. Keep the finished files or video link
together under `submission/`. See the [personal reflection](docs/personal-reflection.md)
and [AI-use disclosure](docs/ai-use-disclosure.md) for the reasoning and use of
assistance. Later project work such as CI/MLflow and GenAI lies outside this RD1
checkpoint.

Keep datasets, fitted bundles, credentials and excerpt-containing outputs out of
new commits. [ADR 002](docs/decisions/002-notebook-output-policy.md) records the
approved exception for supplied notebook examples already present in Git history.
