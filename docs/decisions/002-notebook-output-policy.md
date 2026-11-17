# ADR 002 — Notebook outputs and history retention

Status: accepted and final.
Decision recorded: 17 November 2026.

## Decision

Retain the existing Git history, including historical supplied notebook
outputs, to preserve provenance and the commit identifiers referenced by
the project's evidence. No history rewrite is planned.

## Rationale and scope

The initial notebook upload contained supplied worked outputs, including
example contract passages. Keeping that historical reference documents
the starting point from which the model was reproduced and packaged.

Running the baseline can produce contract excerpts in notebook outputs.
Saving and committing outputs is a separate action. The initial supplied
examples must not be presented as newly measured student results.

The notebook's Section 10 includes “no data or contract text committed”.
Retaining the historical examples is a deliberate, documented exception
to that instruction. This decision does not assert that Git history
contains no contract text.

## Policy for subsequent work

Keep the tracked notebook's outputs and execution counts cleared before
committing. Preserve the supplied code and Markdown.

Run:
python scripts/clear_notebook_outputs.py

Keep the byte-for-byte reference backup under Git-ignored data/reference.
Exclude newly generated contract passages, raw/processed datasets,
credentials and trained artifacts from commits. Store reviewed aggregate
measurements and figures separately with source and environment references.

Historical outputs remain unchanged; current notebook outputs are cleared.
