# EPS Concept Templates

These templates are intentionally implementation-neutral. They describe future surfaces without making them authoritative.

## Concept: Evidence Timeline

**Inputs:** EPS events
**Interaction:** time window, entity, source, status
**Output:** linked event sequence
**Authority:** source evidence
**Validation:** every node resolves to event_id + source reference

## Concept: Agent Work Graph

**Inputs:** agent/task/attempt/provider/manager EPS events
**Interaction:** actor, task, handoff, retry, intervention
**Output:** relationship projection
**Authority:** EPS + source evidence
**Validation:** unknown attribution remains unknown

## Concept: Repository Activity Projection

**Inputs:** Git/PR/Actions EPS events
**Renderer:** Gource or future equivalent
**Interaction:** temporal playback, path/actor filters
**Authority:** EPS/source evidence
**Validation:** rendered event count reconciles to projection input

## Concept: Operations Observatory

**Inputs:** validated EPS + derived metrics
**Renderer:** Grafana / SHE / Vercel
**Interaction:** time-series, drill-down, alert → evidence
**Authority:** EPS/source evidence
**Validation:** freshness + provenance + completeness gates

## Concept: Research Observatory

**Inputs:** repository observations, starred/forked/added seeds, provider/model experiments
**Renderer:** Hex / future interactive surface
**Interaction:** cohort, similarity, disposition, experiment comparison
**Authority:** source evidence + frozen snapshots
**Validation:** reproducible snapshot and schema version

## Concept: ML Experiment Loop

**Inputs:** frozen EPS snapshot
**Process:** feature extraction → model → evaluation → derived evidence
**Output:** model/version/result record
**Authority:** source EPS snapshot
**Validation:** deterministic fixture + uncertainty + source IDs

## Design rule

A custom interactive surface is a **projection of EPS**, never an alternative telemetry authority.
