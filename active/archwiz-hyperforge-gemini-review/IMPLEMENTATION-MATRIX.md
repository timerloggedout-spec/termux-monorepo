# ArchWiz Hyper-Forge — Gemini Implementation Matrix

**Review state:** open for collaborative reconciliation  
**Baseline:** merged PR #937 / `master`  
**Authority rule:** implementation state is determined from repository evidence, not proposal prose.

## Status vocabulary

- **IMPLEMENTED** — repository implementation exists and is on `master`.
- **PARTIAL** — some source intent is implemented, but the complete capability is not.
- **DOCUMENTED** — architecture/requirements are recorded, without claiming runtime completion.
- **PLANNED** — decomposed for future work.
- **NOT STARTED** — no implementation evidence identified.
- **REVIEW** — requires operator/reviewer decision before promotion.

## Reconciliation

| Gemini source item | Repo realization | State | Evidence / review note |
|---|---|---|---|
| Hyper-Forge / ArchWiz cockpit | `archwiz/termux_cockpit.py` | **IMPLEMENTED** | Merged via PR #937. |
| ArchWiz menu integration | `archwiz/archwiz.py` | **IMPLEMENTED** | Hyper-Forge entry is part of established cockpit. |
| Dependency-free Termux surface | ANSI/TUI cockpit | **IMPLEMENTED** | No third-party Python dependency required by cockpit. |
| 20-operation operator matrix | `termux_cockpit.py` menu | **IMPLEMENTED / NORMALIZED** | Capabilities represented; historical numbering is explicitly non-canonical. |
| Tron presentation | `ARCHWIZ_THEME=tron` | **IMPLEMENTED** | Presentation-only; no authority/routing change. |
| Foresight | `workspace/llm_map/foresight_collect.py` | **PARTIAL / COMPOSED** | Surfaced by cockpit; not a new unified Foresight runtime. |
| ChronoMancer | timeline/session surfaces | **PARTIAL / COMPOSED** | Existing tools composed; not rewritten into one subsystem. |
| Autonomous dispatch | existing dispatch runner | **PARTIAL / COMPOSED** | Cockpit routes to existing runner rather than replacing orchestration. |
| Deep RECON / archaeology | archaeology tooling | **IMPLEMENTED / COMPOSED** | Routed through existing repository-owned tooling. |
| Forensic toolchain | existing forensic helpers | **PARTIAL** | Availability is capability-dependent. |
| Backup / restore | existing state mechanisms | **PARTIAL** | Cockpit exposes state operations; full source-proposal restore semantics need explicit review. |
| Profiles / environment | existing workspace utilities | **PARTIAL** | No new universal profile protocol claimed. |
| Workflow / task builder | existing workflow surfaces | **PARTIAL** | Composition exists; full source-level builder parity remains open. |
| Timeline editor | timeline tooling | **PARTIAL** | ChronoMancer concepts are composed, not duplicated. |
| Session pipeline | existing session/pipeline surfaces | **PARTIAL** | Needs end-to-end acceptance definition. |
| Activity / narrative feed | existing evidence surfaces | **PARTIAL** | Needs canonical live-feed contract if promoted. |
| Lexicon / AST harvest | existing harvest/index tooling | **PARTIAL** | Capability exists across repo lanes; unified Hyper-Forge contract is open. |
| Live view | existing live/portal surfaces | **PARTIAL** | No claim of a single authoritative live view. |
| Documentation pipeline | existing docs automation | **PARTIAL** | Repository has automation; source proposal parity is not yet certified. |
| Sandbox promotion | existing promotion tooling | **PARTIAL** | Promotion remains governed; cockpit cannot bypass gates. |
| Dual-gate validation | repo gate + Termux smoke | **IMPLEMENTED** | Regression tests added and merged. |
| Evidence/authority boundary | Hyper-Forge docs + README | **IMPLEMENTED** | Visual UI is explicitly non-authoritative. |
| Four native Android tabs | Android UI | **NOT STARTED** | Future presentation target. |
| Unified Foresight → ChronoMancer → Dispatch loop | architecture only | **DOCUMENTED / PLANNED** | Existing pieces are composed, not yet one certified runtime loop. |
| Full agent-shell v3 / 3.5 semantics | existing agent infrastructure | **PARTIAL** | Reuse is intentional; exact Gemini parity remains unverified. |
| Source proposal milestone graph | this package | **IMPLEMENTED** | This package creates the reviewable decomposition. |
| Source-vs-engineering separation | this package | **IMPLEMENTED** | Plan and considerations are separate artifacts. |
| Collaborative GitHub issue graph | parent + milestone issues | **PLANNED / POSTING** | Issues are the next review surface. |

## Review questions

1. Which source items require exact Gemini parity versus capability-equivalent implementation?
2. Which of the 20 operations deserve independent acceptance tests?
3. Should native Android work remain a separate proposal after the Termux cockpit stabilizes?
4. Which existing Foresight/ChronoMancer artifacts are canonical enough to promote into a shared protocol?
5. What evidence is required before a source item changes from PARTIAL to IMPLEMENTED?

## Promotion rule

A row may move to **IMPLEMENTED** only when the implementation, tests, and authoritative evidence are identifiable. A design discussion alone cannot close a row.
