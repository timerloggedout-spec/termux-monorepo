# Workspace Artifact Inventory

This is a **classification record**, not a cleanup instruction. It records the observed `workspace/` estate as of 2026-08-17 so later agents can route a specific request without treating every nested Markdown, text, JSONL, or generated map as live context.

| Metric | Observed value |
|---|---|
| Files under `workspace/` | 897 |
| Largest subtree | `workspace/llm_map/` with 853 files |
| Dominant file types | 532 `.txt`, 190 `.json`, 73 `.py`, 24 `.md`, and 13 `.jsonl` files |
| Last tracked `workspace/llm_map/` change | 2026-08-03 (`03f5a5a`) |
| Other observed workspace subtrees | `maxc`, `cedar_forge`, `compression_sandbox`, and project task-marker folders |

## Classification summary

| Area | ICM role | Universe | Evidence | Maintenance rule |
|---|---|---|---|---|
| `workspace/README.md` | catalog | leftover | It is the master workspace index and routes task trackers/project folders.[1] | Read only to identify an owner; do not use it as application architecture. |
| `workspace/llm_map/README.md` and declared generator scripts | catalog / factory | leftover | The README describes an LLM ecosystem mapper, its generator flow, and declared output files.[2] | Keep any source change in the mapper’s owning workflow; do not rewrite as part of ICM documentation. |
| `workspace/llm_map/*.jsonl`, JSON index files, `SYSTEM_MAP.md`, assembled reports, and package/tool snapshots | product | leftover | The mapper README identifies JSONL and Markdown maps as generated outputs; `SYSTEM_MAP.md` enumerates broad derived paths.[2] [3] | Do not hand-edit, treat as primary evidence, or load wholesale into agent context. Regenerate only through the owner. |
| Older project task notes, backups, and isolated prototypes | leftover | leftover | The root index routes project-specific trackers; subtree history is older than the active ICM integration.[1] | Retain pending a scoped owner decision. Archive/remove only through a separate approved proposal. |
| Runtime/session/account/browser or other sensitive material surfaced by broad maps | excluded | ghost | Broad generated maps can enumerate device/runtime material that is not an ICM source.[3] | Never ingest into ICM cards, copy into docs, or use as cleanup evidence without security review. |

## Triage protocol

For a named path, start at [`../processes/workspace-artifact-triage.md`](../processes/workspace-artifact-triage.md). The path must be classified as catalog/contract, factory, product, leftover, or excluded before a map update, archival, deletion, relocation, or code change is proposed.

> **Scope boundary:** This inventory does not declare any file disposable. It creates the minimum evidence needed to stop accidental context loading and to make a future cleanup reviewable.

## Evidence

[1] [`workspace/README.md:1-9`](../../../workspace/README.md)
[2] [`workspace/llm_map/README.md:1-20`](../../../workspace/llm_map/README.md) and [`workspace/llm_map/README.md:167-176`](../../../workspace/llm_map/README.md)
[3] [`workspace/llm_map/SYSTEM_MAP.md:1-18`](../../../workspace/llm_map/SYSTEM_MAP.md)
