# StudySprint TUI surface

A Textual terminal app over the StudySprint core — the same core
functions the CLI calls, no forked logic (`tui.py`).

**Version line: independent.** This surface versions on its own
SemVer line (owner overrule 2026-11-03), separate from the
foundation road {core v0.3.0 ⇒ v0.4.0 ⇒ v1.0.0}. Surface version =
`TUI_VERSION` in `tui.py` — currently **0.1.1** — with its own
releases.

## Install + run (one line)

Copy-paste install — clone, dependencies, launch:

```
git clone https://github.com/timerloggedout-spec/studysprint.git && cd studysprint && pip install textual fsrs genanki && python3 tui.py
```

(Verified verbatim from a clean environment 2026-11-03: fresh clone
→ deps → the TUI boots to the Today screen. Already cloned? Just
`pip install textual fsrs genanki && python3 tui.py` from the repo
root.)

Screens (tabs): **Today** (today's sessions + one-tap check-in) ·
**Plan / Receipt** (the plan and the trust receipt — evidence one
tap away from everywhere) · **Reader** (RSVP, one word at a time,
start/step/play/rewind) · **SR Review** (flip, grade 1–4, FSRS
default or SM-2, scheduler-named receipt after every grade) ·
**Export** (Anki .apkg, Obsidian vault surface).

## Feature-parity checklist vs CLI core

| Core capability | TUI | Notes |
|---|---|---|
| Study plan | present | Plan / Receipt tab, from `build_study_plan` |
| Trust receipt | present | Plan / Receipt tab, from `format_trust_receipt` |
| Today view | present | Today tab, from `render_today_view` |
| Daily check-in | present | Today tab buttons → `record_daily_checkin` |
| Reader (RSVP) | present | Reader tab over `RSVPReader` |
| SR cards + review | present | SR Review tab → `review_card` (FSRS default, SM-2 selectable) + Leitner boxes via `leitner_review`; receipts name the scheduler |
| .apkg export | present | Export tab → `export_apkg` |
| Obsidian vault export | present | Export tab → `export_obsidian_vault` |
| Reading pipeline (§1b) | absent | core module ships in the CLI; not yet surfaced in the TUI |
| Multi-course / countdown / .ics | bound (0.4.0) | Courses tab over the real core intake; per-course check-in logs; .ics file export; create-a-course form |
| Memory methods (§1c) | present | Memory tab runs the real core: `walk_review` scoring · `explain_back` vs the section text · `retrievability_notifications` over the surface's own FSRS states · Leitner rotation in SR via `leitner_review` · `interleave_sessions` in the Plan pane (iteration 2) |
| Calendar awareness (§1d) | present | Calendar tab → `surface_calendar_geo` (intake · briefings · frequency · quiet hours), assembled live |
| Geography (§1d) | present | Routes tab → locations · assessment routes · temple route + audio cues |

## Verification

- Pilot tests: `tests/test_tui.py` (headless Textual pilot:
  check-in, SR flip+grade receipts for both schedulers, reader
  stepping, both exports on disk).
- Recorded run: `evidence/tui/01-today.svg`,
  `evidence/tui/02-sr-review.svg` (Textual screenshot exports of a
  live pilot session: Today screen; SR review after a grade, with
  the scheduler-named receipt visible).

## Release gates (standing requirement, owner 2026-11-03)

Every iteration of this surface ships only when ALL hold:
- Demo evidence present: screenshots/screen-recording of the demo in
  `evidence/<surface>/` in-tree at the release tag.
- Device frames land header-cropped, always: the status/notification
  band is cropped before any device capture is committed, and frames
  are swept for other PII (notification content, names, account
  hints) before they land.
- Parity statement present: what this surface rides vs the foundation
  version it ships against, and what is honestly absent/pending.
- Tests green for the surface + no foundation regressions.
- **Parity table in every release body (owner rule, 2026-11-03):** from
  v1.0.0 onward, every release of record for this surface carries the
  current surface×core parity table (`evidence/PARITY-MATRIX.md`,
  embedded verbatim from the cut tag by the studysprint repo's
  release-cut machinery). A cut from a pre-matrix tag falls back to a
  named versions-of-record line. Patch cuts included.
