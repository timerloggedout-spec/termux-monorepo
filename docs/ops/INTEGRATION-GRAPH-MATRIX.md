# Integration Graph Matrix (tensor mapping)

**Status:** living RECON consolidation · **Date:** 2026-09-19  
**Scope:** routing · live catalog · MoneyBall · Agentic-Agile waves · Mayan 13-phase · Paper2Agent gaps · Bifrost · notation/automation  
**Rule:** statements below are backed by GitHub sources (issue/PR/file±lines). Chat is not authority.

---

## 0. How to read this document

Objects are **nodes**. Morphisms are **directed edges** (category-theory style; see #320). Parallel independent work is a **wave** (same integer layer in the dependency DAG). Evidence classes must not be collapsed (system ATES/3L0 ≠ scientific reproduction).

```text
           live_catalog          dependency_phase_engine.waves
                │                         │
                ▼                         ▼
         model_router peers        wave admission
                │                         │
                ▼                         ▼
            invoke/MCP              execution states
                │                         │
                └──────────┬──────────────┘
                           ▼
                    telemetry / provenance
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           ATES      MoneyBall/3L0   scientific validity
                                    (Paper2Agent gap)
```

---

## 1. Source index (issues / PRs)

| ID | Title | Role in matrix |
|----|--------|----------------|
| [#621](https://github.com/timerloggedout-spec/termux-monorepo/issues/621) | Gaps Identified (Paper2Agent) | Scientific-agent factory gaps vs existing control plane |
| [#631](https://github.com/timerloggedout-spec/termux-monorepo/issues/631) | Phases with multiple parallel at different stages | Mayan 13-tone ↔ operational phases (process vocabulary) |
| [#506](https://github.com/timerloggedout-spec/termux-monorepo/issues/506) | RinDig CliefNotes Template / Certifications | Template + certification participation lane (P0 template track) |
| [#421](https://github.com/timerloggedout-spec/termux-monorepo/issues/421) | Automation Methods | Points at #320 automation comment; open checklist |
| [#320](https://github.com/timerloggedout-spec/termux-monorepo/issues/320) | Notation Sets | Category/arrow composition language for graphs |
| [PR #636](https://github.com/timerloggedout-spec/termux-monorepo/pull/636) **MERGED** | expose deterministic dependency waves | `compute_waves` on phase DAG |
| [PR #618](https://github.com/timerloggedout-spec/termux-monorepo/pull/618) **OPEN** | Agentic-Agile wave governance docs | Process contract over phase engine (adapter, not replacement) |
| [PR #611](https://github.com/timerloggedout-spec/termux-monorepo/pull/611) | Bifrost slice | Registry, catalog evaluation, provider-capabilities |
| [PR #663](https://github.com/timerloggedout-spec/termux-monorepo/pull/663) | live catalog → router | `live_catalog_feed` + bootstrap peers + FELO |

Comment cited by #421:  
https://github.com/timerloggedout-spec/termux-monorepo/issues/320#issuecomment-5514892707

---

## 2. Plane tensor (three ops planes × selection × evidence)

Authoritative three-plane split: `docs/ops/ROUTING-ORCHESTRATION-MAP.md` (whole file; Bifrost contract ~L54–62).

| Plane | Runtime | Selection input | Output |
|-------|---------|-----------------|--------|
| Review / ops (GHA) | peer-review, continuous-ops, Jules | model-router + live catalog | comments / PRs / telemetry |
| Chat | `llm_api_hub` | OpenAI-compat routes | completions |
| MCP | mcp-hub, github-remote, termux/android MCP | catalog.json hosts | tools |

**Bifrost** sits in **evaluation**, not `live_verified`:

- Proposal items: `docs/proposals/active/bifrost-gateway-integration/ITEMS.md` (BIFROST-001…)
- RECON: `docs/proposals/active/bifrost-gateway-integration/RECON.md`
- Capabilities row: `docs/schemas/provider-capabilities.md` (Bifrost evaluation / native MCP)
- Promote only with dual-gate + `results.json` (`ROUTING-ORCHESTRATION-MAP.md` Bifrost section)

ICM / context selection for Bifrost remains **templated evaluation** (drop-in `base_url`), not default ADE path until BIFROST-006 evidence lands (`BENCHMARK-SMOKE.md`).

---

## 3. Live catalog → model-router → MoneyBall (optimized chain)

Documented in `docs/ops/ROUTING-LOGIC-CHAIN.md` and implemented:

| Step | Code | Lines (approx.) |
|------|------|------------------|
| Multi-provider endpoints | `scripts/live_catalog_feed.py` | `ENDPOINTS` ~L24; `load_eligible` ~L122 |
| Peer ranking for role | same | `peer_candidates_for_role` ~L183 |
| Inject peers into router | `scripts/model_router_bootstrap.py` | whole module (~L1–80) |
| Soft-budget pick | `scripts/model_router.py` | Gemini primary then peers |
| Evidence side-channel | `docs/ops/generated/catalog-feed/latest.json` | written by `load_eligible` |

**Invariant (do not invert):**

- Live catalog **feeds** router eligibility.
- MoneyBall/3L0 **scores after repeated success** (`docs/ops/SCOUT-MISSIONS.md` admission ladder; `docs/ops/SCOUT-ROSTER.md` L8 pipeline).
- MoneyBall is **not** the per-call HTTP model picker.

FELO is first-class when `FELO_AI_API` is passed into the composite action inputs (`has-felo`, `felo-api-key`) — composite actions cannot read `secrets.*` directly.

---

## 4. Agentic-Agile waves × Mayan 13-phase (parallel stages)

### 4.1 Machine authority (waves)

Merged implementation (#636):

```text
scripts/agentic/dependency_phase_engine.py
  compute_waves()          ~L204–216
  evaluate_plan() waves    ~L346+
tests/test_dependency_phase_engine.py  (wave unit coverage)
```

Rules (from PR body + engine docstring):

- Wave 0 = no prerequisites.
- Dependent phase = 1 + max(prerequisite waves).
- **Structural** wave ≠ **runtime** readiness (`ready/running/awaiting_review/blocked/complete`).

### 4.2 Process layer (Agentic-Agile)

Open PR #618 adds / targets:

- `docs/ops/AGENTIC-AGILE-PROCESS-INTEGRATION.md` (adapter, not second scheduler)
- lifecycle: `INTAKE → … → WAVE ADMISSION → … → NEXT WAVE`
- nested runtime: `ACT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD`
- Canonical artifacts remain `docs/agentic/dependency-phases.json`, phase engine, workflows — **no competing agentic-agile.yaml**

Master already carries related sections in `docs/ops/AGENT-TEAM-ORCHESTRATION.md` (Agentic-Agile / phase-engine sections near end of file when #618 merges fully).

### 4.3 Mayan 13-phase (#631) as **process vocabulary**, not second engine

| Tone | #631 operational phase | ADE mapping |
|------|------------------------|-------------|
| 1 Magnetic | Initiation / Purpose | INTAKE / SPECIFY |
| 2 Lunar | Challenge / Obstacle | dependency / ownership check; gap taxonomy |
| 3 Electric | Activation | WAVE ADMISSION when `ready` |
| 4 Self-Existing | Form / Architecture | phase contract + DAG |
| 5 Overtone | Empowerment | authority tier / preferred_agent |
| 6 Rhythmic | Balance / Rhythm | cadence (scout 2h / execute 4h / status hourly) |
| 7 Resonant | Alignment | multi-agent coordination; no conflicting writers |
| 8 Galactic | Integrity / Modeling | review gate + required checks |
| 9 Solar | Realization | push toward completion evidence |
| 10 Planetary | Manifestation | merged PR + checks → `complete` |
| 11 Spectral | Release / Dissolution | Spectral cull; drop failing policies |
| 12 Crystal | Cooperation / Review | retrospective classifications |
| 13 Cosmic | Transcendence | next wave / higher baseline |

**Multiple parallel at different stages** = concurrent phases in the **same wave** and concurrent waves across **independent** DAGs — implemented by `compute_waves`, not by inventing 13 GitHub Project columns as authority.

---

## 5. Paper2Agent gaps (#621) vs existing ADE

#621 states the control plane is strong; the missing middle is **paper → validated scientific capability**.

| # | Gap (from #621) | Existing ADE substrate | Status |
|---|-----------------|------------------------|--------|
| 1 | Paper intake → agentification | Issue/task → manager → router | **Missing** paper manifest object |
| 2 | Method/capability extraction | Capability registry (provider tools) | **Missing** paper→method extractor |
| 3 | Paper MCP resources | MCP hosts/catalog | **Partial** — hosts not paper resources |
| 4 | Scientific prompt/workflow templates | Role prompts / manager policies | **Missing** paper-scoped prompts |
| 5 | Reference-result equivalence | ATES / MoneyBall system metrics | **Missing** scientific REPRODUCED harness |
| 6 | Claim → evidence graph | Provenance / attribution concepts | **Missing** claim graph schema |
| 7 | Scientific hierarchical router | Domain-agnostic router + MB | **Missing** domain science registry |
| 8 | Paper-agent environment isolation | Docker/Codespaces | **Partial** — not paper content-addressed |
| 9 | Scientific supply-chain boundary | MCP security | **Needs** paper-ingestion trust boundary |
| 10 | Scientific lifecycle | RECON…RECORD software loop | **Missing** DISCOVER…RE-VALIDATE paper loop |
| 11 | Dual benchmark axes | System benches | **Need** separate scientific axis |
| 12 | Paper-agent acceptance certificate | Evidence-led gates | **Missing** certificate artifact |

**Producer vs manager split (#621 synthesis):**  
Paper2Agent-style pipeline **produces** specialized scientific agents; ADE orchestration **manages** them. Do not collapse into “install Paper2Agent and delete the router.”

Critical spine (from #621, preserved here as backlog sequence):

```text
Paper → Manifest → Claim/Method Graph → Environment → Capability Extraction
  → MCP (tools+resources+prompts) → Reference Reproduction → Certificate
  → Scientific Agent Registry → Hierarchical CSO Router → MoneyBall/3L0
```

---

## 6. Notation / automation (#320, #421)

- **#320** supplies the **arrow language** for this matrix (objects, morphisms, composition, functors). Merged follow-ons include linguist/CEDR work (see #320 closed-by PR list).
- **#421** is a thin automation checklist pointing at the #320 comment thread; implementation remains open (“tbc”).
- Treat category notation as **documentation of the graph**, not a second runtime.

---

## 7. Certifications / CliefNotes (#506)

Parallel **human/agent credential** track: Skool CliefNotes templates, Eduba, role certifications. Related: #232, #485, #488.  
Does **not** alter live catalog → router → MB edges; feeds **roster / attribution** confidence when certificates exist.

---

## 8. Combined adjacency (compact)

```text
[#631 Mayan vocab] ──maps──► [Agentic-Agile lifecycle] ──adapter──► [dependency_phase_engine.waves #636]
                                      │
[#618 process docs] ──────────────────┘

[live_catalog_feed #663] ──feeds──► [model_router] ──invoke──► [telemetry]
                                      │                           │
                                      │                           ▼
                                      │                    [MoneyBall/3L0 admission]
                                      │
[provider_model_catalog / FELO / OR / Omni] ──evidence──► [catalog-feed/latest.json]

[Bifrost evaluation #611] ──optional base_url──► [chat plane]   (not live_verified)

[#621 Paper2Agent gaps] ──future producer──► [scientific agents] ──managed by──► [ADE router/MB]

[#320 notation] ──describes──► [this graph]
[#421 automation] ──open──► [automate graph ops]
[#506 certifications] ──roster──► [human/agent identity]
```

---

## 9. Implementation priority (evidence-led)

1. **Keep one phase engine** — extend waves/ownership/retrospectives; merge #618 when gates allow; never fork a second planner.
2. **Finish live-catalog callers** — pass `openrouter-api-key` / `felo-api-key` / `omni-api-key` into model-router composite from all review/ops workflows.
3. **Bifrost** — complete BIFROST-006 mocker evidence before any primary-route change.
4. **Paper2Agent spine** — start with paper manifest schema + claim graph **proposal** under `docs/proposals/` (do not pretend system ATES is scientific REPRODUCED).
5. **Mayan 13** — optional labeling overlay on phase reports (`wave` + tone id); not a new SSOT.
6. **#421 / #506** — separate lanes; link certificates into roster when artifacts exist.

---

## 10. Non-goals

- Chat transcripts as proof of integration.
- MoneyBall as runtime model picker.
- HuggingFace as required gate (optional research peer only).
- Collapsing scientific reproduction into 3L0 system scores.

---

## 11. Citation checklist (primary)

| Claim | Source |
|-------|--------|
| Three planes + Bifrost eval contract | `docs/ops/ROUTING-ORCHESTRATION-MAP.md` |
| Live catalog feeds router | `docs/ops/ROUTING-LOGIC-CHAIN.md`; `scripts/live_catalog_feed.py`; PR #663 |
| Scout → … → MoneyBall admission | `docs/ops/SCOUT-ROSTER.md`; `docs/ops/SCOUT-MISSIONS.md` |
| Deterministic waves | `scripts/agentic/dependency_phase_engine.py` `compute_waves` ~L204; PR #636 |
| Agentic-Agile adapter | PR #618; `docs/ops/AGENTIC-AGILE-PROCESS-INTEGRATION.md` (on branch) |
| Mayan 13 phases | Issue #631 |
| Paper2Agent gaps | Issue #621 |
| Bifrost items | `docs/proposals/active/bifrost-gateway-integration/ITEMS.md` |
| Provider matrix includes Bifrost/Felo | `docs/schemas/provider-capabilities.md` |
| Notation foundation | Issue #320 |
| Automation pointer | Issue #421 → #320 comment |
| Certifications template | Issue #506 |

Agent-Identity: Grok (Administrator) · RECON consolidation 2026-09-19
