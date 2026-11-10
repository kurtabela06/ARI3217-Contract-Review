# Investigation log

Record observations during the work, not retrospectively.

## Entry template
- Date: 10/11/2026
- Aim: Reproduce the supplied model before refactoring.
- Results: Macro AUPR 0.489, or 0.499 with knowledge support. Recall at 20 highlights: **88.0%** on regular contracts, **53.3%** on franchise agreements. Classifier fitting: **5 seconds**.
- Findings: Rare categories were weaker; excluding absent clauses overstated precision; fixed windows often cut clauses.
- Uncertainty: The passage-split gain wasn’t conclusive. Rare-category estimates had wide intervals.
- Decision: Preserve the supplied model and grouped split; evaluate chronology separately.
- Reflection: That a result can look +ve but be useless.
- AI assistance: Interpretation, workflow guidance, and evidence-export code.
- Next: Additional data investigation, tests, packaging, and uninterrupted runtime measurement.
- Evidence commit: eb7b2f3f4992fdf95209a5cbd4bd96833b3e4e7e
