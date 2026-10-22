# Wingman / Steward Wait Loop

```text
RECON → PLAN / MEASURE → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT
```

## WAIT

WAIT is not completion. Re-read authoritative state at an adaptive cadence. Queued/in-progress states remain unresolved.

## WATCH

Capture current SHA/ref, run/attempt, jobs, steps, timestamps, conclusions, artifacts, and resulting repository state. Preserve failures and cancellations as observations.

## VALIDATE

Run the smallest relevant deterministic check plus repository dual gates when the change reaches their scope.

## RE-FETCH + COMPARE

Re-fetch the current immutable SHA and source revision. Compare expected versus observed paths, status, artifacts, and provenance. Classify the delta before acting again.

## RECORD + REPEAT

Record what was proven, disproven, changed, and remains unproven. Repeat only while measurable progress or new evidence exists.

Terminal states: `success` · `clean no-op` · `blocked` · `approval-required` · `exhausted` · `stagnated`.
