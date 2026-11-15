# Skill Creation & Approximation Competition — Source Register

**Register version:** 1  
**Reviewed:** 2026-11-15  
**Repository:** `timerloggedout-spec/termux-monorepo`  
**Proposal item:** `APPROX-008`  
**Purpose:** provide source bundles and evidence controls for creating, upgrading, comparing, and retiring repository skills.

This register is a navigation and provenance index, not a second policy registry. Root `CLAUDE.md`, the proposal registry/ITEMS, domain-owned schemas, and executable code remain authoritative within their scopes.

## 1. Evidence labels

| Label | Meaning | Permitted use |
|---|---|---|
| **CURRENT-REPO** | Retrieved from the repository branch during this review | Describe current repository contracts at the retrieved revision |
| **PINNED-REPO** | Retrieved from a user-owned reference fork; exact blob SHA recorded | Reproduce or compare that reference revision |
| **OFFICIAL-CURRENT** | Official upstream documentation checked 2026-11-15 | Current external capability/specification claims, subject to re-check |
| **PAPER** | Primary research paper or standards handbook | Method/design rationale; not proof of local performance |
| **USER-SUPPLIED** | Uploaded artifact inspected in this session | Candidate patterns and provenance only |
| **HISTORICAL / STALE** | Superseded, outdated, or time-sensitive source | Migration/history analysis only; never assume active capability |
| **UNVERIFIED** | Search result, incomplete retrieval, or unpinned claim | Discovery lead only |

A source's existence does not establish adoption. A successful benchmark run does not establish production suitability. A skill ranking does not confer merge or deployment authority.

## 2. Repository authority and skill inventory bundle

| ID | Source | Evidence / revision | Skill use | Limitation / reconciliation |
|---|---|---|---|---|
| R01 | [Root CLAUDE.md](../../CLAUDE.md) | CURRENT-REPO; blob `98542cc` | First entry, governance order, FA-ADE, BIUDL, CEEL | Primary collaborator entry; downstream docs contain drift and must not silently override it |
| R02 | [SKILLS.md](../../SKILLS.md) | CURRENT-REPO; blob `32c7726` | Short collaborator navigation | Keep synchronized with inventory and current skills |
| R03 | [Skills Inventory](SKILLS-INVENTORY.md) | CURRENT-REPO; blob `73fd26d` | Skill discovery, role load matrix | Metadata refreshed 2026-11-15; the historic path/count snapshot still requires a live recursive-tree check before claiming exhaustive inventory |
| R04 | [Skill Discovery Matrix](SKILL-DISCOVERY-MATRIX.md) | CURRENT-REPO; blob `acb9f84` | Relationship/evidence skill cluster | Its discovery SHA/counts are historical; do not treat as current tree census |
| R05 | [Proposal Process](../proposals/PROCESS.md) | CURRENT-REPO; updated blob `393fbab` | Authorization and lifecycle | Entrypoint and branch guidance reconciled to CLAUDE.md and LANE-MATRIX |
| R06 | [ArchW1z Gate](../ARCHW1Z-GATE.md) | CURRENT-REPO; updated blob `da1630b` | Dual-gate contract | Workflow trigger wording now matches the inspected YAML; live promotion still follows LANE-MATRIX |
| R07 | [Lane Matrix](LANE-MATRIX.md) | CURRENT-REPO; blob `1c469a0` | Current PR disposition and promotion evidence | Live generated board/API still must be fetched for each decision |
| R08 | [Approxination proposal ITEMS](../proposals/active/approxination-integration/ITEMS.md) | CURRENT-REPO; item APPROX-001..008 | Scope/acceptance tracking | APPROX-006 formal A/B/C/D smoke remains separate backlog work; APPROX-008 covers skill/source reconciliation |

## 3. Approxination and competitive-evaluation bundle

