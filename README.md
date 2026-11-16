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
