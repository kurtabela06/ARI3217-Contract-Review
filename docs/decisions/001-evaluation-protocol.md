# ADR 001 — Baseline and supplementary temporal evaluation

Status: accepted plan; experiments not yet run.

## Context

The task notebook prescribes a contract-family grouped split and a
separate franchise holdout. The diary also requests forward-time evaluation.

## Primary protocol

Reproduce the notebook's supplied split, preprocessing, learner and
reference metrics. Preserve the separate franchise holdout.
Do not tune the model or select operating settings using test results.

## Supplementary protocol

Run an additional earlier-to-later filing-year experiment:
- Inspect date coverage, families and category counts first.
- Record temporal boundaries before measuring performance.
- Train on earlier filings, calibrate on an intermediate period,
  and evaluate on later filings.
- Prevent contract-family overlap between partitions.
- Exclude and count unknown-year and boundary-crossing families.
- Keep franchise agreements separate from this regular temporal split.
- Reuse the supplied learner and preprocessing.
- Fit learned transformations only on the relevant training partition.
- Keep test results out of operating-point selection.
- Report these results separately from baseline reproduction.

## Limitations

Filing year is derived from titles, not a reliable contract creation date.
This is a filing-year robustness experiment, not a complete simulation
of future deployment.

The notebook's existing earlier/later test-set comparison is not
forward-time training and evaluation.

If date coverage or category support is inadequate, report the evidence
and limitation rather than claim successful temporal validation.

## Alternatives rejected

Replacing the primary split prevents direct baseline reproduction.
Ignoring time-based evaluation leaves the diary instruction unaddressed.

## Evidence pending

Year coverage, exclusion counts, partition counts, category support,
metrics, runtime and commit references.
