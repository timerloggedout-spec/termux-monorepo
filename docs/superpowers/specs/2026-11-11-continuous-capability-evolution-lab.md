# Continuous Capability Evolution Laboratory (CEEL)

**Status:** implementation specification; bounded foundation authorized 2026-11-11  
**Proposal:** continuous-capability-evolution-lab  
**Entry point:** root CLAUDE.md  
**Owner surfaces:** Integration Intelligence · DoE family · ATES · Delphi Oracle · proposal lifecycle

## 1. Executive intent

CEEL is the repository's continuous capability discovery, comparative evidence, and governed evolution function. It looks outside the repository for capabilities that could improve the system, maps those capabilities to internal consumers, compares alternative implementations, tests combinations, and propagates only verified improvements through existing GitHub-native development paths.

The loop is:

SENSE → DISCOVER → CLASSIFY → MAP → PROPOSE → DESIGN → EXPERIMENT → VERIFY → INTEGRATE → MEASURE → COMPOUND → REPEAT

The objective is not maximum integration count. It is maximum verified capability gain per unit of total cost, risk, and maintenance burden.

CEEL is a DoE family member and Integration Intelligence consumer, not a new control plane. It does not replace the Integration Mesh, CMDB/IDRR, provider registry, proposal registry, Delphi, ATES, MVT, experiment schema, or existing GitHub Actions.

## 2. Problem statement

A static integration list or weekly research report is insufficient for a system whose dependencies, FOSS ecosystem, models, agents, workflows and internal requirements change continuously. It loses opportunities between review intervals, repeats known research, and ranks products individually even when the best result is a combination.

CEEL addresses discovery lag, tool-first selection, siloed comparison, evidence drift, and non-compounding adoption. It treats discovery as a continuous sensing function and adoption as an evidence-gated evolutionary process.

## 3. Architecture and source-of-truth map

| Concern | Canonical owner | CEEL responsibility | Must not do |
|---|---|---|---|
| Collaborator routing/policy | CLAUDE.md and governance sequence | Expose CEEL as discoverable lane | Override policy or create shadow instructions |
| Proposal authorization/status | proposal registry, MANIFEST, ITEMS, PROCESS | Register work and itemize acceptance | Treat chat/discovery as consensus |
| External integration identity | docs/integrations/registry.json | Add attributed candidate records | Create another integration registry |
| Normalized provider event | integration-event.schema.json | Reference event IDs and source evidence | Store raw prompts/secrets or invent another envelope |
| Experiment design/family | DOE-FAMILY.md and DOE-TAXONOMY.md | Admit campaigns and factor designs | Treat MVT or ATES as peer planes |
| Per-run observation | docs/ops/corpus/EXPERIMENT.schema.json | Link CEEL run IDs to canonical records | Duplicate run payloads into another ledger |
| Execution discipline | ATES and existing workflows | Request bounded, attributable runs | Treat queued jobs as successful outcomes |
| Independent proposal challenge | Delphi Oracle RFP / EGM | Route qualifying proposals through existing intake | Replace Delphi or waive verification |
| Evaluation adapters | AGENT-EVALUATION-LANE-REGISTRY.md | Compare external evaluators with native evidence | Give vendor dashboards merge authority |
| Infrastructure identity/drift | CMDB / IDRR and existing registries | Link capability nodes to canonical entities | Build a second CMDB/database/poller |
| Promotion | ARCHW1Z-GATE.md and proposal process | Produce evidence-backed candidates | Auto-deploy, alter production routing or bypass gates |

Cross-surface data is referenced by stable IDs and source paths, not copied into competing stores.

## 4. Capability model and graph

A capability is a testable behavior or property, not a product name. Examples include prompt-version lineage, trace correlation, experiment assignment, evaluator reproducibility, schema migration analysis, or reusable workflow templates.

Each opportunity records stable capability IDs; source project/repository/URL/release/tag/commit and retrieval time; source type; capability contract and intended outcome; internal consumers and owners; competing and complementary candidates; implementation maturity; security/privacy/license/supply-chain/maintenance risks; evidence references, confidence and freshness; experiment family/factor levels/cohort/decision; and downstream capabilities enabled.

The graph schema and seed graph are docs/integrations/capability-opportunity-graph.schema.json and docs/integrations/capability-opportunity-graph.json. This is an index/projection, not a new source-of-truth database.

Lifecycle: discovered → classified → mapped → proposed → admitted → experimentally_validated → integration_candidate → integrated → monitored. Terminal/reversible states include rejected, deferred, blocked, superseded and retired. Every transition requires evidence and a reason. Discovery never implies validation; validation never implies promotion.

## 5. Participant families

