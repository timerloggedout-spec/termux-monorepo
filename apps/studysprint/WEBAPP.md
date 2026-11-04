# StudySprint webApp surface

An installable PWA over the StudySprint core — a browser surface
over the SAME core outputs, consuming the core's state shapes
rather than reimplementing them (`web/`).

**Version line: independent.** This surface versions on its own
SemVer line (owner overrule 2026-11-03), separate from the
foundation road {core v0.3.0 ⇒ v0.4.0 ⇒ v1.0.0}. Surface version =
`web/VERSION` — currently **0.1.1** — with its own releases;
deployable bundles attach to the surface's own release.

## How it works

- `build_data.py` runs the real core (plan, trust receipt, today
  view, SR cards + the ts-fsrs UX-state export, reader sections)
  over the bundled example course and writes `data/state.json`.
  Re-run it whenever the core or the course changes.
- `index.html` + `app.js` render the state: **Today** (sessions +
  check-in), **Plan / Receipt**, **Reader** (RSVP), **SR Review**.
- SR review runs in the browser over the core's ts-fsrs UX-state
  export: the FSRS path is the ts-fsrs formula set (FSRS-5 default
  weights); SM-2 is the core baseline ported rule-for-rule.
  Receipts name the scheduler; review state persists on-device
  (localStorage).
- Installable + offline: `manifest.webmanifest` + `sw.js`
  (cache-first app shell). All interactive targets are ≥ 48px
  (FEATURES UX principles).

## Serve

Any static host serves the bundle as-is, e.g.
`python3 -m http.server -d web/`. On the studysprint repo sync,
the bundle serves from the project's Pages site.

## Feature-parity checklist vs CLI core

| Core capability | webApp | Notes |
|---|---|---|
| Study plan + trust receipt | present | Plan / Receipt view, core-generated state |
| Today view / daily check-in | present | Today view; check-ins register on-device |
| Reader (RSVP) | present | Reader view over core-built sections |
| SR cards + review | present | FSRS (ts-fsrs formulas over the core UX export) + SM-2, scheduler-named receipts |
| .apkg / vault export | absent | export stays a CLI/TUI surface in this version |
| Reading pipeline (§1b) | bound (0.5.0) | Ingest view runs the one core ingestion path (in-browser grammar for text; photographs recorded as awaiting core OCR — the browser cannot run tesseract, the named platform limit); the demonstration book (Darwin, Origin of Species 6th ed., Ch. XIV + its own Glossary + Index) rides the build-time bundle: ingest receipt counts (62 terms mined · 62 with definitions · 2 with index refs), term expansion in the Reader (core-emphasized segments, tap → the core's tap payload), hypothes.is annotations view (W3C model; API sync needs an account token, not configured) |
| State recall + stress hardening (§1d) | bound (0.5.0) | Hardening view: opt-in only (per-device flag, off by default), ceilings verbatim from the core; varied-context plan + reinstatement script + SIT drill plans (seeded pressure picks) as browser ports battery-pinned to study_hardening; results record answered + 'not yet' with the supportive close — no score/penalty fields exist |
| Multi-course / countdown / .ics | bound (0.4.0) | header switcher + countdown; per-course storage keys; .ics download; create-a-course in Ingest (ports battery-pinned to the core) |
| Memory methods (§1c) | present | Memory view: palace walk (iteration-1 temple route) scored by the core's ordered-recall rule · Feynman explain-back graded on key-term coverage of the verified section text (abstain/escalate named) · retrievability reminders at R ≤ 0.9 with one-tap grades · Leitner boxes selectable in SR · interleaved session in the Plan view — browser ports of the core scorers, battery-pinned (iteration 2) |
| Calendar awareness (§1d) | present | Calendar view over the core assembler (build-time state, as the bundle's other state) |
| Geography (§1d) | present | Routes view — locations · assessment routes · temple route + audio cues (build-time state) |

## Verification

`tests/test_web_surface.py`: the state builder emits the full core
shape set; the committed `data/state.json` matches the builder's
structure; the bundle is complete (every asset the shell/worker
reference exists); the manifest is installable-shaped; the ≥48px
rule is in the CSS; `app.js` parses (node --check) and contains the
FSRS/SM-2 engines and scheduler-named receipts.

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
