# RD1 — Four-layer enterprise architecture

![Four-layer enterprise architecture](images/contract-review-architecture.png)

## Scope

This is a local prototype of an online, human-in-the-loop contract-review
service. The API returns cited highlights; a lawyer retains responsibility
for reviewing the agreement and deciding what action to take.

Intake/CLM integration is an intended enterprise connection, not an
implemented integration. The current interface is HTTP JSON, exercised
through scripts, curl and interactive API documentation.

## Layer map

| Layer | Components and responsibilities |
|---|---|
| Business | Legal operations defines the review policy and capacity assumptions. A lawyer interprets the highlights and owns the review/signing decision. The notebook assumes approximately 40 contracts per month and a 20-passage review budget. |
| Application | FastAPI exposes health and review endpoints. The contract_review package masks contacts, chunks text, applies the saved extractor and selects highlights. contract-train handles offline training. Grafana presents operational measurements. Intake/CLM integration is planned. |
| Data | CUAD supplies training/evaluation text and annotations. The fitted bundle contains vocabulary, weighting, classifiers, calibration, knowledge-query vectors and review settings. SQLite records request IDs, timestamps, model versions, passage locations and scores. Prometheus retains metric history. |
| Technology | Docker Compose runs the API, Prometheus and Grafana on the Ubuntu VM. Uvicorn serves one API process. SQLite writes to a named external Docker volume. Prometheus and Grafana have separate persistent volumes. The measured deployment is Linux/arm64 with two CPUs and approximately 5.26 GiB available to Docker. |

## Architecture diagram

Solid arrows describe implemented relationships. The dotted arrow marks
the intended intake integration.

```mermaid
flowchart TB
    subgraph B["Business"]
        Lawyer["Lawyer: review and decision"]
    end

    subgraph A["Application"]
        Intake["Intake / CLM: planned"]
        API["Review API and package"]
        Train["Offline training command"]
        Dashboard["Grafana dashboard"]
    end

    subgraph D["Data"]
        Dataset["CUAD inputs and annotations"]
        Bundle["Fitted serving bundle"]
        Records["Minimised review records"]
        Metrics["Operational metric history"]
    end

    subgraph T["Technology"]
        Runtime["Ubuntu VM and Docker containers"]
        Volumes["Persistent Docker volumes"]
    end

    Lawyer -->|"submits contract"| API
    API -->|"returns cited highlights"| Lawyer
    Intake -.->|"intended integration"| API

    Train -->|"reads"| Dataset
    Train -->|"saves"| Bundle
    API -->|"loads at startup"| Bundle
    API -->|"commits before success"| Records
    API -->|"metrics scraped by Prometheus"| Metrics
    Dashboard -->|"queries through Prometheus"| Metrics

    API -->|"runs on"| Runtime
    Dashboard -->|"runs on"| Runtime
    Records -->|"persisted in"| Volumes
    Metrics -->|"persisted in"| Volumes
```

The runtime also hosts Prometheus. Its collection/query functions are
represented by the metrics relationships; metric history is the data-layer
asset. Grafana's own configuration also persists in a separate volume.

The serving bundle is retained inside the built API image. It is not stored
in the review-records volume. Training inputs are removed from the final
training build layer after the bundle is saved.

## Request and decision responsibilities

1. A caller submits contract text to POST /review.
2. The service validates input, masks emails/phones without shifting offsets,
   chunks the text and scores it using the fitted bundle.
3. It selects up to the configured passage budget and prepares citations.
4. It commits minimised review metadata before returning HTTP 200.
   An unwritable database returns HTTP 503.
5. The lawyer interprets the highlights alongside the original agreement.
   “Not found in highlights” does not establish absence.
6. The operator uses monitoring to investigate availability, errors, latency
   and changes in submitted contract lengths.

The business roles are the proposed enterprise operating model; the current
prototype does not implement lawyer authentication, CLM integration or
capture of lawyers' corrections.

## Cross-layer consequence: healthy service, weak predictions

The operational dashboard does not have immediate ground-truth labels.
It can show low latency and successful requests while important clauses are
missed. The baseline's recall at 20 passages was approximately 88.02% on
regular test contracts and 53.33% on held-out franchise agreements.

Lawyers' corrections would provide delayed quality labels. This data-layer
delay means operational monitoring cannot establish live extraction recall.
A complete production design would need a feedback process, quality monitoring
and a route to fuller manual review. Those mechanisms are not implemented
by the current dashboard.

## Evidence

Implementation and extended-workload checkpoint:
282cf23093d0d5cf9683987e991f2bfc2d6b7e34.

- compose.monitoring.yaml and compose.grafana.yaml
- evidence/sustained-load-deployment-summary.json
- evidence/review-sustained-load-summary.json
- evidence/storage-recheck-summary.json
- evidence/baseline-operating-point-results.csv
- docs/evidence-index.md

This architecture describes the current prototype and clearly labels the
intended integration. It does not claim a production deployment.
