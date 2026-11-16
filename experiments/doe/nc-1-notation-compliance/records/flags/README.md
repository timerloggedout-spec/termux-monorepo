# nc-1 run-002 — tier-1 flags + reconciliation confirm

Flags: `run-002-tier1-flags.jsonl` — 50 gold-corpus units scored with
`scripts/notation/compliance_scorer.py` AS-BUILT (heuristic v1 +
density amendment; drift = score < 0.40, borderline 0.40–0.55; no
tau re-derivation — the evaluator compares detectors as-built).
Layer := L2 for chat stratum, L3 for github/docs/records.
Counts: drift 16 · borderline 18 · compliant 16. Scratch source
md5 12b115a51528389130e91b8b88de3fd0 (identical bytes).

Reconciliation confirm (tier1-classifiers-steward, 2026-10-31):
element-level `records_density` (leaf signal / leaf elements; keys =
structure, not counted; absent-marker 0, numbers/ids/refs 1, stated
0.25) is the records variant OF RECORD for gold scoring. The
token-side density in the layer-outputs remains the population
diagnostic only, not a competing gold variant. No objection.
