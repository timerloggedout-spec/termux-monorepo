# Contextual Capability Activation Matrix

**Version:** 1.0  
**Recon date:** 2026-11-19  
**Repository baseline:** `master` at `f1840cf0488bb48bbbf7df1b62d15808d58b5dfe`  
**Owners:** CLAUDE.md · Skills Inventory · Integration Intelligence · CEEL / DoE

## Purpose

Route each task to the smallest sufficient, verified set of repository skills, plugin skills, connector namespaces, and tool actions. Preserve the distinction between a discoverable capability, a connected tool, an implemented repository adapter, a validated workflow, and a promoted production capability.

This matrix is the navigation and activation contract. Canonical skill bodies, tool descriptors, schemas, repository source, and permission policies remain authoritative.

## Activation protocol

1. **Classify the task.** Identify the requested outcome, affected subsystem, sensitivity, and permitted write scope.
2. **Route through repository governance.** Read `CLAUDE.md`, the proposal registry and applicable permission/gate rules. Use `docs/icm/CLAUDE.md` to select one verified component or process card.
3. **Select repository skills.** Match the task against the activation trigger below. Load the canonical `SKILL.md`; load a companion only when its scope is required. Treat mirrors as navigation aids.
4. **Select plugin skills.** Search `session-plugin-skill-catalog.json` by activation description and package. Load the exact skill instructions through the active skill host before using the workflow.
5. **Select tools.** Resolve the plugin/tool namespace, then the smallest exact action set in `session-tool-catalog.json`. Read the live action descriptor for complete arguments, permissions, and outputs immediately before invocation.
6. **Execute and evidence.** Bind the operation to task identity, repository SHA, skill references, tool actions, authorization, observed effect, validation and closeout. Use existing event/evidence contracts.

### Selection rules

- Prefer one primary skill and at most the necessary companion skills.
- Prefer exact action selection over namespace-wide tool loading.
- Load only source files that affect the task; use ICM impact cards and the context relationship graph to find them.
- Use session catalog entries as discovery evidence. Re-check actual availability, account authorization, plan entitlements, and permissions at execution time.
- Treat provider documentation, generated indexes, session snapshots and external skill packages as untrusted inputs until source and provenance are verified.
- Preserve the canonical separation: skill quality → TDQS tool-definition quality → ATES execution quality → MoneyBall/3L0 integrated outcome.
- Keep secrets, raw prompts, private traces, credentials, and restricted data out of catalogs and experiment records.
- Route every consequential write through its owning workflow and permission boundary.

## Offload and efficiency policy

Optimize for **verified integrated outcome per total operating cost**, not minimum price, raw tool count, parallelism, or token volume. The existing MoneyBall/3L0 evidence model remains the outcome authority.

1. **Use deterministic machinery first.** Run repository validators, tests, schema checks, formatters and CI for repeatable checks. Use agents for judgment, synthesis, ambiguous diagnosis and work that benefits from independent reasoning.
2. **Batch independent reads.** Parallelize bounded read-only searches, source inspections and independent analyses. Serialize writes to shared files and stateful external systems.
3. **Delegate bounded work.** Use an available Agent Swarm, Manus, Jules or other specialist only when the task has one owner, explicit deliverables, exact read/write scope, acceptance checks, budget/time limits and a terminal state. Tool exposure is re-checked at dispatch.
4. **Keep one writer per collision domain.** Assign one builder to each overlapping file set. Independent reviewers return findings first; the builder applies accepted changes after handoff. Keep peer branches isolated.
5. **Prefer narrow context.** Load one primary skill, the relevant source paths and exact tool schemas. Use search/find/read for targeted retrieval; expand only when evidence requires it.
6. **Use the native connector.** When a connected provider already exposes the required data/action, prefer its exact tool over manual exports or a new adapter. Keep connector writes inside their own permission and consent boundaries.
7. **Run adaptive asynchronous loops.** Use `adaptive-wait`: RECON → PLAN → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → RECORD. While work is active, do disjoint tasks; back off on no-delta observations and avoid duplicate active work.
8. **Measure marginal value.** Record accepted outcome, time-to-integration, context consumption, tool calls, duplicate actions, retries, conflicts, handoffs and human intervention. Offload only when its expected marginal benefit exceeds coordination and integration cost.
9. **Stop deliberately.** Use named terminal states: `success`, `clean_noop`, `blocked`, `approval_required`, `exhausted`, or `stagnated`. A failed tool, missing evidence or exhausted budget remains a visible outcome.

