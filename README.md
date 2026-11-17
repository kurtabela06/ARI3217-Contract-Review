# ARI3217-AI-Enterprise-Architectures-and-Transformation
Main repository for ARI3217 - AI Enterprise Architectures and Transformation

## Train and evaluate the model

Run from the project root:

```bash
source .venv/bin/activate
contract-train
```

The command fits the clause classifiers on training passages,
selects the knowledge-retrieval weight and fits calibration on
validation passages, then reports test macro AUPR.

It saves the serving bundle to models/model.joblib by default.
A successful run replaces the bundle at the configured path.

Measurements are saved beside it as model.joblib.metrics.json.
The elapsed time includes the configured pipeline, evaluation and
saving; dataset loading may use existing caches.

The command does not produce a lawyer review pack.

Shared settings are in config/config.yaml.
Supported local overrides are documented in env.example.
Never commit .env, dataset text or generated model artifacts.

A successful command exits with code 0.
A failed command logs its traceback and exits with code 1.

Run tests with:

```bash
python -m pytest tests/ -q
```

## Review API

Run from the project root with a trained serving bundle available:

```bash
source .venv/bin/activate
uvicorn contract_review.api:app --host 0.0.0.0 --port 8888
```

If the bundle is missing, run contract-train first.

Check health:

```bash
curl http://localhost:8888/health
```

Request a review using synthetic example text:

```bash
curl -X POST http://localhost:8888/review \
  -H "Content-Type: application/json" \
  -d '{"text":"The company may terminate this agreement by providing thirty days of written notice."}'
```

The response includes:
- A request identifier and model version.
- Up to the configured number of distinct highlighted passages.
- Category tags and probability estimates.
- Character start/end positions and citations.
- Red-flag categories not found in the highlights.

“Not found in highlights” does not establish that a clause is absent.
The service supports human review; it does not give legal advice.

The bundle loads once at startup. Restart the API after replacing it.
Review requests do not train or recalibrate the model.

Emails and phone numbers are masked with equal-length replacements.
This is partial masking, not complete anonymisation. The supplied email
regex can also mask trailing punctuation.

Interactive documentation: http://localhost:8888/docs

For access from macOS through VirtualBox, forward host port 8888
to guest port 8888.

Run the synthetic HTTP checks while the server is running:

```bash
python scripts/check_review_api.py
```

Training–serving equivalence was checked separately on 99 regular test
contracts and 15 franchise contracts. The check used their already-masked
dataset text; masking behaviour is covered separately by tests.

Stop the server with Control+C.

## Docker deployment

Build the image; training runs during the build:

```bash
docker build --progress=plain -t contract-review:0.1 .
```

Start the API:

```bash
docker run -d --name contract-api -p 8888:8888 contract-review:0.1
```

Check health and run the synthetic API checks:

```bash
curl http://localhost:8888/health
python scripts/check_review_api.py
```

Inspect logs and stop gracefully:

```bash
docker logs contract-api
docker stop --time 30 contract-api
```

Restart the existing container:

```bash
docker start contract-api
```

The image contains a fitted bundle. Starting the container and submitting
reviews do not retrain the model. Training data is removed during the build.

Image identity, architecture and local uncompressed size are recorded in
evidence/container-image-summary.json. Container training measurements and
API smoke-test results are recorded separately in evidence/.

## Persistent review records

Each successful POST /review commits a SQLite record before returning.
Records contain the request ID, UTC timestamp, model version, passage
positions, category scores, and other response metadata. Contract text
and highlighted passage text are excluded.

REVIEW_DB_PATH controls the database location. Its default is
var/reviews.sqlite3, relative to the process working directory.

For Docker, the storage-enabled deployment uses:

```bash
docker volume create contract-review-records
docker run -d --name contract-api-storage-replacement \
  -p 8888:8888 \
  -e REVIEW_DB_PATH=/app/var/reviews.sqlite3 \
  -v contract-review-records:/app/var \
  contract-review:0.2
```

Run this creation command only when the container name and host port are
available. For the existing deployment, use:

```bash
docker stop --time 30 contract-api-storage-replacement
docker start contract-api-storage-replacement
```

The named volume preserves the database across container restarts and
replacement, provided the replacement mounts the same volume. Removing
the container does not remove this named volume.

