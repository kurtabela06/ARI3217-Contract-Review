# Contract Review Assistant

ARI3217 individual project, Task 29. Status reviewed on 17 November 2026.

Purpose: highlight contract clauses for human lawyer review. The lawyer owns the
review/signing decision; the service does not provide legal advice.

Dataset: CUAD v1, The Atticus Project, from public SEC EDGAR filings. Attribute
the dataset under CC BY 4.0; the contracts have separate licensing caveats.

## Recorded implementation checkpoint

- The supplied classifier and knowledge blend are packaged with configuration,
  a training command, a thin notebook client and unit tests.
- Baseline and fresh-copy combined test macro AUPR are 0.49900236, using the same
  primary holdout fingerprint. Supplementary filing-year evaluation is separate.
- Loaded-bundle equivalence was checked on 99 test and 15 franchise contracts.
- Docker image `contract-review:0.5` serves the API with SQLite review metadata
  on a named external volume. Training happens during an uncached training build
  layer; requests use the fitted bundle.
- Prometheus and Grafana collect request/status counts, processing latency and
  contract-length metrics. The extended benchmark recorded 4,000 measured
  requests without failures, with input, duration and resource limits stated.

These records are indexed in [the evidence index](evidence-index.md). The latest
implementation/evidence checkpoint is commit `282cf23093d0d5cf9683987e991f2bfc2d6b7e34`.

## Remaining RD1 work

Four-layer enterprise architecture; a quantified pattern comparison including
running cost and ownership/failure behaviour; AI Act reasoning; reflection and
AI-use disclosure; the written PDF, slides, video and final submission checks.

The reusable Docker storage recheck passed on Ubuntu on 17 November 2026.
Its result is in `evidence/storage-recheck-summary.json`; earlier manual
checks retain their original evidence.

## Scope and history

Dataset files, processed text, credentials and fitted artifacts are excluded
from the current working tree. The current reference notebook has cleared
outputs. Older supplied notebook outputs remain in public history; see
[ADR 002](decisions/002-notebook-output-policy.md) and
[audit follow-up](repository-audit-followup.md).

The operational RD1 checkpoint is separate from completing all C1–C5, E1–E4 and
S1 tasks. CI gates, MLflow/registry, full knowledge tasks, and local-model GenAI
are later project work unless independently completed and evidenced.
