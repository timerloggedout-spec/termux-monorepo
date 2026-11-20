---
type: object
cluster: operations
universe: live
status: verified
entity: archwiz/TOOL_INDEX.md
verified_at: 2026-08-17
---

# ArchWiz

**ArchWiz** is the monorepo’s operational cockpit and tool catalog for automation, forensics, verification, knowledge retrieval, and ecosystem maintenance.

## Why this shape

The monorepo keeps its operational surface in specialized tools rather than one generic runner. The catalog groups the tools by the editing question they answer, letting an agent load the relevant category instead of unrelated operational code.

## Shape

- Cockpit and pipeline tools provide dashboard, listener, review, and failure-monitoring functions.
- Forensic and version-control tools trace provenance and restore versions.
- Autonomous, verification, knowledge, and maintenance tools provide separate execution, checks, retrieval, and upkeep surfaces.

Citations: `archwiz/TOOL_INDEX.md:1-42`.

## Connected to

- **owns:** the canonical high-level catalog of ArchWiz operational tool roles.
- **owned-by:** `archwiz/` and its documented tool/index sources.
- **joins:** repository changes to validation, provenance, task execution, and knowledge indices.
- **looks-like-but-is-not:** a replacement for the governed branch and human-review process.

## If you change this

- **Hits:** the named tool’s source, its direct tests or probes, its documentation entry, and any index or data-flow contract it explicitly writes.
- **Does not hit:** every ArchWiz tool in the same catalog category; inspect direct references before widening scope.

## Surfaces

| Surface | Role |
|---|---|
| Developer or agent | Selects a bounded operational tool for the task. |
| ArchWiz source | Implements the selected operational behavior. |
| Validation tools | Check file, syntax, import, test, or hygiene conditions. |
| Documentation indices | Route later users to the appropriate tool. |

## See

- Source: [`archwiz/TOOL_INDEX.md`](../../../../archwiz/TOOL_INDEX.md)
