# RD1 data findings

Measured on the CUAD baseline using scripts/check_data_quality.py.
Exact counts are stored in evidence/data-quality-summary.csv.

| Finding | Source | Measured result | Consequence | Safeguard / response |
|---|---|---|---|---|
| Rare categories | Documented | 5 of 41 categories occur in fewer than 30 contracts | Overall averages can conceal weak and uncertain rare-category performance | Retain per-category results; report rare-category performance separately. Not a reason to reject otherwise valid input. |
| Categories absent from contracts | Documented | 14,208 of 20,910 contract-category pairs have no annotation: 67.95% | Evaluation only on present categories overstates practical precision | Evaluation includes absent categories; tests/test_evaluation.py guards this behaviour. Use “not found in highlights”, not “absent”. |
| Clauses cut across passages | Documented | 895 of 13,823 annotated spans have less than 90% coverage in any single passage: 6.47% | A relevant highlight may omit essential clause context | Pipeline rejects a cut share above 7%; tests/test_validation.py checks the boundary and failure cases. |
| Exact duplicate annotations | Additional investigation | 0 excess rows with identical contract ID, category, start and end | Repeated annotation rows could distort annotation-level counts and coverage statistics | Inspection script records the count. No removal or deduplication was necessary. |
| Invalid annotation offsets | Additional defensive check | 0 negative, reversed, empty or out-of-bounds spans | Incorrect positions could invalidate annotation matching and citations | Inspection script fails if invalid offsets are found. This offset check is not yet integrated into normal training. |

## Interpretation

Legitimate overlapping labels are not duplicates.
Near-duplicate contracts are a separate documented issue handled through
contract-family grouping.

No additional defect was found in the duplicate-annotation investigation.
The result must not be presented as a correction to the dataset.

The rare-category count uses fewer than 30 contracts.
The earlier performance analysis used a separate tail definition:
fewer than 60 contracts. Those thresholds must not be confused.

## Evidence reference

Commit: add the commit ID containing the measured evidence after committing.