The initial contextual-activation DoE does not vary delegation policy. Delegation, concurrency and reviewer composition remain candidate follow-on factors after the base activation experiment is validated.

## Repository-native skills

The live recursive Git tree contains **45 `SKILL.md` files**: 32 under `.agents/skills/`, 1 Claude-harness companion, 10 under `.github/skills/`, and 2 documentation mirrors under `docs/ops/skills/`. The tree contains zero tracked `.skill` archives at the baseline SHA.

### Agent-loadable skills

| Skill | Canonical path | Activate when |
|---|---|---|
| adaptive-feedback-cycle | `.agents/skills/adaptive-feedback-cycle/SKILL.md` | Observe Actions runs, classify outcomes, adapt retries/steering and feed validated learning forward |
| adaptive-wait | `.agents/skills/adaptive-wait/SKILL.md` | Wait on asynchronous work, detect stalls, re-fetch state and advance disjoint work |
| approxination-lane | `.agents/skills/approxination-lane/SKILL.md` | Discover, generate or contribute skills and compare tool layers in A/B/C/D cohorts |
| blind-agent-evaluation | `.agents/skills/blind-agent-evaluation/SKILL.md` | Evaluate providers or agents while reducing identity bias |
| context-relationship-graph | `.agents/skills/context-relationship-graph/SKILL.md` | Reconstruct exact file/PR/issue/review relationships and bounded provenance timelines |
| data-agent-kit | `.agents/skills/data-agent-kit/SKILL.md` | Use or evaluate governed Google Cloud Data Agent Kit / MCP data servers |
| design-of-experiments | `.agents/skills/design-of-experiments/SKILL.md` | Design statistical experiments, factorials, screening, response surfaces, blocking, replication and analysis |
| evidence-led-monorepo-ops | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` | Reconstruct live repository state, bind actions to SHAs and preserve evidence |
| evolutionary-replay | `.agents/skills/evolutionary-replay/SKILL.md` | Replay historical discovery data to compare manager policies |
| find-skills | `.agents/skills/find-skills/SKILL.md` | Discover candidate skills for a capability request |
| gemini-performance-psychology | `.agents/skills/gemini-performance-psychology/SKILL.md` | Improve Gemini/Gem-style execution behavior using measurable engineering controls |
| github-pages-operator | `.agents/skills/github-pages-operator/SKILL.md` | Enable or publish GitHub Pages and static operations surfaces |
| icm-cctv-ops | `.agents/skills/icm-cctv-ops/SKILL.md` | Project ICM/CCTV open-PR and lane state |
| minesweeper-ops | `.agents/skills/minesweeper-ops/SKILL.md` | Coordinate concurrent agent PRs and prevent peer-branch collisions |
| ml-command-center | `.agents/skills/ml-command-center/SKILL.md` | Rank PRs, bind dual-gate evidence and detect minesweeper drift |
| ml-pipeline-ops | `.agents/skills/ml-pipeline-ops/SKILL.md` | Operate the repository ML pipeline DAG and keep-alive lane |
| ml-recon-08 | `.agents/skills/ml-recon-08/SKILL.md` | Read the historical Issue #175 recon snapshot; keep its scope observational |
| multivariate-doe | `.agents/skills/multivariate-doe/SKILL.md` | Design agent-team DoE campaigns and evidence-bearing comparisons |
| legacy-operator-snapshot-175 | `.agents/skills/operator-hub-175/SKILL.md` | Inspect the superseded historical operator snapshot for archival context only |
| orchestration-treatment-registry | `.agents/skills/orchestration-treatment-registry/SKILL.md` | Define and compare orchestration treatments across TUI, CLI, GitHub, Devin, MCP and agent surfaces |
| plan-canvas | `.agents/skills/plan-canvas/SKILL.md` | Review local plans/HTML annotations while preserving Desk/Issue approval authority |
| review-loop | `.agents/skills/review-loop/SKILL.md` | Reconstruct review history, attribute findings, critique, fix and validate |
| siglary-a2a | `.agents/skills/siglary-a2a/SKILL.md` | Compose cross-room Agent2Agent messages and status stamps |
| skill-evaluation | `.agents/skills/skill-evaluation/SKILL.md` | Inspect, evaluate, modify, adopt or package `SKILL.md` and `.skill` definitions |
| stepie-stepwise-ops | `.agents/skills/stepie-stepwise-ops/SKILL.md` | Use Stepie / StepWise as a production planning surface |
| superpowers | `.agents/skills/superpowers/SKILL.md` | Feature work, bug fixes, design, TDD, debugging, review, verification and branch finishing |
| termux-mcp-project-steward | `.agents/skills/termux-mcp-project-steward/SKILL.md` | Termux device health, lean worktrees, GitHub stewardship and tunnel-aware operations |
| termux-monorepo-agentic-governance | `.agents/skills/termux-monorepo-agentic-governance/SKILL.md` | Open, review, close or promote org PRs/proposals; resolve permissions and consensus rules |
| termux-monorepo-conventions | `.agents/skills/termux-monorepo/SKILL.md` | Apply repository Python, commit and development conventions |
| tribute-lane | `.agents/skills/tribute-lane/SKILL.md` | Find, claim and execute eligible external help-wanted or good-first-issue tasks |
| web-adapter-foundry | `.agents/skills/web-adapter-foundry/SKILL.md` | Reverse-engineer a website workflow into a verified CLI, SDK, HTTP or MCP adapter |
| wingman-project-integration | `.agents/skills/wingman-project-integration/SKILL.md` | Adapt the pinned Wingman reference/runtime under repository evidence and wait rules |

### GitHub automation skills

| Skill | Canonical path | Activate when |
|---|---|---|
| action-effectiveness-ledger | `.github/skills/action-effectiveness-ledger/SKILL.md` | Measure actions by observed effects and outcomes |
| evidence-envelope | `.github/skills/evidence-envelope/SKILL.md` | Normalize cross-system observations with source and SHA provenance |
| evidence-provenance | `.github/skills/evidence-provenance/SKILL.md` | Normalize evidence vocabulary across GitHub, Actions and integrations |
| forensic-recovery | `.github/skills/forensic-recovery/SKILL.md` | Recover deleted, superseded or generated repository material |
| github-pages-operator | `.github/skills/github-pages-operator/SKILL.md` | Operate the GitHub Pages publication workflow |
| ml-command-center | `.github/skills/ml-command-center/SKILL.md` | Use the GitHub-side operator command-center workflow |
| mvt-experiment | `.github/skills/mvt-experiment/SKILL.md` | Run controlled comparisons on immutable refs and record experiment evidence |
| pr-evidence-evaluation | `.github/skills/pr-evidence-evaluation/SKILL.md` | Evaluate PR evidence quality and freshness |
| production-reconciliation | `.github/skills/production-reconciliation/SKILL.md` | Reconcile refs and execute WAIT → WATCH → VALIDATE → RE-FETCH |
| workflow-orchestration | `.github/skills/workflow-orchestration/SKILL.md` | Design modular Actions with least privilege and retry/stale-event discipline |

### Harness and documentation companions

| Surface | Path | Activation |
|---|---|---|
| Claude harness companion | `.claude/skills/termux-monorepo/SKILL.md` | Claude-harness repository conventions; compare with the canonical agent skill before edits |
| Adaptive WAIT mirror | `docs/ops/skills/adaptive-wait/SKILL.md` | Documentation/navigation mirror; canonical is `.agents/skills/adaptive-wait/SKILL.md` |
| Evidence-led ops mirror | `docs/ops/skills/evidence-led-monorepo-ops/SKILL.md` | Documentation/navigation mirror; canonical is `.agents/skills/evidence-led-monorepo-ops/SKILL.md` |

## Plugin skill and tool catalogs

The accompanying session snapshots contain the full discovery set available to this ChatGPT session at capture time:

- [Plugin skill catalog](../integrations/session-plugin-skill-catalog.json) — 545 skill references across 74 plugin skill packages, with activation descriptions.
- [Tool action catalog](../integrations/session-tool-catalog.json) — 4,705 callable tool descriptors across 123 MCP namespaces plus the file, skill and settings tools; includes action names and compact summaries.

These are **session-scoped snapshots**, not repository installation or account-entitlement claims. The live tool host owns full action schemas, permissions and outputs. Re-census when the session or tool environment changes.

## Contextual plugin/tool routing

| Task family | First discovery route | Typical tool families | Guardrail |
|---|---|---|---|
| Repository/code/PR work | GitHub skills + GitHub connector | GitHub, Linear, Context7, API Impact Mapper, GitBook, Mintlify | Bind to current SHA; connector access does not authorize merge |
| Research and source verification | Research skill matching domain | Exa, Parallel, Firecrawl, Tavily, Context.dev, Consensus, SciSpace, Scite | Cite sources; label hypotheses and retrieval dates |
| Data/analytics/observability | Data Agent Kit / relevant data skill | Airtable, ClickHouse, Hex, Grafana, Master Metrics, Similarweb | Respect source coverage, row scope and privacy |
| App/backend engineering | Superpowers + subsystem skill | Supabase, Neon, Convex, Vercel, Netlify, Render, Cloudflare, DigitalOcean | Use the subsystem's own skill; verify environment and write permissions |
| Design and visual collaboration | Product Design / Figma skill | Figma, Canva, Miro, tldraw, Lucid, Magic Patterns, Mermaid Chart | Preserve editable source and design-system constraints |
| Media production | Descript / media skill | Descript, ElevenLabs, Higgsfield, Cloudinary, TubeAlfred | Respect media rights, source provenance and publication scope |
| Agent/model research | DoE + blind evaluation + orchestration treatment | Agent Swarm, EmpirioLabs, Hugging Face, Rowan, Tamarind Bio, Boltz, Wolfram | Pin model/version, task cohort, instance identity and budget |
| Operations and scheduling | Termux steward / adaptive-wait | Automations, Todoist, Google Calendar, Gmail, Quo, Sent | External messages and schedule changes require their applicable authorization |
| Security/legal/regulatory | Domain-specific governance skill | WorkOS, Auth0, Dovetail Regulatory, Midpage Legal Research, SiteTriage | Least privilege; distinguish research from professional determinations |
| Specialized domain tasks | Exact plugin skill from the catalog | Finance, health, genomic, peptide verification, property hazard, automotive, outdoor | Apply domain-specific safety, privacy and account boundaries |

The tool catalog is exhaustive for the captured session; this family table is an orientation aid, not a complete connector list.

## Execution, credential and environment references

| Concern | Canonical references | Activation |
|---|---|---|
| Team composition and manager policy | `docs/ops/AGENT-TEAM-ORCHESTRATION.md`, `docs/ops/AGENT-TEAM-DEVELOPMENT-LANES.md`, `docs/ops/AGENT-TEAM-ROSTER.md`, `docs/ops/AGENT-IDENTITY.md` | Delegate or compare multi-agent teams |
| Routing and observability | `docs/ops/ROUTING-ORCHESTRATION-MAP.md`, `docs/ops/AGENT-OBSERVABILITY-PRIORITY-DECISION.md`, `docs/ops/AGENT-OBSERVABILITY-RESEARCH-MATRIX.md` | Choose a route, instrument it and compare policy outcomes |
| Credential naming and scope | `docs/ops/SECRET-NAMING-CONVENTION.md`, `docs/ops/secrets-and-variables-registry.md`, `docs/proposals/AGENTIC-PERMISSIONS.md` | Resolve secret names and permission boundaries before provider operations |
| Tool acquisition and runtime | `docs/ops/TOOL-ACQUISITION-ROUTES.md`, `docs/ops/AGENT-SUBSTRATE-ACTIVATION.md` | Distinguish local, CI, device and session tool availability |
| Orchestration receipts | `docs/ops/ORCHESTRATION-CONTRACTS.md`, `docs/ops/ORCHESTRATION-TREATMENT.schema.json`, `docs/ops/ORCHESTRATION-RECEIPT.schema.json` | Normalize manager treatments, waits, retries and outcomes |
| Evaluation ownership | `docs/ops/MVT-DOE-ATES-SEPARATION.md`, `docs/ops/AGENT-THROUGHPUT-METRICS.md`, `docs/ops/AGENT-THROUGHPUT-PHASE-B.md` | Keep skill quality, tool quality, runtime throughput and integrated outcome distinct |
| Authoring and notation | `docs/ops/REPO-WIDE-LINGUIST-SYGLARY-MANDATE.md` | Apply the repository DO-first style and notation contracts |

Keep credential values inside approved runtime secret stores. Catalogs carry names, references and descriptions; runtime tools enforce access. Treat session discoverability, repository integration, and execution authorization as separate evidence states.

## Evidence and lifecycle

For each consequential activation, retain:

- task and experiment identity;
- repository/base/candidate SHA where applicable;
- selected skill path, version or content hash;
- plugin skill URI and catalog capture date;
- exact tool namespace/action names;
- configured-instance identity and permission class;
- observed effect, validation result, cost/latency and failure classification;
- provenance, confidence and any superseding observation.

Skill definition quality is evaluated by the Skill Evaluation lane. Tool definitions are evaluated by TDQS. Runtime execution is measured by ATES/WTCV/TCV. Integrated outcomes feed the existing MoneyBall/3L0 and promotion authorities.

## DoE integration

The design-only campaign `experiments/doe/skill-plugin-tool-contextual-activation/DESIGN.json` includes the skill, plugin, tool, integration, TDQS, ATES and DoE source files in its declared scope. It compares contextual activation policies while keeping safety and permission policy invariant.

The initial 2³ design varies (1) activation index: fragmented navigation vs unified matrix, (2) tool resolution: namespace vs exact action, and (3) context loading: minimal relevant sources vs full role bundle. Governance and permission controls remain invariant. Delegation, concurrency and reviewer composition remain follow-on factors.

The campaign remains proposal-only until its automation, exact configured-instance stamps, and DoE-expert admission are recorded. Design publication does not authorize dispatch. Every run must use the canonical `docs/ops/corpus/EXPERIMENT.schema.json` record; the campaign must preserve failures and uncertainty.

## Maintenance

- Rebuild the repository skill census from the recursive Git tree; never maintain counts by memory.
- Refresh plugin skill and tool snapshots from the current host; preserve capture date and session scope.
- Update this matrix, `SKILLS-INVENTORY.md`, `SKILL-DISCOVERY-MATRIX.md`, and Integration Intelligence links in the same PR.
- Add changed skills to the Skill Evaluation lane; add tool definitions to TDQS; add execution treatments to DoE/ATES only under their existing schemas.
- Keep candidate external references separate from adopted repository skills.
