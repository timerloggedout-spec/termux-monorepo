# Agent Team Control Plane

The canonical compact architecture chart is [`AGENT-TEAM-CONTROL-PLANE.mmd`](./AGENT-TEAM-CONTROL-PLANE.mmd).

## Why the chart exists

The repository contains many detailed workflows, skills, experiments, telemetry collectors, provider lanes, recovery mechanisms, and historical implementations. This chart is the **orientation layer**: it shows how those mechanisms compose into a continuously improving agent team without pretending that every transition is already operational.

```text
SCOUT
  │
  ├── discover providers/models
  ▼
TEAM CANDIDATES
  │
  ├── OX-ALPHA
  ├── DEEPSEEK
  └── GEMINI / future providers
  │
  ▼
MVT
  │
  └── provider × model × prompt × manager × cohort × sequencing
  │
  ▼
TELEMETRY
  │
  └── SHA → run → job → step → logs → artifacts
  │
  ▼
BILATERAL REVIEW
  ├── RETAIN
  └── CULL / QUARANTINE
  │
  ▼
MONEYBALL / 3L0
  │
  ▼
TEAM ADMISSION
  │
  ▼
SKILL SYNTHESIS
  │
  ▼
BIUDL
  │
  └──────────────────────→ next Scout cycle
```

## Lane ownership

| Lane | Function | Evidence output |
|---|---|---|
| Scout | discover and normalize candidate providers/models | candidate roster |
| Builder | implement smallest useful change | commit/SHA |
| Recon | correlate prior art and context | provenance graph |
| Experiment | run MVT treatments | request/run records |
| Telemetry | collect and reduce runtime evidence | run/job/step/artifact records |
| Review | bilateral critique and regression detection | review disposition |
| MoneyBall | score observed performance | ranking/treatment score |
| Synthesis | promote reusable knowledge | skill/SSOT revision |

## Promotion rule

The system must not equate activity with success. A green workflow, HTTP 200, reviewer acknowledgement, low latency, or large response can be an observation, but **task outcome remains separately classified** as `PASS`, `FAIL`, `UNKNOWN`, or other documented state.

Correctness has priority over latency. Resource/quota state is a capacity signal, not a quality score.

## Dynamic population

OX-Alpha and DeepSeek are current priority admission lanes. They must be treated as selectable candidates with live availability/capability/quota evidence rather than permanent hardcoded winners. Additional providers/models can enter the same population through Scout.

## BIUDL

**Broad integration → focused development lane → thin validated slice → feed-forward synthesis → broaden.**

A thin slice is not the end state. Its useful, verified mechanisms are synthesized back into the broader system, and the next cycle starts with the improved baseline.

## Related systems

- `evidence-led-monorepo-ops`: evidence collection, reduction, disposition, and SHE advancement.
- `review-loop`: repeated review, bilateral critique, regression protection, and skill evolution.
- `adaptive-feedback-cycle`: the repeat-until-desired-outcome execution contract.
- `context-relationship-graph`: temporal/provenance mapping of issues, PRs, commits, runs, agents, and evidence.
- `gemini-performance-psychology`: momentum and feedback-cycle behavior without reward hacking.
- `ACTIONS-METRICS-INTEGRATION.md`: run/job timing reconstruction and telemetry boundaries.
- `SELF-HEALING-ENGINE-ROADMAP.md`: incident observation and recovery orchestration.
