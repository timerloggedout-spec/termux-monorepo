# Deep RECON — Intel, Familiarization, Critical Evaluation & Proposals

**Date:** 2026-08-01  
**Branch:** `feature/recon-intel-and-nav`  
**Scope:** Codebase map, open branches/PRs/commits, refTemplates gaps, navigation SSOT, actionable proposals.

> Rule of engagement: **expand** existing recovery + inventory docs; do not replace them. All write work stays on `feature/*` until reviewed.

---

## 1. Situation report

| Fact | Detail |
|------|--------|
| Default branch | `master` @ `6ef0e2f` (protected) |
| Live monorepo | Termux-origin agentic stack: DeepSeek CLI → ArchWiz dispatch → Sentinel → promote; synthegration/Chronos; multi-agent |
| refTemplates on `master` | **Stub only:** `refTemplates/01_Agent_Runtime/README.md` |
| refTemplates skeleton | Full metadata tree on `recreate/refTemplates-skeleton` (README + SOURCE.txt per entry; depth-1 sparse style) |
| Open PRs | #1 critical-proposal, #2 GHA Rust workflow, #3 security session-store hygiene (draft) |

Canonical pipeline (from `critical-proposal` / `replit.md`):

```text
User → deepcli (TUI/cli)
  → core.py stream_completion → session cache
    → dispatch_pipeline (on cache write)
      → autonomous_runner / dispatch_task (sandbox)
        → Sentinel (5-gate) → promote
  → cli-synthegration / Chronos
  → archwiz/archivist (indices)
```

Legacy parallel paths (`export_poller.sh`, `activity_listener.py`) are **candidates for archive**, not dual maintenance.

---

## 2. Better navigation than “Entry + HTML only”

`_Entry+ReadMe.md` and `termux-ecosystem-architecture.html` are useful but **insufficient** as the sole pointers. Prefer this **SSOT ladder**:

