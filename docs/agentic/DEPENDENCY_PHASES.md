# Dependency Phase Status

This file is generated from `docs/agentic/dependency-phases.json` and a normalized evidence snapshot.
Do not edit it as an authority source.

**Plan hash:** `b32550775db0810f9204c2fe16385f03a37fb70b0653dd9e18a77f510657a6b7`

```mermaid
flowchart LR
  DPH_000["DPH-000<br/>Foundation and lifecycle engine<br/>ready"]
  DPH_100["DPH-100<br/>GitHub Projects synchronization<br/>waiting"]
  DPH_200["DPH-200<br/>Idempotent agent dispatch<br/>waiting"]
  DPH_300["DPH-300<br/>Derived timeline and reconciliation<br/>waiting"]
  DPH_000 --> DPH_100
  DPH_100 --> DPH_200
  DPH_200 --> DPH_300
  class DPH_000 ready
  classDef ready fill:#166534,color:#ffffff,stroke:#14532d
  class DPH_100,DPH_200,DPH_300 waiting
  classDef waiting fill:#64748b,color:#ffffff,stroke:#475569
```

| Phase | State | GitHub Project status | Linked PRs | Reason |
|---|---|---|---|---|
| `DPH-000` | **ready** | Todo | — | all prerequisites and current evidence permit a claim |
| `DPH-100` | **waiting** | unmapped | — | waiting on DPH-000 |
| `DPH-200` | **waiting** | unmapped | — | waiting on DPH-100 |
| `DPH-300` | **waiting** | unmapped | — | waiting on DPH-200 |

## Safety boundary

The chart and report are derived views. Phase completion requires a matching merged PR, the configured checks, and a GitHub Project item in `Done`; agent comments, rendered diagrams, and inferred approvals do not satisfy those conditions.
