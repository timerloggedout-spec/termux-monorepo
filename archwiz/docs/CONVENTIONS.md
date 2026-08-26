---
title: "🪄 ArchW1z Conventions"
tags: [conventions, architecture, pipeline, promotion]
date: 2026-07-18
---

Canonical rules for the self‑bootstrapping Termux ecosystem.
Adapted from **Model Workspace Protocol (MWP)** by Jake Van Clief.

---

## Five‑Layer Context Architecture

Agents (LLMs, TUI, router) read down the layers and stop when they have enough context.

| Layer | Purpose | Our Implementation |
|-------|---------|--------------------|
| 0 – Orientation | "Where am I?" | `CAVEMAN_INDEX.md`, `_Entry+ReadMe.md` |
| 1 – Routing | "Where do I go?" | `SYSTEM_MAP.md` (llm_map), `ARCHITECTURE_OVERVIEW.md` |
| 2 – Stage Contracts | "What do I do?" | Pipeline docs, tool `--help`, `PIPELINE.md` |
| 3 – Reference Material | "What rules apply?" | This document, `DATA_STORES.md`, `FORGE_OVERSIGHT.md`, `GRIMOIRE_DICTIONARY.md` |
| 4 – Working Artifacts | "What am I working with?" | Session store, export dirs, provenance, run history |

No agent loads everything.  The context builder selects only what's relevant for the current session or file.

---

## Pattern 1: Stage Contracts

Every change follows the **Time Loop Accelerator** (Fork → ForeSight → Generate → Validate → Promote → Index).
Each stage has:
- **Inputs** – files, session context, dependency graph
- **Process** – the tool(s) that execute the stage
- **Outputs** – backups, verdicts, log entries

No file is modified without a timestamped backup and a log entry in `master_tasks.json`.

---

## Pattern 2: Output Folders as Handoffs

Stages communicate through files on disk, not memory:
- Stage N writes to `synthegration_exports/{sid}/session.json`
- Stage N+1 reads that file
- A human can edit the file between stages; the next stage picks up the changes

This is the **pipe‑and‑filter** pattern applied to LLM pipelines.

---

## Pattern 3: One‑Way References (DAG)

The dependency graph (`file_graph.json`) is a **directed acyclic graph**.
If file A imports file B, file B does not import file A.
All indices (`func_index.jsonl`, `ast_snippets.json`) respect this constraint.

---

## Pattern 4: Selective Section Routing (Context Scoping)

The `context_graph_builder.py` loads only the files relevant to a session or query:

1. Session → provenance → files touched
2. File graph → dependency neighborhood (k‑hop)
3. Token Jaccard → structurally similar files
4. Session store → chat messages + code blocks

No prompt receives the entire ecosystem.  See [[CONTEXT_SCOPING]].

---

## Pattern 5: Canonical Sources

Every data store has **one authoritative location**.  All tools read from that location and never duplicate.

| Data | Canonical Source |
|------|------------------|
| File‑session mapping | `comprehensive_provenance.json` |
| Code block hashes | `pointer_index.json` / `codex_index.json` |
| Function signatures | `func_index.jsonl` |
| Dependency graph | `file_graph.json` |
| True versions | `true_versions.json` |
| Run verdicts | `run_history.jsonl` |

Duplication is a bug.  Pointers are the fix.

---

## Pattern 6: Documentation as Routing

`CONTEXT.md` files (like this one) answer **what** and **where**, not **how**.
Implementation details live in tool‑specific files ([[TOOLS_INDEX]], [[DATA_STORES]]).

---

## Pattern 7: Tool Prerequisites (Termux‑Native)

All tools are installed via `pkg` or `pip`.  No external servers required.
Setup guides live in `workspace/llm_map/README.md` and individual project directories.

---

## Pattern 8: One‑Shot Setup

`CAVEMAN_INDEX.md` is the **single entry point** for any LLM or new contributor.
It answers every orientation question in one file, then points to deeper docs via `[[wikilinks]]`.

---

## Pattern 9: Bundled Skills (Utility Belt)

`harmony_hub/utility_belt/` contains standalone scripts that work without dependencies.
Each script is self‑contained and documented in its header.

---

## Pattern 10: Specs Are Contracts (Impact Oracle)

Before promotion, `impact_oracle.py` assesses:
- **Shockwave Index** – how many files are affected?
- **Nexus Rank** – how critical are the affected files?
- **Forged Stability** – how reliable is the change?

The oracle reports risk; it does not prescribe fixes.

---

## Pattern 11: Checkpoints (Validate Stage)

No file is promoted without a **PASS verdict** in `run_history.jsonl`.
The validate stage is a hard gate — no exceptions.

---

## Pattern 12: Audits (Forensic Toolchain)

`forensic_toolchain.py` runs post‑change audits:
- `correlation_scout` – cross‑references all indices for a file
- `similarity_scan` – finds similar code blocks across sessions
- `fragment_match` – locates specific functions in history

---

## Pattern 13: Value Validation (Promotion Criteria)

`validate_promotion.py` checks:
1. Session‑matched PASS verdict exists
2. Timestamped backup created
3. Entry in `master_tasks.json` logged

If any check fails, promotion is **blocked**.

---

## Pattern 14: Docs Over Outputs (True Versions)

`true_versions.json` is the **canonical record** of known‑good file states.
`restore_version.py` reads from it, never from raw session exports.
Early outputs are never used as templates.

---

## Pattern 15: Shared Constants

`bloat_exclusions.lst` is the **single source of truth** for directories and patterns to exclude from indexing.
All mappers (`build_final_all_profile.py`, `comprehensive_fast.py`) read from it.

---

## Quick Reference

| Need | Tool |
|------|------|
| File lifecycle | `archaeo [file]` |
| Impact check | `oracle [file]` |
| Promote change | `promote` |
| Session context | `context_graph_builder.py --session [id]` |
| Code block origin | `forensic_toolchain.py scout [file]` |
| Similarity check | `forensic_toolchain.py similar [text]` |
| Restore file | `restore_version.py [file]` |
| Orphan commands | `find_orphan_commands.py` |

---

*Adapted from [Model Workspace Protocol](https://github.com/RinDig/Content-Agent-Routing-Promptbase) (Van Clief, 2026).*
