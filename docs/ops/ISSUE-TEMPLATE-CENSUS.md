# Issue-template census

Source: `.github/ISSUE_TEMPLATE/` on `feat/trigger-workflow-registry-generator`. Snapshot: 2026-11-27.

| Measure | Count |
|---|---:|
| YAML issue templates | 14 |
| Declare `issue-dispatch/v1` blocks | 2 |
| Intake-only (no dispatch block) | 12 |

## Declared dispatch templates

| Template | Labels | Lane | Tier | Route |
|---|---|---|---:|---|
| `game-development-task` | `game-development` | `game-development` | 3 | `game-development-dispatch.yml` |
| `project-task` | `project-task` | `swarm-dispatch` | 3 | `project-task-dispatch.yml` |

## Intake-only templates

- `apk-cross-reference-findings` — `apk-xref`
- `apk-cross-reference` — `apk-xref`
- `bug` — `bug`
- `data-ingestion` — `data-ingestion`
- `delphi-rfp` — `delphi:rfp`
- `egm-review` — `egm-review`
- `proposal` — `proposal`
- `research-provider` — `research`, `research:provider`
- `research-service` — `research`, `research:service`
- `reverse-engineering-taxonomy-record` — `re-taxonomy`
- `reverse-engineering-taxonomy` — `re-taxonomy`
- `target-brief` — `target-brief`

## Interpretation

A declared block records dispatch intent under `issue-dispatch/v1`; the admission workflow remains the execution gate. Intake-only means the template itself carries no dispatch block in this snapshot. Other workflow-specific issue, comment, label, or manual routes may still consume resulting issues.

The census records source blob SHAs and preserves each form's title and labels in the JSON artifact. Re-run the source extraction after template changes.
