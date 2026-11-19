# RD1 capability-pattern comparison

The prototype serves online predictions for lawyer review. The on-demand batch
benchmark sent the same inputs through the same API and published all packs as
one file at the end of the job.

| Criterion | Online review | On-demand batch test |
|---|---|---|
| Latency and throughput | 130.81 ms client p95. The phase took 63.74 s at 31.38 successful reviews/s. Each pack was available as its response arrived, supporting same-session review. | All packs were published together in 63.69 s at 31.40 successful reviews/s. A daily schedule would add the time between intake and job start. |
| Daily running cost | Unmeasured. | Unmeasured. |
| Decision ownership | The lawyer checks the cited highlights against the agreement and decides how to proceed. | The lawyer makes the same decision after batch publication. |
| Failure handling | 0 failures in 2,000 requests. A database write failure returns HTTP 503. The operator investigates and the lawyer can review manually. | 0 failures in 2,000 requests. The runner records failed items for operators to review. A daily schedule and automatic retries were outside the benchmark. |

Both modes repeated the same 40 CUAD inputs 50 times with two workers and the
same fitted bundle, `0.1.0:eef20dbe2aca`. The phases shared a VM with the client.
The batch timing includes writing and publishing the local JSONL file. The
benchmark excludes three warm-up requests, API startup and scheduled queue time.
The two phases had similar throughput in this run.

## Decision

Keep the API for same-session review. I would test tiered delivery if realistic
peak demand pushed online p95 above the measured 130.81 ms reference and delayed
same-session work. I would switch non-urgent overflow to batch delivery only if
the trial restored priority API latency and the queued packs met the agreed
submission-to-ready deadline. That deadline would include the schedule wait.

[Matched benchmark and runner](evidence-index.md#matched-online-and-batch-test)
