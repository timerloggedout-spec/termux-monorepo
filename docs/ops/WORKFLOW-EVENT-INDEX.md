# Workflow event index

Snapshot: `feat/trigger-workflow-registry-refresh`, 2026-11-27. This index carries all records from the generated automation workflow catalog and reconciles them against the workflow directory.

| Coverage | Count |
|---|---:|
| Workflow YAML files in directory | 332 |
| Generated catalog records | 332 |
| Indexed records | 332 |
| Directory/catalog drift | 0 |

## Source-level authority correction

`project-repository-visibility.yml` is classified as `read-only-or-advisory` in the generated catalog. Its source invokes `gh api --method PATCH repos/$TARGET_REPOSITORY -F private=false`, then reads the repository back to verify the visibility change. The index records the source-verified authority as `writer` and preserves the catalog value separately as `catalog_authority` so the mismatch remains auditable. Source blob: `5a42fc64c81632c38ffa892a1a890d685114fcda`.

## Coverage semantics

For all catalog records, the index carries event names, schedules, jobs, authority, concurrency text, and action pins. It does not claim per-workflow activity types, branch/path filters, input schemas, permissions, or job-level `if` expressions. The source-level exemplar census captures those details for selected workflows; the next parser pass should enrich the remaining source-level fields.

Catalog source fingerprint: `d1fc2a62d098070ccae2d73efe34528bf17d3c3f1245d3137b4ba80ea41b689e`.
Machine-readable index: `docs/ops/generated/workflow-event-index.json`.
