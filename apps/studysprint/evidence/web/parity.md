# webApp 0.1.0 — parity statement (vs foundation v0.4.0)

Standing requirement (owner, 2026-11-03): every surface iteration ships
demo evidence + a parity statement. Demo evidence = this directory:
today.png · sr-review.png · reader.png — the served PWA rendered
headless (420×900) from the synced tree at the webapp-v0.1.0 release
head; the GitHub Pages deployment of the same tree
(https://timerloggedout-spec.github.io/studysprint/web/, verified live)
is byte-identical.

Rides the foundation (v0.4.0):
- Core plan + trust receipt + today view, via web/build_data.py running
  the real core → data/state.json (keys: plan · trust_receipt ·
  today · sr · reader · course · surface).
- SR schedulers: FSRS (ts-fsrs formulas over the core export) + SM-2,
  rule-for-rule vs study_sr; scheduler-named receipts; on-device
  persistence.
- Reader sections from the core export (study_reader shapes).

Absent / parity pass pending (honest, per WEBAPP.md):
- study_pipeline (reading pipeline §1b) — not yet bound.
- study_courses (multi-course/countdown/.ics) — state key present;
  full binding pending.
- study_memory (memory methods §1c) — not yet bound.