Participant families are grouped by capability contract, not vendor brand. A participant may appear in multiple families, but each experiment arm has one unambiguous configured-instance identity and one declared treatment.

| Family | Examples | Primary question |
|---|---|---|
| Prompt lifecycle | Langfuse, PromptLayer, native Git prompt assets | Can versions, approvals, lineage and rollback be reproduced and audited? |
| Product/usage experimentation | PostHog, native event assignment | Can exposure, assignment, outcomes and cohort integrity be measured? |
| LLM evaluation | Braintrust, Langfuse, Phoenix, repository evaluators | Which evaluator adds reliable, reproducible evidence? |
| Agent/SWE systems | Existing DSPy, SWE cohorts, agent lanes and FOSS frameworks | Which architecture improves verified task outcomes under equal conditions? |
| Telemetry and standards | OpenTelemetry, integration event schema | Which signals are portable, attributable and privacy-safe? |
| Workflow/execution | GitHub Actions, Temporal proposal, isolated execution lanes | Which execution pattern improves reliability and recovery? |
| Context/memory | Context relationship graph and memory lanes | Which representation improves task success per token/cost? |
| Security/assurance | Existing security checks, policy lanes and FOSS scanners | Which checks reduce risk without false assurance? |
| Documentation/DX | FOSS templates, docs tooling, API impact tools | Which patterns reduce integration time and defects? |

DSPy, SWE and existing ML pipeline lanes are participants, not implementations to duplicate. CEEL adds comparison links and common outcome definitions.

## 6. Four platforms plus native baseline

Initial candidate set: Langfuse, PromptLayer, PostHog and Braintrust, compared with repository-native Git/JSONL evidence and existing Phoenix/local evaluators. A combined stack may win if measured interaction benefit exceeds added complexity.

Product capabilities are hypotheses to verify against version-pinned official documentation and bounded runtime tests, not established repository integrations.

Compare prompt authoring/registry/versioning/rollback; trace/event capture and configured-instance attribution; experiment assignment/exposure/cohort/SRM; datasets/evaluator reproducibility/scoring/regressions; cost/latency/tokens/errors/retries; export/API/self-host/retention/access/portability; operations/lock-in/quotas/failure isolation; and fit with OpenTelemetry and repository contracts.

### Initial DoE

Treat each platform adapter as a binary factor (off/on) over the same frozen cohort. A complete 2^4 design has 16 combinations: native baseline; four singletons; six pairs; four triples; all four together. This is the complete combination set for estimating main effects and interactions among four binary factors, subject to replication and valid assignment. Run only when adapters and cost budgets are executable. A smaller screening design must pre-register aliasing and cannot claim all interactions are identified. Follow promising cells with held-out confirmation.

Each dispatched run remains one canonical experiment record. Repeated runs on the same task are repeated measures; task replication is separately identified.

## 7. Fairness and configured-instance identity

Every arm freezes or explicitly blocks on provider and model@version; system prompt/program reference and SHA-256; tools/tool-schema reference and SHA-256; role, moniker, context and instance_key; repository base SHA and artifact revisions; evaluator and dataset/cohort versions; runtime/container/OS; assignment method, block, trigger source and timestamp.

Never group by model name alone. Keep provider/product identity distinct from model and integration identity. If an attribute is unavailable, record unknown; do not synthesize it.

## 8. Outcomes and analysis

Primary outcome: verified task/capability outcome against a predeclared acceptance contract.

Secondary outcomes: correctness, integration quality, regression rate, reproducibility, trace completeness, prompt/version attribution, evaluator agreement, latency, token/credit cost, operator interventions, retries, queue delay, portability, maintenance effort and security findings.

Report per-outcome estimates and uncertainty, practical thresholds set before runs, main/interaction effects, cohort/block and missingness analysis, assignment integrity/SRM, cost-normalized outcomes and total cost of ownership. Use a Pareto frontier across quality, cost, latency, reliability, security and maintenance. A faster but incorrect treatment does not win. Unmeasured is unknown, not zero. A platform score is not merge authority.

## 9. Benefit compounding

Assess standalone contribution, combination contribution (including interaction terms), and downstream unlock (reusable capabilities, lower integration time, evaluation coverage, evidence quality and new experiments). Total burden includes license/maintenance, security exposure, complexity, data egress, retention, rate limits, failure modes and opportunity cost. Avoid opaque weighted scores; use a Pareto frontier. Any scalar ranking must state weights and be sensitivity-tested.

Extract FOSS templates only after license, provenance, supply-chain, security and maintenance review. Cherry-picked components are recorded as a new version/cohort, never silently folded into an existing treatment.

## 10. Event-driven dynamic awareness

