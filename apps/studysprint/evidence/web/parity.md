# webApp 0.1.1 — parity statement (vs foundation v0.5.0)

Standing requirement (owner, 2026-11-03): every surface iteration ships
demo evidence + a parity statement. Demo evidence = this directory:
today.png · sr-review.png · reader.png — the served PWA rendered
headless (420×900) from the synced tree at the webapp-v0.1.0 release
head (0.1.1 = the RFP-D1-7 award-batch patch line: due-aware SR,
persisted check-ins, advancing Today, all reader sections,
version-stamped service worker); the GitHub Pages deployment of the same tree
(https://timerloggedout-spec.github.io/studysprint/web/, verified live)
is byte-identical.

Rides the foundation (v1.0.0 — the tree's own VERSION, the version that generated the shipped state.json; #4225):
- Core plan + trust receipt + today view, via web/build_data.py running
  the real core → data/state.json (keys: plan · trust_receipt ·
  today · sr · reader · course · surface).
- SR schedulers: FSRS (ts-fsrs formulas over the core export) + SM-2,
  rule-for-rule vs study_sr; scheduler-named receipts; on-device
  persistence.
- Reader sections from the core export (study_reader shapes).

Absent / parity pass pending (honest, per WEBAPP.md):
- study_pipeline — BOUND since foundation v0.5.0 build D:
  the Ingest view runs the one core ingestion path (in-browser
  mirror of the syllabus grammar for text; photographs recorded
  as awaiting core OCR, disclosed as such).
- study_courses (multi-course/countdown/.ics) — state key present;
  full binding pending.
- study_memory (memory methods §1c) — not yet bound.
