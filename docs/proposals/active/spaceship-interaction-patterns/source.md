# Source evidence — Spaceship IDE

**Observed:** 2026-11-23

| Evidence | Observation |
|---|---|
| Fork repository | https://github.com/timerloggedout-spec/spaceship_fork |
| Upstream repository | https://github.com/chuanqisun/spaceship |
| Fork default branch | `master` |
| Fork master SHA | `e567943134da28e337ccab6662e5a11fa4869fed` |
| Upstream master SHA | `e567943134da28e337ccab6662e5a11fa4869fed` |
| License | MIT; LICENSE identifies Copyright (c) 2026 Sun |
| Commit signature | GitHub API reports verified=true |
| Main concept documentation | README.md and extra/illustrations.html |
| Supporting design material | extra/style-1.html…style-4.html, knob-states.html, pointer-1.html…pointer-5.html, tray-1.html…tray-3.html, bar-1.html…bar-3.html, extra/clips/*.gif |
| Fork delta | No independently observed customization delta at the reviewed revision |

## Source-supported concepts

1. Focus Monitor — line-level attention/salience meters respond to the current knob sentence or hovered phrase.
2. Attention Lock — draggable phrase boxes bind key wording to the knob and influence future text.
3. Future Vector Steering — a detachable future knob selects a semantic dimension, value, and strength, then displays fulfillment and pins to delivered text.
4. Realtime Regeneration — a playhead scrubs speculative text; rewinding discards the future and streams an alternative.

The source also includes knob states, pointer variants, trays, bars, style explorations, illustrations, and GIF clips.

## Evidence boundary

The source establishes its own design descriptions and implementation artifacts. It does not establish measured usability, model quality improvements, or performance outcomes for this monorepo. Those remain candidate evaluation questions.

The upstream README describes browser-local storage for user API keys. This behavior remains source-specific; the integration imports no provider credential handling, source code, or media.

The context-relationship index currently excludes `refTemplates/**` and its published manifest reports partial historical coverage. This bounded source recon therefore uses direct GitHub file and repository metadata inspection; graph coverage is not claimed for this source path.
