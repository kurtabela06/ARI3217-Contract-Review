# Reflective Diary Entry 1 — checklist

Deadline: 23 November 2026.
Check the exact submission time on the VLE.

## Administration
- [X] Task 29 recorded on the allocation sheet.
- [X] Task 29 announced in the VLE forum.
- [X] University rules on AI assistance checked.

## Baseline and implementation
- [X] Original notebook preserved.
- [X] Given model run from a clean kernel.
- [X] Headline metrics and training time recorded.
- [X] Model and preprocessing packaged without learner replacement/tuning.
- [X] Configuration, training command and unit tests added.
- [X] Notebook retained as a thin client.

## Data investigation
- [X] At least three documented quirks verified with counts.
- [X] One additional potential issue investigated.
- [X] At least one quirk guarded by a test or input check.
- [X] Findings table records consequence and safeguard.

## Reproducibility and deployment
- [X] Pinned requirements recorded.
- [X] Fresh-copy run reproduces metrics within a stated tolerance.
- [X] Container serves reviews.
- [X] Image identifier and size recorded.
- [X] Training and serving preprocessing consistency checked.

## Monitoring and performance
- [X] Successful review requests persisted with request ID, UTC timestamp and model version; invalid requests are not successful review records.
- [X] Request count, latency and contract-character length exposed; validated input-feature check recorded.
- [X] Complete-contract workload documented and executed: 40 unique inputs repeated 50 times per phase, concurrency 1/2; controlled-capacity limitations stated.
- [X] p95 latency or batch throughput recorded.
- [X] Dashboard evidence captured, including the input-feature panel and historical benchmark window.

## Audit follow-up
- [X] Python base image pinned by digest.
- [X] Current deployment and measured results indexed in documentation.
- [X] Reusable Docker storage recheck passed on Ubuntu; result recorded separately from historical manual checks.
- [X] Historical supplied outputs reviewed; final retention decision recorded in ADR 002.

## Architecture and reasoning
- [x] Four-layer enterprise architecture diagram.
- [ ] Chosen capability pattern compared against one alternative.
- [ ] Comparison includes latency, daily cost, ownership and failure.
- [ ] AI Act tier, provision, provider and deployer stated.
- [ ] At least three reflection prompts addressed.
- [ ] Every reported measurement traces to a commit.
- [ ] AI assistance disclosed.

## Submission
- [ ] Written PDF: 400–600 words, excluding permitted supporting material.
- [ ] Slides PDF: 5–8 content slides.
- [ ] Video: at most 5 minutes, in my own voice.
- [ ] Data findings table.
- [ ] Service results table and dashboard panel.
- [ ] Architecture diagram and pattern comparison table.
- [ ] Classification statement.
- [ ] Submission files checked and uploaded before the cutoff.
