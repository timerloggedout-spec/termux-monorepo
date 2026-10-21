# HITL Control Plane — Work Items

| ID | Work | Priority | Acceptance |
|---|---|---:|---|
| HITL-01 | Extend OPS-EVENT taxonomy for operational/action/cadence/collaborator events | P0 | schema + fixtures + validator |
| HITL-02 | Add command proposal/approval/effect envelope | P0 | immutable correlation + HITL gate tests |
| HITL-03 | Build SeekLog-backed dashboard replay adapter | P0 | bounded replay, seek, pause, snapshot identity |
| HITL-04 | Context-graph overlay adapter | P0 | verified/candidate separation preserved |
| HITL-05 | GitHub comment/PR context inspector | P0 | exact permalink → context bundle |
| HITL-06 | Command deck | P0 | preview first; no implicit writes |
| HITL-07 | Cadence/sprint event adapter | P1 | replayable sprint timeline |
| HITL-08 | Collaborator synchronization planner | P1 | observed/proposed/confirmed states |
| HITL-09 | MDX/MMD/image projection compiler | P1 | shared snapshot/event-range provenance |
| HITL-10 | Gource parallel renderer | P1 | same event range renders through Gource-compatible log |
| HITL-11 | n8n workflow adapter | P2 | declarative workflow export, no source-of-truth ownership |
| HITL-12 | Owner RBAC/policy integration | P1 | role/policy gates before dispatch |
| HITL-13 | Replay comparison mode | P2 | snapshot A/B with event diff |
| HITL-14 | Audit/reconciliation view | P1 | command → runtime → effect → evidence chain |