| Priority | Artifact | Why it is better |
|----------|----------|------------------|
| 1 | `archwiz/TOOL_INDEX.md` | 28 tools, 7 categories, cockpit + FOSS stack — **operational** map |
| 2 | `archwiz/CONCEPT_INDEX.md` | Concepts, status (✅/🟡/❌), feature backlog, methodology evolution |
| 3 | `archwiz/REFERENCE_HUB.md` | Auto-generated links to DATA_FLOW, SYSTEM_MAP, func/llm indices |
| 4 | `archwiz/METHODOLOGY_INDEX.md` | What was tried, what broke, what stuck |
| 5 | `archwiz/PROCEDURES.md` + `ARCHWIZARD_TASKS.md` | Runbooks and active tasks |
| 6 | `replit.md` (branch `critical-proposal` / PR #1) | Critical issues, env-aware config design, branch evaluations |
| 7 | `_Entry+ReadMe.md` | One-line command table only |
| 8 | `termux-ecosystem-architecture.html` | Visual diagram; Termux-path absolute links in REFERENCE_HUB still need portability |
| 9 | `refTemplates/README_RECOVERY.md` (skeleton branch) | How to restore refs without recursive submodule bloat |

**Proposal N1:** Treat TOOL_INDEX + CONCEPT_INDEX as primary “where do I start?” docs; demote Entry/HTML to secondary.  
**Proposal N2:** Fix REFERENCE_HUB absolute `/data/data/com.termux/...` links via `archwiz/config.py` path roots (align with PR #1 / mistral config work).  
**Proposal N3:** Add a short “Navigation SSOT” block at the top of root README (done on this branch) that lists the ladder above — expand-only.

---

## 3. Branches — critical evaluation

| Branch | SHA (approx) | Assessment |
|--------|--------------|------------|
| `master` | `6ef0e2f` | Recovery README + live inventory + tiny refTemplates stub. Protected. |
| `critical-proposal` | `2bc964b` | **High value docs.** Corrects poller/listener as legacy; env-aware config; silent-except critique; symlink/path coupling. Safe to merge as docs. Follow-ups need code branches. |
| `mistral/fixes-config-security` | `cbe0d30` | Real `archwiz/config.py`, security docs, requirements-base, setup.sh. Gaps noted in replit.md (paths properties, __init__, silent dispatch in multi-ai-cli). **Merge after** dispatch-log fix. |
| `vibe/mistralai-vibe-code-wrapper-6055d2` | `9864646` | Mistral CLI + code_harvester (content-addressable). Copies silent `except: pass`. Path hardcoding. High value if hygiene fixed. |
| `recreate/refTemplates-skeleton` | `c1ae49f` | **Best current refTemplates representation** — categories 01–14 + uncategorized Haven/ICM_fork + README_RECOVERY. Should land on master as metadata-only. |
| `agent/repository-hygiene` | `742bba7` | PR #3: untrack session stores, sanitizer. **Priority security.** Draft; pre-commit hook issue documented. |
| `timerloggedout-spec-patch-1` | `5862ebe` | PR #2: GHA Rust build/test. Scope unclear vs monorepo Python-heavy reality; review for Termux resource limits. |

---

## 4. Open PRs — evaluation

### PR #1 — Critical Evaluation (docs)
- **Keep.** Mergeable as documentation.
- Strengths: pipeline truth, config intermediary (not naive relative paths), archive poller/listener, extension table.
- Do not treat poller/listener as first-class in architecture HTML without a “legacy” label.

### PR #2 — GHA Rust workflow
- **Caution.** Monorepo is predominantly Python/Bash; Rust is mainly Harmonizer / select refTemplates.
- Propose: narrow workflow to paths that actually contain Cargo projects; add resource limits suitable for Termux-origin CI expectations.

### PR #3 — Session store hygiene (draft)
- **Prioritize.** Session artifacts in Git is a credential-adjacent risk.
- Requirements before merge: fix pre-commit scanning deleted files to stdout; document rotation of any leaked tokens; history rewrite is separate, reviewed work.

---

## 5. refTemplates — CoPilot gaps & nesting debt

### 5.1 What CoPilot / recovery snapshot listed vs skeleton

Documented categories **01–14** plus loose top-level names. Consolidation commit `b104890` **removed** nested pointers including:

- `01_Agent_Runtime/deepcode-cli`, `hermes-agent` (later re-skeletoned as metadata)
- `07_Prompt_Context/Interpreted-Context-Methdology` (+ `_fork`)
- `13_Third_Party_Refs/assistral`
- **`15_Reverse_Engineering/`** entire set: AIStudio2API, AIStudioProxy, AIstudioProxyAPI, gemini-cli-api

### 5.2 Still uncategorized at `tree -L 1` (skeleton branch)

These sit **beside** 01–14, not inside a numbered category:

| Entry | Proposed nest |
|-------|----------------|
| `Haven/` | **15_Android_Workspaces/** or **16_Product_Workspaces/** — Android app workspace + build artifacts |
| `Interpreted-Context-Methdology_fork/` | **07_Prompt_Context/** (restore under category; keep `_fork` naming) |

### 5.3 Missing category **15_Reverse_Engineering** (removed pointers)

Propose recreate as **metadata-only** slots (README + SOURCE.txt), same sparse pattern:

- AIStudio2API
- AIStudioProxy
- AIstudioProxyAPI
- gemini-cli-api

Optional: `assistral` under 13; `deepcode-cli` under 01 if still relevant.

### 5.4 master vs skeleton drift

| Location | State |
|----------|--------|
| `master` | Only `refTemplates/01_Agent_Runtime/README.md` |
| `recreate/refTemplates-skeleton` | Full 01–14 + Haven + ICM_fork + README_RECOVERY |

**Proposal R1:** Merge skeleton → master as metadata-only (no full clones).  
**Proposal R2:** Add `15_Reverse_Engineering/` placeholders + nest Haven + ICM_fork.  
**Proposal R3:** Update root README refTemplates snapshot to mark 15 as intentional category and list uncategorized→nested plan (expand-only).

---

## 6. Live codebase comprehension (compressed)

| Layer | Paths | Role |
|-------|-------|------|
| CLI | `deepcli/`, `deepcli-tui/`, `deepseek-cli/` | Sessions, stream, PoW, export/fork |
| Cockpit | `archwiz/` | Menu, dispatch, Sentinel, Archivist, forensic restore |
| History | `cli-synthegration/`, Chronos | Branch/export/ELO/sync |
| Agents | `termux-multi-agent/` | Provision, run, Cedar MCP |
| Multi-provider | `multi-ai-cli/`, `harmonizer-prod_cli/`, `harmony_hub/` | Mistral/other + Harmonizer |
| Map | `central_mapper_v420.py`, `workspace/llm_map/` | AST/index/bloat |
| Projects | `_1-Projects/`, `exchanges/` | APIs, detectors, eggshell submodule pointers |
| Swarm template | `commingle-swarm/` | **Scavenge-only** — not first-class runtime |

Critical defects already documented (endorse, don’t re-litigate):

1. Termux path coupling / broken root symlinks  
2. Silent `except: pass` on dispatch (deepcli + multi-ai-cli)  
3. Diverged send_message vs stream_completion payloads  
4. Hardcoded session UUID fallback  
5. Session stores tracked in Git (PR #3)  
6. `.bak` pollution under archwiz  

---

## 7. Prioritized proposals (“Build the Future Now”)

| ID | Action | Effort | Depends |
|----|--------|--------|---------|
| P0 | Land PR #3 hygiene (session untrack) after pre-commit fix | M | — |
| P0 | Log dispatch failures (no silent pass) in deepcli + multi-ai-cli | S | — |
| P1 | Merge `recreate/refTemplates-skeleton` metadata to master | S | — |
| P1 | Nest Haven + ICM_fork; add `15_Reverse_Engineering` metadata slots | S | P1 skeleton |
| P1 | Expand README nav SSOT (this branch) | S | — |
| P2 | Merge PR #1 docs; implement `archwiz/config.py` consumers | M | mistral branch |
| P2 | Archive poller/listener to `_archive/` once dispatch confirmed | S | P0 log |
| P2 | Replace broken Termux absolute symlinks with config-rooted entrypoints | M | config.py |
| P3 | ChronoMancer TUI; report_back(); self-heal sandbox glue | L | pipeline stable |
| P3 | Narrow PR #2 GHA to real Cargo paths | S | review |

---

## 8. Out of scope / non-goals

- Full recursive submodule update as default (refTemplates = depth-1 sparse metadata).
- Treating `commingle-swarm` as production dependency.
- History rewrite without explicit, reviewed ops plan (after tip hygiene).

---

## 9. Sign-off

This RECON is documentation-only on `feature/recon-intel-and-nav`. Implementation of P0–P2 should proceed as separate `feature/*` branches, one concern each, with PRs against `master`.
