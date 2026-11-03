# StudySprint webApp surface

An installable PWA over the StudySprint core — a browser surface
over the SAME core outputs, consuming the core's state shapes
rather than reimplementing them (`web/`).

**Version line: independent.** This surface versions on its own
SemVer line (owner overrule 2026-11-03), separate from the
foundation road {core v0.3.0 ⇒ v0.4.0 ⇒ v1.0.0}. Surface version =
`web/VERSION` — currently **0.1.0** — with its own releases;
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
| Reading pipeline (§1b) | absent | core v0.4.0; web parity pass pending |
| Multi-course / countdown / .ics | absent | core v0.4.0; web parity pass pending |
| Memory methods (x6) | absent | core v0.4.0; web parity pass pending |

## Verification

`tests/test_web_surface.py`: the state builder emits the full core
shape set; the committed `data/state.json` matches the builder's
structure; the bundle is complete (every asset the shell/worker
reference exists); the manifest is installable-shaped; the ≥48px
rule is in the CSS; `app.js` parses (node --check) and contains the
FSRS/SM-2 engines and scheduler-named receipts.
