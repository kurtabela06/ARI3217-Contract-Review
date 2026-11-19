# ADR 002 — Notebook outputs and history retention

Status: accepted and final. Decision recorded 17 November 2026.

Retain existing Git history, including the supplied worked notebook outputs,
to preserve the starting point and evidence commit identifiers. The notebook’s
Section 10 asks that contract text be excluded from commits. The historical
supplied example passages are a documented exception under this decision.
They are distinct from the student’s recorded baseline measurements.

- [Initial notebook with supplied worked outputs at `7f27e29`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/7f27e29a427c909517b0fd319efd1a7c2084b86d/29_contract_review.ipynb).
- [Cleared reference notebook at `10cc10a`](https://github.com/kurtabela06/ARI3217-Contract-Review/blob/10cc10ad543143bf383344d62280b62a816d254c/29_contract_review.ipynb), used as the source for the baseline.
- [Student baseline evidence at `eb7b2f3`](https://github.com/kurtabela06/ARI3217-Contract-Review/tree/eb7b2f3f4992fdf95209a5cbd4bd96833b3e4e7e/evidence).

The live repository keeps the [thin package client](../../notebooks/contract_review.ipynb).
Clear outputs and execution counts before committing notebook changes. Keep
raw and processed datasets, generated contract excerpts, fitted bundles,
credentials and batch pack files local. Commit measurement summaries and
reviewed figures with their source references.
