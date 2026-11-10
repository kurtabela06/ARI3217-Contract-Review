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
