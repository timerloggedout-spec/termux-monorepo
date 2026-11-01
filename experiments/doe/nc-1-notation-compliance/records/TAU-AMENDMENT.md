# nc-1 — τ amendment (pre-scoring, per DESIGN drift_metric.tau)

`[MUSEai]@{role:{doe-mgr-classifier-tuning}}` · 2026-10-31

- **τ = 0.7472** on prose_ratio (prose tokens ÷ total tokens,
  tokenizer = `scripts/doe/nc1_features.py`).
- Derivation: midpoint of gold-corpus class medians at build time —
  drift median 0.8382 (n=17) · compliant median 0.6562 (n=15) ⇒
  τ = (0.8382 + 0.6562) / 2 = 0.7472. Set BEFORE first scoring;
  never tuned on scored data (any retune = new amendment + new run
  on a fresh window, per DESIGN).
- Scope Δ (main ⇒ doe-expert, 2026-10-31): L3 metric =
  information-density effectiveness (signal ÷ tokens), ¬ style-only.
  Arms unchanged. Evaluator therefore reports density alongside
  prose_ratio for every unit; the drift *detector* of record for
  run-001 remains the pre-registered prose_ratio > τ rule, and any
  density-based detector variant enters only by amendment.
- Detector mode for run-001: Tier-1 L3/L2 builds have NOT landed
  @master (code search prose_ratio/notation_drift = 0 hits,
  2026-10-31) ⇒ arms score with the reference implementation of the
  metric (same tokenizer + τ, surface subsets per arm). When Tier-1
  flag files land, run-002 re-scores with their flags and supersedes
  run-001 numbers with a correction note. Coordination ask sent ⇒
  steward fae834fb (submission 19e7d267) + comment on #2865.
