---
type: object
cluster: knowledge
universe: live
status: initiated
entity: https://deepwiki.com/timerloggedout-spec/termux-monorepo
verified_at: 2026-11-01
---

# DeepWiki.com Index (Public Repo Wiki)

DeepWiki.com maintains a generated wiki for this repository — 11 topics and 32 subpages at first harvest (2026-11-01) — readable without any credential through its public MCP server (`https://mcp.deepwiki.com/mcp`: `read_wiki_structure`, `read_wiki_contents`, `ask_question`). This card is the ICM routing entry for that external surface.

## Provenance rules (load-bearing)

- `source_surface: DeepWiki.com`. The wiki is **generated from an index snapshot, not from HEAD** — its claims are external evidence, never a source of truth. Repo source wins over wiki content, always.
- Harvests land in [`_meta/deepwiki-import-record.md`](../../_meta/deepwiki-import-record.md) as dated, additive sections with per-unit provenance (`retrieved_at`, `tool`, `evidence_class: generated-external`).
- Refresh is event-driven (manager assignment, major map change, or a staleness flag past 30 days) — there is no polling of this surface.
- Structure only is imported. Page contents, Q&A answers, diagrams, and any credential-related claims are not imported.

## Boundary

DeepWiki.com (this card) and DEVINdeepWiki (the org branch-level wiki behind the Devin API) are **distinct surfaces** with distinct material and interfaces; their records are never blended. Nothing from DEVINdeepWiki is imported here.

## Read when

- Looking for a generated overview of a repo subsystem before reading its source.
- Checking what the public wiki currently covers, or when it was last harvested.
- Routing a "what does DeepWiki say about X" question to the right surface.

## See

- Import record: [`docs/icm/_meta/deepwiki-import-record.md`](../../_meta/deepwiki-import-record.md)
- Surface: [deepwiki.com/timerloggedout-spec/termux-monorepo](https://deepwiki.com/timerloggedout-spec/termux-monorepo)
- Fabric manifest builder: [`scripts/agentic/build_knowledge_fabric_manifest.py`](../../../../scripts/agentic/build_knowledge_fabric_manifest.py)
