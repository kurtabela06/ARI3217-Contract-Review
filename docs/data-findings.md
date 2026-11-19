# RD1 data findings

The [data quality script](../scripts/check_data_quality.py) measured the
[recorded counts](../evidence/data-quality-summary.csv) on the CUAD baseline.

| Finding | Source / what the notebook says | Measured result | Consequence | Safeguard / response |
|---|---|---|---|---|
| Rare categories | Section 1, quirk 3 / Section 4, Trap 2: five categories occur in fewer than 30 contracts | 5 of 41 categories occur in fewer than 30 contracts | Overall averages can conceal weak and uncertain rare-category performance | Retain per-category results and report rare-category performance separately. This is not a reason to reject otherwise valid input. |
| Categories absent from contracts | Section 1, quirk 2 / Section 4, Trap 3: about 68% of question rows have no span | 14,208 of 20,910 contract-category pairs have no annotation: 67.95% | Evaluation only on present categories overstates practical precision | Evaluation includes absent categories; `tests/test_evaluation.py` guards this behaviour. Say “not found in highlights”, not “absent”. |
| Clauses cut across passages | Section 4, Trap 4: sentence-like chunks cut about 6.5% of clauses under the 90%-coverage rule | 895 of 13,823 annotated spans have less than 90% coverage in any single passage: 6.47% | A relevant highlight may omit essential clause context | Pipeline rejects a cut share above 7%; `tests/test_validation.py` covers the 90%-coverage boundary, excessive cutting and invalid coverage. |
| Exact duplicate annotations | Additional hypothesis: identical annotation rows could inflate counts; not one of the seven listed quirks | 0 excess rows with identical contract ID, category, start and end | Repeated annotation rows could distort annotation-level counts and coverage statistics | Inspection script records the count. No removal or deduplication was necessary. |
| Invalid annotation offsets | Additional defensive check: negative, reversed, empty or out-of-bounds spans would invalidate positions | 0 invalid spans | Incorrect positions could invalidate annotation matching and citations | Inspection script fails on invalid offsets; this check is not yet integrated into normal training. |

## Interpretation

Three supplied issues were measured: rare categories, no-answer cases and
clause cutting. The first two overlap the notebook's data-quirk and trap lists;
clause cutting is Trap 4. This does not claim all seven quirks or all four traps
have been completed.

Exact duplicate annotations were one additional investigation; offset validation
was an additional defensive check. Finding zero is a valid investigation result,
not a discovered defect or dataset correction. Legitimate overlapping labels
are not duplicates. Near-duplicate filings are a separate issue handled through
contract-family grouping.

The rare-category count uses fewer than 30 contracts. Earlier performance
analysis used a separate tail definition, fewer than 60; do not mix thresholds.

A later synthetic API check also exposed trailing-punctuation masking by the
supplied email regex. This limitation is recorded in the README and checked by
`scripts/check_review_api.py`. It is separate from the five counted rows above.

## Evidence reference

[Measured counts at `e4da385`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/e4da385ad3ba487656aa9df156e40b23555d91a2/evidence/data-quality-summary.csv).
The [evidence index](evidence-index.md) links these counts to the other RD1 results.
