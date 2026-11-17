# ADR 002 — Notebook outputs and reference preservation

Status: accepted.

The supplied notebook's saved outputs are worked reference examples.
They are not measurements from my own investigation.

Keep a byte-for-byte reference backup under Git-ignored data/reference.
Keep the tracked notebook's code and Markdown while clearing outputs
and execution counts before commits.

Run:
python scripts/clear_notebook_outputs.py

Do not commit raw contracts, processed contract text, trained artifacts,
credentials, or screenshots containing contract passages.

Store reviewed aggregate measurements and figures separately as evidence.
Record the code commit, environment and configuration for each experiment.

Clearing current outputs does not remove copies from earlier Git history.
Review history before making the repository public.


## Historical exception identified during repository review — 17 November 2026

The initial public commit `7f27e29a427c909517b0fd319efd1a7c2084b86d` includes
supplied notebook outputs, including example contract passages. The current
reference notebook has zero saved outputs, but clearing it did not remove that
history. These worked examples are not the student's new measured results.

History remediation remains an open policy decision. Rewriting public history
would change commit IDs referenced by evidence; its scope and replacement
references must be planned before any rewrite. The documentation-alignment
change preserves history and records the exception openly. See
`docs/repository-audit-followup.md`.
