# CNS-12 — Brain BioFeedBack signal trace

**Status:** implementation plan / in progress  
**Work item:** CNS-12 · [Issue #5699](https://github.com/timerloggedout-spec/termux-monorepo/issues/5699)  
**Surface:** `apps/project-pages-hub/brain-ops/`

## Outcome

Add an EEG-inspired, multi-lane event raster to the existing Brain Operations page. Each marker represents an observed GitHub Actions workflow-run event for Brain or MOSAIC. The chart exposes event time, workflow lane, outcome class, duration when available, and source commit identity.

## Scope

- Reuse the page's existing public GitHub Actions API request and two-minute refresh cycle.
- Render a lane per observed Brain/MOSAIC workflow name.
- Plot each run as a discrete timestamp marker; encode success, failure, cancellation, pending, and unknown states with distinct classes.
- Preserve run name, run number, timestamp, duration, and head SHA in marker tooltips.
- Keep the existing workflow list as the accessible link/detail fallback.
- Add a pure JavaScript renderer and deterministic Node-backed regression tests.

## Evidence and interpretation

The chart is a software execution-event visualization. It is an event raster with discrete observations, not a continuous voltage waveform. The existing page's source remains GitHub Actions public workflow-run metadata. Production Brain-stage telemetry, physiological sensor input, model quality, token cost, and task-level outcomes remain separate measurement domains.

## Non-goals

- Brain kernel, MOSAIC, QUE/QDesk, policy, memory, dispatch, or provider-routing changes.
- Physiological EEG acquisition or medical interpretation.
- A new telemetry store, event collector, scheduler, or deployment platform.
- Synthetic production observations or inferred Brain-stage timings.

## Tasks

1. Add a pure event-raster renderer with safe text escaping and explicit empty-state behavior.
2. Wire the renderer to the existing Brain/MOSAIC workflow-run response.
3. Add source and measurement-boundary copy to the page.
4. Test status classes, time ordering, provenance tooltips, escaping, empty inputs, and page wiring.
5. Run focused tests, repository gate, Termux smoke, and exact-head CI.

## Acceptance

- Every chart marker originates from a returned workflow-run record.
- The x-axis is time; each lane names an observed workflow.
- Status, timestamp, duration, and head SHA remain inspectable per event.
- Missing or malformed timestamps yield the explicit empty state.
- The page identifies the source and labels the chart as software-event telemetry.
- Existing workflow metrics and list behavior remain intact.