| ID | Source | Evidence / revision | Skill use | Limitation / reconciliation |
|---|---|---|---|---|
| R09 | [approxination-lane skill](../../.agents/skills/approxination-lane/SKILL.md) | CURRENT-REPO; blob `85f9de4` | Search, generate, feedback, benchmark routing | Existing workflow; this upgrade makes substantive skill creation/upgrade competition mandatory |
| R10 | [Approxination ops card](APPROXINATION-LANE.md) | CURRENT-REPO; blob `137754f` | Tool-layer comparison and contribution cadence | Formal A/B/C/D execution is a separately tracked experiment |
| R11 | [Approxination cohort](../evaluations/approxination/COHORT.md) | CURRENT-REPO; blob `7425b1c` | A/B/C/D treatment definition and evidence freeze | Cohort now distinguishes A/B/C/D tool modes from skill candidate treatments and references APPROX-008; formal smoke remains APPROX-006 |
| R12 | [Approxination Benchmark fork README](https://github.com/timerloggedout-spec/Approxination-Benchmark_fork/blob/5ad5a3a45b4026b27e6408f3a838ba969a4fd113/README.md) | PINNED-REPO; README blob `5ad5a3a` | Fixed 67-task, four-mode tool-layer comparison; blind pairwise judging; category breakdown and multiple ELO estimators | Reference fork, not monorepo runtime; inspect current pinned content before each formal run |
| R13 | [Approxination task schema](https://github.com/timerloggedout-spec/Approxination-Benchmark_fork/blob/06b31d8eff1a7e23858a1dd7d4c624dc3717b620/SCHEMA.md) | PINNED-REPO; blob `06b31d8` | Agent-agnostic task prompts and deterministic output criteria | Task set/version and graders must be pinned together |
| R14 | [Inverse Arena fork README](https://github.com/timerloggedout-spec/Inverse-Arena_fork/blob/ac8adef355fb3fe02cac4c1279a40daeba7f4487/README.md) | PINNED-REPO; blob `ac8adef` | Execution-backed skill feedback, pairwise ranking, fuzzy scoring and ELO | Hosted arena includes behavior not necessarily present in open-source fork; do not equate public ranking with causal benchmark evidence |
| R15 | [Blind Agent Evaluation skill](../../.agents/skills/blind-agent-evaluation/SKILL.md) | CURRENT-REPO; blob `fddfc1e` | Blinding, attribution preservation, outcome-first scoring | Blinding is partial when identity is inferable or operationally required |
| R16 | [Multivariate DoE skill](../../.agents/skills/multivariate-doe/SKILL.md) | CURRENT-REPO; blob `e4abf7f` | Factors, blocking, randomization, replication, multi-response analysis | A/B/C/D tool-layer arms are not the same thing as candidate skill variants |
| R17 | [Agent Evaluation Framework](../architecture/AGENT-EVALUATION-FRAMEWORK.md) | CURRENT-REPO navigation target | AEF oversight and MoneyBall/3L0 integration | Load the current document and schemas before defining score fields |

## 4. Skill authoring, execution loops, and provenance bundle

| ID | Source | Evidence / revision | Skill use | Limitation / reconciliation |
|---|---|---|---|---|
| R18 | [Agent Skills specification](https://agentskills.io/specification) | OFFICIAL-CURRENT; checked 2026-11-15 | Required SKILL.md format, metadata, directory and optional resources | Validate the actual target harness's loader behavior; format support is not uniform |
| R19 | [Agent Skills authoring best practices](https://agentskills.io/skill-creation/best-practices) | OFFICIAL-CURRENT; checked 2026-11-15 | Progressive disclosure, concise trigger descriptions, scripts/resources and testing | Apply with repository conventions; don't import vendor-specific policy |
| R20 | [Claude skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | OFFICIAL-CURRENT; checked 2026-11-15 | Skill quality checklist, trigger specificity, examples, tests | Vendor guidance, not the normative cross-platform format spec |
| R21 | `skill-loopy-api-loop-library-skill.json` (session attachment) | USER-SUPPLIED; inspected 2026-11-15 | Discover/audit/craft/run/debrief/save/publish routing; terminal states; run receipts | Candidate pattern only. Catalog host in the export is a placeholder; do not claim live catalog access |
| R22 | `termux-mcp-project-steward.skill` (session attachment) | USER-SUPPLIED; inspected 2026-11-15 | Read-only default, explicit apply, isolated worktree, device preflight | Session artifact; compare against repository skill before adoption or copying |
| R23 | `context-relationship-graph.skill` (session attachment) | USER-SUPPLIED; inspected 2026-11-15 | Metadata-only graph, exact roots, verified/candidate separation | Superseded by the second uploaded variant and richer current repository skill |
| R24 | `context-relationship-graph_2.skill` (session attachment) | USER-SUPPLIED; inspected 2026-11-15 | Adds cross-reference timeline events, exact comment/review permalinks and file-review timelines | Current repository skill already contains these plus temporal corpus and optional Rust acceleration; do not create a duplicate |
| R25 | [Adaptive Feedback Cycle](../../.agents/skills/adaptive-feedback-cycle/SKILL.md) | CURRENT-REPO; blob `6c57e58` | Runtime evidence, provenance, resource/model neutrality, feed-forward loop | Reuse its event/evidence model; don't create another telemetry ledger |
| R26 | [Superpowers repository skill](../../.agents/skills/superpowers/SKILL.md) | CURRENT-REPO; blob `06fbf55` | Engineering workflow, TDD, debugging, review, verification and skill authoring | Repository governance overrides generic upstream defaults |
| R27 | [CEEL specification](../../docs/superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md) | CURRENT-REPO; blob `a86ad14` | Capability discovery, comparison, integration and compounding | CEEL reuses existing registries, schemas, DoE, ATES and proposal gates; no shadow control plane |

## 5. Technical optimization and platform bundle

| ID | Source | Evidence / revision | Skill use | Limitation / reconciliation |
|---|---|---|---|---|
| R28 | [QuickScorer SIGIR 2015](https://doi.org/10.1145/2766462.2767733) | PAPER | Bitvector representation and cache-aware traversal for additive regression-tree ensembles | Research hypothesis for eligible tree ensembles only; no transferable speedup claim for arbitrary policy trees |
| R29 | [QuickScorer PKDD 2017](https://link.springer.com/chapter/10.1007/978-3-319-71273-4_36) | PAPER | Efficient traversal of large learned decision-tree ensembles | Validate equivalence and benchmark target workload/runtime |
| R30 | [NIST blocking of factorial designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3333.htm) | PAPER / official handbook | Control nuisance variation and distinguish blocks from treatments | Use a design matched to the task population and estimand |
| R31 | [GitHub Actions concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency) | OFFICIAL-CURRENT; checked 2026-11-15 | Queue/cancellation semantics and orchestration review | Applies to Actions queues, not application-level QUE |
| R32 | [GitHub Jules changelog — Turndown](https://jules.google/docs/changelog/2026-10-29) | HISTORICAL / STALE for execution; checked 2026-11-15 | Export/migration and historical skill/workflow patterns | Jules became read-only after 2026-11-11 and is scheduled to wind down 2026-12-31; not an active execution treatment now |
| R33 | [Jules Actions repository](https://github.com/google-labs-code/jules-action) | HISTORICAL / STALE for execution; README retrieved 2026-11-15 | Historical GitHub Action contract and migration inventory | Do not design new live dependencies on Jules without fresh official lifecycle confirmation |

## 6. Additional legacy entrypoint references

| ID | Source | Evidence / revision | Finding | Treatment |
|---|---|---|---|---|
| R34 | [Codex local baseline](../../.codex/AGENTS.md) | CURRENT-REPO; updated in this branch | Previously claimed to supplement a missing root AGENTS.md | Updated to route through root CLAUDE.md |
| R35 | [ICM routing resource](../icm/routing.md) | CURRENT-REPO; updated in this branch | Previously called CLAUDE.md and AGENTS.md byte-identical aliases | Updated: CLAUDE.md is canonical; root AGENTS.md is deprecated |
| R36 | [CLAUDE human compatibility copy](../../CLAUDE.hum.md) | CURRENT-REPO; updated in this branch | Historical Linguist/CedrLang copy contains old branch rules and inventory statistics | Marked compatibility-only; not current authority |
| R37 | [GitHub project management reference](../../.github/PROJECT_MANAGEMENT.md) | CURRENT-REPO; updated in this branch | Previously named AGENTS.md as workflow integration surface | Updated to route governance to CLAUDE.md |
| R38 | [Consensus process](../CONSENSUS.md) | CURRENT-REPO; updated in this branch | Previously linked the deprecated root AGENTS.md and prescribed master-staging as the universal branch base | Updated to reference CLAUDE.md and defer branch selection to current lane policy |

## 7. Reading bundles by skill

| Skill / workstream | Required bundle | Optional / conditional |
|---|---|---|
| Skill discovery and authority reconciliation | R01–R08, R18–R20, R25–R27 | R21–R24 for supplied pattern comparisons |
| Approxination skill search/generation/competition | R09–R17, R18–R20, R25–R27 | R21–R24 for loop/skill packaging patterns |
| Blind evaluation | R12–R16, R17, R30 | R28–R29 only for decision-tree execution candidates |
| DoE / MVT | R11–R17, R25, R27, R30 | R31 for Actions-specific queue factors |
| Decision-tree execution optimization | R01, R07, R16, R25, R28–R30 | Current local router and evaluator code/tests must be fetched before design |
| GitHub Actions orchestration | R01, R05–R07, R25–R27, R31 | R32–R33 only for Jules migration/history |
| QUE performance | R07, R16, R25, R27, R31 | First identify whether QUE means application queue, provider quota queue, or Actions concurrency |

## 8. Mandatory source reconciliation before authoring

For each proposed skill change:

1. Read root `CLAUDE.md` first; then proposal registry, PROCESS, permissions, current gate policy, skills inventory, and ICM route.
2. Fetch the exact current skill, its callers, related schemas/tests, and owning implementation at one immutable ref.
3. Classify every source as current, pinned, historical, user-supplied, or unverified. Record retrieval date and commit/blob where possible.
4. Search for existing skills and superseded duplicates before creating a new skill.
5. Treat `AGENTS.md` as deprecated where root CLAUDE.md says so; do not follow stale links to it as an entrypoint.
6. Resolve policy conflicts by the owning SSOT and current evidence. Do not silently pick the most convenient document.
7. Never convert a search result, README claim, PR proposal, or historical commit into a claim of current runtime behavior.

## 9. Approximation competition contract

Substantive skill creation or upgrade must compete alternatives before adoption:

1. Include the current native skill/prompt as the incumbent baseline when one exists.
2. Search Approxination for candidate skills and references when the service/CLI is available; preserve query, retrieval time, source revision, and result identity.
3. Construct at least three meaningfully distinct candidate treatments where the problem supports them: incumbent, strongest sourced/adapted candidate, and independently designed alternative. Add further treatments only when they test a distinct hypothesis.
4. For tool-layer capability comparisons, use the pinned Approxination A/B/C/D cohort or a justified extension; do not confuse its four fixed tool modes with three candidate skill variants.
5. Hold task cohort, solver, environment, permissions, and output contract constant where possible. Randomize/rotate order and block nuisance variables where necessary.
6. Blind evaluators to treatment identity when safe and feasible; preserve attribution in a protected mapping.
7. Score correctness and task completion first; report completeness, evidence grounding, regressions, policy compliance, latency, tokens, tool calls, retries, and cost separately.
8. Use pairwise preferences/ELO as one ranking view, not sole truth. Report per-task/per-category results, uncertainty, missingness, evaluator disagreement, and replication.
9. Preserve negative, skipped, unavailable, and censored observations. No winner is declared when evidence is insufficient.
10. Select, combine, defer, or reject. Keep the incumbent if no candidate demonstrates a verified improvement after replication.
11. Record the decision, winning and losing hypotheses, source pins, experiment/cohort IDs, evidence hashes, and rollback path.
12. Do not spend paid API budget, trigger external side effects, install globally, or promote production behavior without the applicable authorization.

Approxination competition is a required evaluation method for substantive skill changes, not a blanket requirement to dispatch paid benchmark jobs for every documentation edit. If live Approxination access is unavailable, perform a documented offline candidate comparison and mark formal competition **NOT RUN** rather than claiming it occurred.

## 10. Non-duplication boundaries

- CEEL owns continuous capability discovery and routes opportunities into existing DoE/Integration Intelligence/proposal mechanisms.
- Approxination provides candidate search/generation and reference competition; it does not own repository promotion.
- AEF/DoE/MVT own experiment design and evaluation; ATES and existing evidence schemas own execution observations.
- Context Relationship Graph owns metadata relationship evidence; it is not the skill ranking ledger.
- Adaptive WAIT and production reconciliation own asynchronous execution observation; no new scheduler or telemetry store is created here.
- Jules-specific workflows are migration/history references after its read-only transition; do not treat uploaded examples as current execution guidance.
