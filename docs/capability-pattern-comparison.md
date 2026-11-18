# RD1 capability-pattern comparison

The implemented pattern is online, human-in-the-loop review. A lawyer submits
a contract and receives cited highlights in the same session. The alternative
is a proposed daily batch that uses the same extractor and review budget, then
makes the results available to lawyers after the scheduled run.

| Criterion | Online review | Scheduled batch review |
|---|---|---|
| Latency budget | Proposed target: client p95 of 1 second for a successful API response. Measured p95 was 96.10 ms sequentially and 142.92 ms at concurrency two, with zero failures across 4,000 requests in the extended local test. | Proposed target: results ready within 24 hours and 15 minutes of submission at p95. A document submitted just after cutoff can wait nearly 24 hours before the next run begins. Batch turnaround has yet to be measured. |
| Estimated compute cost per calendar day | At an illustrative €0.05 per VM-hour, 24-hour availability costs €1.20/day. | At the same rate, a VM billed for 15 minutes per daily run costs about €0.013/day in compute. Budget separately for durable intake, storage and monitoring. |
| Decision ownership | The lawyer uses the highlights alongside the original contract and decides how to proceed. Legal operations sets review policy. | The same roles apply. The schedule determines when the results are ready. |
| Failure handling | A failed database write returns HTTP 503. The operator investigates, and the lawyer can proceed with manual review if the matter is time-sensitive. | The proposed batch design would retain failed jobs for retry, alert the operator after a missed run and route time-sensitive contracts to manual review. |

The compute comparison assumes an always-on VM for online service and a VM
billed only during the batch window, including startup. It excludes shared
storage, monitoring, support and lawyer time. The notebook estimates
30 minutes of lawyer time per contract at a 20-passage budget and about
€4,000/month at 40 contracts per month. Both patterns use the same budget,
so this comparison credits neither with a labour saving.

## Recommendation and switch criterion

Keep online review while lawyers need highlights in the same session. The
measured 142.92 ms p95 at concurrency two fits the proposed 1-second API
budget under the tested VM conditions.

Switch the non-urgent workload to daily batch if legal operations accepts
next-run turnaround and a pilot measures submission-to-ready p95 at or below
24 hours and 15 minutes, with lower total daily operating cost after accounting
for intake, storage, monitoring and retries. Keep the online route for
same-session requests.

## Evidence

- [Extended local workload](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/282cf23093d0d5cf9683987e991f2bfc2d6b7e34/evidence/review-sustained-load-summary.json)
- [Operating point and lawyer-time estimate](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/282cf23093d0d5cf9683987e991f2bfc2d6b7e34/evidence/baseline-operating-point-results.csv)
- [Storage failure recheck](../evidence/storage-recheck-summary.json)
