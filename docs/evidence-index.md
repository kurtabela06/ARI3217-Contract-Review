# RD1 evidence index

Use the commit links below when citing measurements. The matched batch summary
and its exact runner are included together in the submission tree. The summary’s
`git_head` identifies the clean project checkout used to run the test. Its
`benchmark_script_sha256` identifies the measurement script used on the VM.

## Model, data and architecture

| Claim | Recorded result | Evidence and commit |
|---|---|---|
| Supplied baseline | 510 contracts and 41 categories. Grouped split 297/99/99, with 15 franchise contracts held out separately. Classifier test macro AUPR 0.489085. | [Notebook run](https://github.com/kurtabela06/ARI3217-Contract-Review/tree/eb7b2f3f4992fdf95209a5cbd4bd96833b3e4e7e/evidence), [split summary](../evidence/baseline-split-summary.csv), [headline CSV](../evidence/baseline-headline-metrics.csv). |
| Packaged baseline | Combined test macro AUPR 0.49900236 at knowledge weight 0.25. | [Combined summary at `768da6c`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/768da6cfc79a9ffe8493d1517d63f6f4b3f6c55c/evidence/packaged-combined-summary.csv). |
| Fresh-copy reproduction | Same combined AUPR, weight and holdout fingerprint. Full command took 27.22 s. | [Fresh-copy verification at `26780cc`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/26780cca9282e22cf306091fff4272ce619fa97e/evidence/fresh-copy-verification.json). |
| Original Part B classifier fit | 5 s in the student notebook run and 10 s in the supplied notebook output. Both display rounded seconds. | [Student timing record at `ad91069`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/ad910690fb9baa6878e4af21b873f85c052df950/evidence/notebook-part-b-fit-timing.json), [cropped output](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/ad910690fb9baa6878e4af21b873f85c052df950/evidence/notebook-part-b-fit-stdout.png), [supplied Part B notebook at `7f27e29`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/7f27e29a427c909517b0fd319efd1a7c2084b86d/29_contract_review.ipynb). |
| Packaged training timing | 4.45 s to fit the packaged classifier. The configured train, evaluate and save command took 20.73 s. | [Fit at `c65f3e8`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/c65f3e8324518c92c0fef55b0a3605e54ee952e9/evidence/packaged-classifier-measurements.json), [command at `46fda34`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/46fda346f3cc6f10387ed022cb47676ab45a3445/evidence/packaged-training-command.json). |
| Three supplied issues and two additional checks | 5/41 rare categories, 14,208/20,910 no-answer pairs, 895/13,823 cut spans, zero excess duplicates and zero invalid offsets. | [Counts at `e4da385`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/e4da385ad3ba487656aa9df156e40b23555d91a2/evidence/data-quality-summary.csv), [findings and safeguards](data-findings.md). |
| Filing-year evaluation | 0.489589 test macro AUPR, 677/792 red flags found at 20 passages (85.48%). | [Temporal metrics at `1749ba1`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/1749ba1581bb30fb630ec42264583114536911e8/evidence/temporal-evaluation-summary.json), [protocol](decisions/001-evaluation-protocol.md). |
| Serving equivalence | Loaded-bundle scoring matched the reference pipeline for selections and scores on 114 pre-masked contracts. The API smoke test exercised the HTTP route separately. | [Equivalence check at `be61713`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/be617131d20133ea2578a5de0fedf78f0874665a/evidence/serving-equivalence-summary.json). |
| Review quality at 20 passages | Red-flag recall 88.02% on the regular test set and 53.33% on held-out franchise agreements. | [Operating point at `eb7b2f3`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/eb7b2f3f4992fdf95209a5cbd4bd96833b3e4e7e/evidence/baseline-operating-point-results.csv). |
| Four-layer architecture | Business, application, data and technology responsibilities, with intake/CLM integration marked as planned. | [Rendered diagram at `270f0f1`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/270f0f16515ae9e1b41963e5fa2857322b02a09e/docs/images/contract-review-architecture.png), [layer map](architecture.md). |

The fresh-copy result uses the [dependency pins at `e4896a3`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/e4896a358bef0b557e9de52366a47a3a383d1e00/requirements.txt)
and the cache scope recorded in its summary. The two evaluation protocols use
different populations. The serving check concerns the recorded pre-masked
workload and fitted host bundle.

## Service, monitoring and persistence

| Claim | Recorded result | Evidence and commit |
|---|---|---|
| Image and VM | API image `contract-review:0.5`, 328,175,166 bytes (312.97 MiB). Linux/arm64, 2 CPUs and about 5.26 GiB available to Docker. | [Deployment at `282cf23`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/282cf23093d0d5cf9683987e991f2bfc2d6b7e34/evidence/sustained-load-deployment-summary.json), [base image](../evidence/python-base-image-summary.json). |
| Extended online workload, 17 November | Sequential p95 96.10 ms at 26.42 reviews/s. Two concurrent requests had 142.92 ms p95 at 28.64 reviews/s. Zero failures across 4,000 measured reviews with three warm-ups excluded. | [Summary at `282cf23`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/282cf23093d0d5cf9683987e991f2bfc2d6b7e34/evidence/review-sustained-load-summary.json), [sequential CSV](../evidence/sustained-load-sequential-requests.csv), [two-worker CSV](../evidence/sustained-load-burst-requests.csv). |
| API and input metrics | Cited response and validation verified. One valid 84-character request added one length observation and 84 characters. A blank request added neither. | [API smoke test at `282cf23`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/282cf23093d0d5cf9683987e991f2bfc2d6b7e34/evidence/api-smoke-test-summary.json), [metric check at `282cf23`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/282cf23093d0d5cf9683987e991f2bfc2d6b7e34/evidence/input-metrics-check-summary.json), [metrics snapshot](../evidence/monitoring-metrics-input-feature.txt). |
| Grafana | Status, latency and contract length for the 17 November benchmark window. | [Dashboard capture at `282cf23`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/282cf23093d0d5cf9683987e991f2bfc2d6b7e34/evidence/rd1-dashboard-input-feature.png). |
| SQLite recheck | Records persisted through restart and replacement, with another successful write after replacement. An unwritable database returned HTTP 503. | [Storage recheck at `22152bf`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/22152bfae9ee2537a2c6c967f3b9e8347f861451/evidence/storage-recheck-summary.json), [storage ADR](decisions/003-review-storage.md). |

The 17 November benchmark repeated 40 length-stratified complete contracts 50
times per phase. Its runner and the client, API, Prometheus and Grafana shared
one VM. The historical capture reflects the Grafana presentation at the time.
The panel's five-minute server p95 of about 157 ms comes from interpolation
within the 100–250 ms histogram bucket. Applying the same interpolation to the
archived cumulative counts gives 158.32 ms. The client p95 values come from
individual request times in each phase.
[Histogram snapshot at `282cf23`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/282cf23093d0d5cf9683987e991f2bfc2d6b7e34/evidence/monitoring-metrics-input-feature.txt) ·
[Prometheus quantile calculation](https://prometheus.io/docs/prometheus/latest/querying/functions/#histogram_quantile).

## Matched online and batch test

On 18 November 2026, the matched run used the same CUAD selection and image
as the 17 November benchmark. Its clean base checkout was
[`7bcddbd`](https://github.com/kurtabela06/ARI3217-Contract-Review/commit/7bcddbdf02cf0c5497c619929cbeed0d2dd5675d).
Both phases used two workers and 2,000 reviews in an isolated API container
with model `0.1.0:eef20dbe2aca`. Three warm-ups were excluded.

| Measure | Online API | On-demand batch |
|---|---:|---:|
| Successful reviews | 2,000/2,000 | 2,000/2,000 |
| Elapsed time | 63.74 s for the phase | 63.69 s from start to published packs |
| Successful throughput | 31.38 reviews/s | 31.40 reviews/s |
| Client API p95 | 130.81 ms for individual responses | 131.76 ms for internal API requests |

[Batch summary at `4e57df4`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/4e57df4a4fec747d17bf8ea6b182fdab81af98cc/evidence/review-batch-summary.json) ·
[Exact benchmark runner at `4e57df4`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/4e57df4a4fec747d17bf8ea6b182fdab81af98cc/scripts/check_review_batch.py) ·
[Daily compute estimate and assumptions](capability-pattern-comparison.md#daily-compute-estimate).

The batch timing includes publishing one local JSONL file. Scheduled queue
time is unmeasured. This was one run per mode on a shared VM using a repeated
workload.

## Archived material

The [last working tree at `7bcddbd`](https://github.com/kurtabela06/ARI3217-Contract-Review/tree/7bcddbdf02cf0c5497c619929cbeed0d2dd5675d)
preserves the earlier planning documents. The [short initial benchmark at
`2c4050a`](https://github.com/kurtabela06/ARI3217-Contract-Review/tree/2c4050ac546a5b490bdfa25d4a70117bb7136528/evidence),
[early image checks at `e814e02`](https://github.com/kurtabela06/ARI3217-Contract-Review/tree/e814e0279560166bd17ff1f511a631ce707ed261/evidence)
and [manual SQLite records at `50d3227`](https://github.com/kurtabela06/ARI3217-Contract-Review/tree/50d3227377e08608b4ebf0b9981f47cd9cc4d4f1/evidence)
remain available as separate historical checkpoints. See [ADR 002](decisions/002-notebook-output-policy.md)
for the supplied notebook and its original outputs.
