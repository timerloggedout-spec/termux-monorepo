# Workflow event index

Snapshot: `feat/trigger-workflow-registry-refresh`, 2026-11-27. This index joins all 331 records in the generated automation workflow catalog with the one YAML workflow present in the live directory but absent from that catalog.

| Coverage | Count |
|---|---:|
| Workflow YAML files in directory | 332 |
| Records from generated catalog | 331 |
| Supplemental source-read records | 1 |
| Total indexed | 332 |

## Catalog gap

`project-repository-visibility.yml` is present in `.github/workflows/` but absent from `docs/ops/generated/automation-workflow-catalog.json` (blob SHA `5a42fc64c81632c38ffa892a1a890d685114fcda`). Its trigger is a `push` to `master` filtered to `ops/requests/project-visibility-public.yaml`; the job validates the authenticated owner, admin permission, target repository identity, and requested public visibility before changing the external repository's visibility and publishing an audit receipt.

## Coverage semantics

For the 331 catalog records, the index carries the generated catalog's event names, schedules, jobs, authority, concurrency text, and action pins. It does not claim per-workflow activity types, branch/path filters, input schemas, permissions, or job-level `if` expressions. The supplemental workflow carries those details only where directly source-read. The next parser pass should enrich these source-level fields and regenerate this index from `.github/workflows/`.

Machine-readable index: `docs/ops/generated/workflow-event-index.json`.
