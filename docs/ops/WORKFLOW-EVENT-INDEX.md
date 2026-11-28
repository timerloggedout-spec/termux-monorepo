# Workflow event index

Snapshot: current master source inventory, 2026-11-28. Current machine-readable artifact schema: `workflow-event-index/v1`; parser output schema: `workflow-event-index/v2`. This index carries all records from the generated automation workflow catalog and reconciles them against the workflow directory.

| Coverage | Count |
|---|---:|
| Workflow YAML files in directory | 333 |
| Generated catalog records | 332 |
| Indexed records (current v1 snapshot) | 332 |
| Directory/catalog drift | 1 |\n| Uncatalogued source writers | 1 |

## Catalog reconciliation gap

`.github/workflows/research-astute-private-repo-provisioner.yml` is present in the live workflow directory and absent from the 332-record generated catalog. The source-derived v2 parser indexes it as a 333rd workflow and reports `DRIFT` until the catalog generator is refreshed.

The current v1 snapshot contains 332 catalog records. The v2 parser will index all 333 directory workflows, report one catalog gap, and list uncatalogued source writers.

## Source-level authority correction

`project-repository-visibility.yml` is classified as `read-only-or-advisory` in the generated catalog. Its source invokes `gh api --method PATCH repos/$TARGET_REPOSITORY -F private=false`, then reads the repository back to verify the visibility change. The index records the source-verified authority as `writer` and preserves the catalog value separately as `catalog_authority` so the mismatch remains auditable. Source blob: `5a42fc64c81632c38ffa892a1a890d685114fcda`.

`research-astute-private-repo-provisioner.yml` is also a source-verified writer: it declares `contents: read` but calls `gh api --method POST /orgs/$ORG_NAME/repos` to create a private repository in the Research-Astute organization. Its path is absent from the generated catalog. Source blob: `2b5c96c951221f3b91508d05bfc07aa2624a2182`.

## Coverage semantics

The v2 index preserves full event configuration, activity types, branch/path/tag/workflow filters, workflow_dispatch inputs, workflow/job permissions, job conditions, dependencies, runners, environments, matrices, concurrency, action references, immutable SHA pins, and source blob SHAs. `scripts/ci/workflow_registry.py` generates the index and detects explicit `gh api` write methods. Authority is inferred from declared permissions plus those write methods; indirect external-token clients remain a source-review requirement. The trusted master refresh writes the enriched 333-record snapshot.

Catalog source fingerprint: `d1fc2a62d098070ccae2d73efe34528bf17d3c3f1245d3137b4ba80ea41b689e`.
Machine-readable index: `docs/ops/generated/workflow-event-index.json`.