If the database cannot be written, /review returns HTTP 503 instead of
a successful response. /health checks process availability; it does not
check database write access.

Storage failure and container-replacement persistence were verified.
Evidence is recorded in evidence/storage-failure-summary.json and
evidence/storage-replacement-summary.json.

Retention and backups:
- Records currently remain until deliberately deleted; automatic expiry
  and backups are not implemented.
- An operator must define retention and backup arrangements before
  operational use.
- Stop all containers using the volume before maintenance or deletion.
- Deleting contract-review-records permanently removes its stored history.
- Treat stored metadata as potentially sensitive and restrict access to
  the Docker host and database.

SQLite files are excluded from Git and the Docker build context.

## Monitoring and load benchmark

Start the monitoring deployment after building contract-review:0.3 and
preparing the pinned image references in monitoring/images.env:

```bash
docker compose --env-file monitoring/images.env \
  -f compose.monitoring.yaml -f compose.grafana.yaml \
  -p contract-review up -d
```

Check service state:

```bash
docker compose --env-file monitoring/images.env \
  -f compose.monitoring.yaml -f compose.grafana.yaml \
  -p contract-review ps
```

Endpoints on the Ubuntu VM:
- API health: http://localhost:8888/health
- API metrics: http://localhost:8888/metrics/
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Prometheus and Grafana are published on VM loopback only. From macOS,
open the Grafana tunnel and keep it running:

```bash
ssh -p 2222 -N -L 3000:127.0.0.1:3000 kurt-abela@127.0.0.1
```

Open http://localhost:3000 and select:
Dashboards → RD1 → Contract Review — RD1 Operations.

The provisioned dashboard shows API scrape availability, successful
reviews, 4xx and 5xx responses, processing latency and request rate.
Metrics exclude contract text and request IDs. API counters reset when
the process restarts; Prometheus retains collected history for three days.
Grafana configuration and Prometheus history use persistent volumes.

An available metrics endpoint does not establish that database writes
work or that predictions are correct. Expected HTTP 422 responses from
invalid-input tests are separate from HTTP 5xx server failures.

### Short workload benchmark — 17 November 2026

Run against the local API:

```bash
python scripts/check_review_load.py
```

If dataset discovery fails, provide:
--dataset /path/to/CUAD_v1.json

The test selects 40 complete contracts at evenly spaced ranks by length,
including the shortest and longest. It shuffles them with seed 42 and
uses the same contracts for sequential and two-concurrent-request phases.
Three successful warm-up requests are excluded from the measurements.
Running the complete test creates 83 review records.

Selected lengths: minimum 645, median 33,391, p95 approximately 163,466,
and maximum 338,211 characters.

| Measure | Sequential | Concurrency 2 |
|---|---:|---:|
| Successful requests | 40/40 | 40/40 |
| Failed requests | 0 | 0 |
| Client p50 latency | 28.12 ms | 53.53 ms |
| Client p95 latency | 71.65 ms | 142.41 ms |
| Maximum client latency | 152.22 ms | 170.91 ms |
| Observed successful throughput | 26.95 reviews/s | 30.33 reviews/s |

The VM provided Docker with two CPUs and approximately 5.26 GiB of memory.
The API, load generator, Prometheus and Grafana shared this VM.

Client timings include receiving and parsing the response. They include
inference and database saving, but exclude model startup and training.
Dashboard percentiles are histogram estimates over a rolling window and
need not equal the client percentiles calculated from individual requests.

Each phase lasted approximately 1.3–1.5 seconds. These are short workload
measurements, not sustained production capacity or a simulation of normal
monthly arrivals. Request success does not establish extraction accuracy.
The sequential phase ran first; order and cache effects were not isolated.

Evidence:
- evidence/review-load-summary.json
- evidence/load-sequential-requests.csv
- evidence/load-burst-requests.csv
- evidence/monitoring-deployment-summary.json
- evidence/monitoring-metrics.txt
- evidence/rd1-dashboard.png

The summary records the pre-benchmark Git HEAD and a dirty working tree.
The monitoring implementation, benchmark script and results are committed
together so the producing code and evidence can be inspected together.

This dashboard covers operational behaviour. Contract-type monitoring and
recall from delayed lawyer corrections remain separate project work.
