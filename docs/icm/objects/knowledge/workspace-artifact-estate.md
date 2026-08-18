# Workspace Artifact Estate

| Field | Value |
|---|---|
| Type | object |
| Cluster | knowledge |
| Universe | leftover |
| Status | verified |
| Entity | The mixed historical and generated-material estate under `workspace/` |

## What this is

`workspace/` is **not** a single runtime subsystem. Its root index routes task trackers and several project folders, while `workspace/llm_map/` contains an LLM ecosystem mapper with generators, source indices, reports, and package/tool snapshots.[1] [2] The estate must be classified before it is read, edited, promoted into the ICM map, or treated as evidence.

## Classification boundary

| ICM role | Typical workspace material | Treatment |
|---|---|---|
| catalog / contract | `workspace/README.md`, a current project README, or explicit task tracker | Read only to route to the owning project. Keep its scope small. |
| factory | Current map-generator scripts and declared build configuration | Maintain only through the owning project and governed code workflow. |
| product | JSON/JSONL indexes, generated maps, package/tool snapshots, and assembled text reports | Treat as derived output. Do not hand-edit or use as a primary source. |
| leftover | Old prototypes, backups, duplicate maps, and historical task notes | Keep out of default context; classify, archive, or remove only through a separately approved cleanup change. |
| excluded | Credential, browser/session, account, or device-runtime artifacts visible in maps | Never load into ICM context or promote into a card. Escalate under security/change-control policy. |

## Read when

Open this card when a request mentions nested `workspace/` Markdown, text, JSONL, generated maps, backups, or stale artifacts.

## First-order impact

**Hits:** the workspace source inventory, the relevant owned project, and the map-maintenance pipeline.
**Does not hit:** application code, device state, generated indexes, or cleanup policy automatically. Those require a separate owner and approved work item.

## Evidence

[1] [`workspace/README.md:1-9`](../../../../workspace/README.md) is the master workspace index.
[2] [`workspace/llm_map/README.md:1-20`](../../../../workspace/llm_map/README.md) defines the mapper, its generated inputs, and its derived outputs.
[3] [`workspace/llm_map/SYSTEM_MAP.md:1-18`](../../../../workspace/llm_map/SYSTEM_MAP.md) is a broad generated catalogue and must not be treated as a canonical source.
[4] [`docs/icm/_meta/workspace-artifact-inventory.md`](../../_meta/workspace-artifact-inventory.md) records the bounded classification summary and triage boundary.
