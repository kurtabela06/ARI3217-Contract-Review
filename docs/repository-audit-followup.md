# Repository audit follow-up — 17 November 2026

Implementation/evidence checkpoint: `282cf23093d0d5cf9683987e991f2bfc2d6b7e34`.
This document distinguishes measured work, source/documentation changes and
verification still to be done. It does not replace the lecturer's instructions.

## Addressed implementation findings

- Contract-character length is exposed as a histogram for nonblank validated
  submissions and displayed in the provisioned dashboard. The HTTP metric check
  verifies a valid input adds one length observation and a blank input adds none.
- The Python base image is pinned by digest, with version/architecture evidence.
- The original short benchmark is preserved. The extended run contains 2,000
  requests per phase, with zero measured failures and approximately 76/70 seconds
  of sequential/concurrent activity. Its limits are stated; there are 40 unique
  contracts, not 4,000 independent documents.

## Alignment changes in this branch

- README: fresh-checkout installation; CUAD attribution and contract-licensing
  caveat; split/holdout; current image-0.5 build, external volume, Compose startup,
  host-versus-container testing, metrics and evidence instructions.
- Project overview and ADR 001: remove stale claims that completed measurements
  are not yet run. Preserve dated decisions and the supplementary protocol.
- Data findings: explicitly separate notebook expectations from measured counts.
- ADR 003: document the implemented SQLite choice and PostgreSQL workflow
  deviation, without claiming a PostgreSQL deployment or lecturer sign-off.
- Evidence index: connect results, image/model identities, timing scopes and
  historical runs to a stable commit snapshot.
- Dashboard configuration: use green for successes, neutral blue for input
  rejections, and red for recorded server failures. Historical screenshots remain
  original evidence rather than being edited to match the new colours.
- Storage verification: add local SQLite unit tests and a reusable Docker script.
  The Docker script uses temporary containers and a disposable volume, has no
  published ports and does not mount the live review-records volume.

## Open verification/policy work

- [X] Reusable Docker storage check passed on Ubuntu on 17 November 2026.
  All five checks passed; temporary resources were removed. Result:
  `evidence/storage-recheck-summary.json`. Earlier manual evidence is preserved.
- [ ] Verify provisioned dashboard presentation after pulling this branch. No
  model or application image rebuild is needed for dashboard-only changes.
- [X] Historical supplied outputs retained by final decision; see ADR 002.
  The current notebook is cleared, but initial commit
  `7f27e29a427c909517b0fd319efd1a7c2084b86d` retains worked outputs. History
  rewriting would change existing evidence references and needs a deliberate
  migration plan. This branch records the issue and does not rewrite history.

## Remaining RD1 submission work

Four EA layers and responsibilities; quantified capability-pattern comparison
with daily running cost and failure ownership; supported AI Act classification;
at least three reflection prompts and AI-use disclosure; final written PDF,
slides/video and consistency/submission checks. The student's reflection must
state their own reasoning and lessons. The short existing investigation-log
entry is not treated as a finished reflection on the later work.

The full notebook's CI gate, MLflow/registry, knowledge-layer extensions,
contract-type/delayed-label monitoring and local-model GenAI remain wider-project
requirements unless separately completed and evidenced. They must not be marked
complete solely because operational RD1 checks pass.


## Final history decision — 17 November 2026

Retain existing history and evidence commit identifiers. ADR 002 records
the final decision and the exception to the notebook's no-contract-text
instruction. Historical rewrite discussion above records the earlier
audit context; the current decision is to retain history.
