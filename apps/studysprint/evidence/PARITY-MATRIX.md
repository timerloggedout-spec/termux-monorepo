# Surface × core feature-parity matrix (iteration 1 of #4282)

Ground truth: the shipped bindings, read from the surfaces'
own builders (`web/build_data.py`, `tui.py: build_state`, the
APK bundle = the web bundle) at core **v0.5.0** + surface line
**0.3.0**. This matrix is the catch-up program's baseline;
every iteration updates it and the per-surface parity
statements together (standing surface gates). Legend:
**bound** = the surface runs the real core path ·
**partial** = a named subset, with the gap stated ·
**absent** = not on the surface.

| Core capability (FEATURES.md) | CLI/core | webApp 0.3.0 | TUI 0.3.0 | APK 0.3.0 |
|---|---|---|---|---|
| §1/§2 Plan + trust receipt + Today (§2/§3) | bound | bound | bound | bound (build-time state, disclosed) |
| §3 Daily check-in + no-guilt shift | bound | bound (persisted; surface-level shift, core reflow not bound) | bound (persisted; real week/day identity) | as webApp |
| §3 SR review — FSRS + SM-2, receipts | bound | bound (browser engines over the core UX export) | bound (real `review_card`) | as webApp |
| SR exports — Anki .apkg · Obsidian vault | bound | absent | bound (Export tab) | absent |
| §1/§3 Reader (sections + RSVP) | bound | bound (all 6 sections, 0.1.1) | bound | as webApp |
| §1 Intake — syllabus/textbook ingestion | bound | bound (in-browser grammar; photos = awaiting-core-ocr, disclosed) | bound (real `ingest_any`, confirm-gated) | bound (native file chooser + camera wiring) |
| §1b Reading pipeline — finder · OCR · structure · term bank | bound | partial (structure/term bank ride ingestion; finder + OCR + hypothes.is not bound) | partial (same, via the core path; OCR seam unwired) | partial (as webApp) |
| §1c Multi-course + exam countdowns + .ics export | bound | absent (single bundled course) | absent | absent |
| §1c Memory methods — loci/palace · Feynman · retrievability notifications · interleaving · Leitner | bound | bound (Memory view: palace walk over iteration 1's temple route · Feynman pane · retrievability list with one-tap grades · Leitner in SR · interleaved plan — browser ports battery-pinned to the core) | bound (Memory tab runs the real core functions; Leitner via `leitner_review`; interleave in the Plan pane) | as webApp |
| §1d Calendar awareness — intake · frequency ramps · shift briefings · quiet hours | bound | bound (build-time state, disclosed) | bound (Calendar pane, live-assembled) | as webApp |
| §1d Geography — locations · routes · temple routes | bound | bound (build-time state, disclosed) | bound (Routes pane, live-assembled) | as webApp |
| §1d State recall + stress hardening (OPT-IN, ceilings in FEATURES §1d) | bound | absent | absent | absent |

## Catch-up slate (per surface line; D1 verifies each iteration)

- **Iteration 1 → surfaces 0.2.0** — §1d calendar + geography: **LANDED** (this update; #4414) —
  builders emit the calendar briefing (ramps · shift notices ·
  quiet hours) and locations/routes incl. the temple route;
  webApp gains Calendar + Routes views; the TUI gains panes;
  the APK follows the bundle.
- **Iteration 2 → surfaces 0.3.0** — §1c memory methods: **LANDED**
  (this update; #4415) — palace walk (over Iteration 1's temple
  route) · Feynman dialogue pane · retrievability notification
  list · Leitner rotation in SR · interleaving in the plan view.
- **Iteration 3 → surfaces 0.4.0** — §1c multi-course:
  course switcher with per-course state · countdown banner ·
  .ics export (download on web, file on TUI).
- **Iteration 4 → surfaces 0.5.0** — §1d hardening (opt-in
  surface only, FEATURES ceilings copied verbatim, no-guilt by
  construction) + §1b completion (hypothes.is annotations view;
  the OCR seam wired where the platform allows).

Each iteration: the matrix + all three parity statements
updated in the same PR, demo evidence refreshed (web headless
captures · TUI pilot SVGs · APK emulator screenshots from the
#4283 harness).

Producer of record for the program: Swarm Optimizations &
Implementation Assurance seat, session
6628d41d-9519-4881-9063-3afe501df815 (claim #4282 comment
6604280926).