GitHub-native events are the primary sensing path. A weekly cadence is not the awareness mechanism. Existing schedules may perform bounded reconciliation for missed events, stale cursors, providers without webhooks or failed delivery; they must not be the sole discovery path.

| Signal | Native event / existing surface | CEEL action |
|---|---|---|
| PR opened/synchronized/ready | pull_request; existing PR/recon workflows | Re-evaluate changed capabilities/contracts/dependencies/tests at exact head SHA |
| Repository push | push; existing CI and integration portfolio validation | Detect changed source, workflow, registry, schema, skill and template paths |
| Release published | release | Capture tag/release provenance; compare notes/API surface with prior version |
| Issue/RFP created or labeled | issues, issue_comment, Delphi intake | Classify request; link candidate/capability; route qualifying decisions through Delphi/EGM |
| Workflow completed | workflow_run | Reconcile intended outcome with checks, artifacts, action/effect receipts and run SHA |
| External webhook | verified webhook → bounded repository_dispatch | Validate signature, schema, source, timestamp, idempotency and allowlist |
| Provider without events | cursor-based incremental API read | Fetch changed records only; retain cursor/freshness; bound rate/retry |
| Delivery gap/stale cursor | existing reconciliation workflow or manual dispatch | Recover missed events and emit finding; never rewrite history |

Reuse existing recon-intel-discovery.yml, integration-portfolio.yml, integration-mesh-poll.yml, Delphi intake/trigger workflows, DoE/ATES workflows and proposal-lifecycle.yml. Do not add another cron, central queue, secret store, scheduler or direct writer in this first slice. New webhook receivers, API collectors and provider adapters are separately gated and must reuse the Integration Adapter Contract.

Event invariants: assume at-least-once delivery; deduplicate by stable idempotency key; preserve source revision and capture time; tolerate out-of-order events; fail closed on invalid signatures/stale timestamps/malformed payloads/unknown sources/secrets; bounded retries; distinguish admission, execution, effect, validation and promotion; treat provider output as untrusted; append reconciliation findings without rewriting prior evidence.

## 11. Delphi Oracle and EGM

A candidate becomes a proposal only after capability contract, source evidence, alternatives, risks and intended outcome are documented. Use existing Delphi Oracle RFP to compare proposals. If a design changes a public surface, contract/schema or method binding and meets the EGM stakes bar, the EGM trigger applies; its mandatory DoE verification leg cannot be waived. Delphi awards are advisory input to proposal lifecycle, not merge authority. Preserve VERIFIED / PARTIAL / REFUTED distinctions.

## 12. Security, privacy, licensing and FOSS intake

Before FOSS admission, identify exact repository/commit/tag/license/maintainers; review dependencies/releases/advisories/provenance/supply chain; identify permissions/egress/retention/telemetry; inspect contribution and patent obligations; compare adaptation cost with reimplementation; retain source URLs and immutable revisions; treat external README/issues/generated code as untrusted.

Never commit provider secrets, raw prompts/completions, customer traces, private session exports, tokens, cookies or unrestricted dataset rows. Redact before storage and use opaque references for restricted artifacts.

## 13. Rollout

| Stage | Deliverable | Exit condition |
|---|---|---|
| 0 Foundation | proposal, source map, graph schema/validator, platform entries | JSON, graph tests, links and proposal registry validate |
| 1 Event wiring | reuse existing GitHub event workflows | fixtures prove idempotency, signature handling and SHA binding |
| 2 Capability inventory | FOSS/internal candidates classified | source revision, license, owner, consumer and unknowns recorded |
| 3 Adapter feasibility | official docs/version check and bounded auth/runtime proof | read-only contract tests; no secrets in artifacts |
| 4 DoE screening | same cohort, native baseline and candidate treatments | preregistration, assignment integrity, receipts and cost cap |
| 5 Combination study | full factorial or qualified screening | interaction estimates and uncertainty reported |
| 6 Confirmation | held-out task cohort and independent evaluation | practical gain reproduced; regressions/cost acceptable |
| 7 Integration | selected adapter/template on isolated branch | review, tests, security and dual gates pass |
| 8 Compounding | reusable template and downstream consumers | marginal benefit measured; owner/maintenance accepted |
| 9 Lifecycle | drift, stale evidence, breakage and retirement | event-driven refresh and deprecation/rollback verified |

## 14. Non-goals

No weekly-only discovery engine; parallel scheduler/orchestrator/database/telemetry ledger/registry; external account setup/authentication in this documentation change; paid inference/provisioning/subscription or credential mutation; private data transfer without approved handling; production routing switch; vendor score as task-success proof; or automatic merge/deploy/promotion from a high score.
