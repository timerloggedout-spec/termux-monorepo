---
title: "🎯 Context Scoping — Role‑Optimised LLM Prompts"
tags: [context, scoping, tokens, llm, prompt-engineering]
date: 2026-07-18
---

## What is Context Scoping?

Context scoping is the **selective assembly of files, code blocks, and conversation messages**
into a single JSON payload that can be injected into any LLM prompt.
It answers the question: *“Given a session or file, what is the minimum set of information
the model needs to continue the work, and nothing more?”*

This follows **ICM Pattern 4: Selective Section Routing** — an agent loads only the
files and sections required for its current task, avoiding token bloat.

## How it Works

The pipeline is orchestrated by [[TOOLS_INDEX|`context_graph_builder.py`]]:

1. **Session → files** — `provenance_api.search(session_id)` returns every file
   touched in that session.
2. **Dependency expansion** — the file dependency graph (`file_graph.json`) adds
   direct imports and dependents (k‑hop neighbourhood).
3. **Token similarity** — for each file, the top‑N most similar files (via Jaccard
   similarity on the first 3000 characters) are added.  This catches structurally
   related code that AST hashes miss.
4. **Chat context** — the last N messages from the session store, including
   `thinking_content`, are attached if the `--chat` flag is used.
5. **Code blocks** — Markdown‑fenced code blocks, `cat > file << 'EOF'` patterns,
   and executable commands are extracted from the session messages.
6. **Output** — a JSON context pack with `files`, `dependency_neighborhood`,
   `similar_files`, `timelines`, `chat_context`, and `code_blocks`.

## Underlying Matrices

Three pre‑computed tensors support fast graph‑based expansion:

| Matrix | Source | Use |
|--------|--------|-----|
| File dependency adjacency | `archwiz/graph_tensors/file_deps_adj.npz` | k‑hop import/dependent expansion |
| AST snippet similarity | `archwiz/graph_tensors/ast_sim_matrix.npz` | Clone detection (threshold > 0.8) |
| Token Jaccard (on‑the‑fly) | `context_graph_builder.py` | Soft structural similarity |

> **Why token Jaccard and not AST similarity alone?**
> Two files can share zero identical AST snippets yet be closely related
> (e.g., `core.py` and `cli.py`).  Token‑level similarity captures shared
> imports, naming conventions, and coding style — a broader signal that
> leads to better context expansion.

## Integration Points

- **`deepcli send`** — a future `deepcli context {sid}` command will load the
  pre‑built context pack and inject it into the prompt.
- **TUI** — when opening a session, the dashboard can offer a one‑key
  “send context to LLM” action.
- **Dispatch hook** — `dispatch_pipeline.update_all()` can pre‑build a
  context pack for every new session and cache it in
  `~/.cache/context/{sid}.json`.

## See Also

- [[HOME]] — dashboard & quick commands
- [[DATA_STORES]] — every index used by the scoping pipeline
- [[PIPELINE]] — full data flow from API to context pack
- [[TOOLS_INDEX]] — all tools, including the context builder and forensic similarity scanner
- [[CONVENTIONS]] — canonical rules (Pattern 4: Selective Section Routing)
