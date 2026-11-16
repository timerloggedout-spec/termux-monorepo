# Source Adoption Matrix — Software Recipe Intelligence

This matrix separates source-derived requirements from proposed adaptations. A cited source is not automatically adopted as an implementation or authority.

| Source / concept | Evidence-backed content | Adopt / adapt / defer | Application |
|---|---|---|---|
| Stack Overflow: algorithmic recipe classification (2012) | Classification depends on feature representation; answers discuss Bayesian, SVM, boosting, k-NN, neural and tree methods; redundant features can hurt. | Adapt | Establish a feature census and deterministic/statistical baselines before selecting a classifier. |
| “What you use, not what you do” (2018) | Ingredient and instruction-derived features support classification and similarity; these are related but distinct tasks. | Adopt as experiment design | Evaluate classification and similarity separately; compare ingredient, procedure, lexical and combined feature families. |
| Recipe similarity network (Scientific Reports, 2025) | Weighted ingredient overlap, normalization, thresholds and graph/community methods influence similarity networks. | Adapt cautiously | Test normalized dependency/tool/API/contract similarity; measure threshold sensitivity and graph bias. |
| Tree-sitter | Incremental concrete syntax trees and robust parsing, including malformed/incomplete source. | Adopt as optional extractor | Record parser version and parse gaps; syntax is not semantic or runtime proof. |
| SLSA terminology | Build process, steps, environment, parameters, dependencies, outputs and provenance have precise supply-chain meanings; “build recipe” is ambiguous. | Adopt terminology discipline | Avoid redefining SLSA or conflating a general capability recipe with build provenance. Link to SLSA attestations when available. |
| OpenTelemetry | Vendor-neutral traces, metrics, logs and baggage. | Adapt | Reference existing telemetry evidence; do not create a parallel telemetry ledger or claim OTel is required. |
| Repo Replay | External owner system; session-provenance pointers and operation-based recipes, own history DAG. | Integrate by reference | Preserve external ownership and source plane; do not copy its engine or merge its DAG into Git history. |
| Commit Replay | Git-plane `grecipe/v1`, fragment-level pointers, immutable Git object identity; explicitly separate from Repo Replay. | Integrate by reference | Link code-fragment recipes and verify materializations; do not replace either replay plane. |
| Context Relationship Graph skill | Metadata-only graph; narrow roots; verified vs candidate evidence; no persistence of PR/issue/review/comment bodies or secrets. | Adopt | Query exact roots, keep verified/candidate separate, and project recipe relations through the canonical publisher. |
| Integration Intelligence | Canonical integration registry and event envelope; capability states are not collapsed into one boolean. | Adopt | Use stable integration IDs and evidence refs; preserve discovered/connected/planned/implemented/validated/promoted distinctions. |
| CEEL | Continuous sense/discover/classify/map/propose/design/experiment/verify/integrate/measure/compound loop; reuse existing authorities. | Adopt | Use CEEL as the discovery/evolution lifecycle, not a new orchestrator or scheduler. |
| DoE / MVT | Canonical `EXPERIMENT.schema.json`; preregistration, frozen treatments, independent analysis, uncertainty and no fabricated metrics. | Adopt | Reuse experiment records and predeclare primary outcomes, blocks, randomization, leakage controls and stop rules. |
| Delphi / EGM | Independent challenge and admission; admission signal is not proof of utility. | Adopt | Preserve independent review; no self-acceptance or automatic promotion. |
| SHE / 3L0 / MoneyBall / ATES / TCV / TPV / WTCV | Existing outcome, quality, cost, throughput and operational evidence surfaces. | Adapt | Measure useful integrated outcomes, latency, retries, conflicts, human intervention, context/resource cost and attribution confidence. |
| ICM / proposal lifecycle | Existing ownership, navigation, source routing and proposal lifecycle. | Adopt | Register work and references in the existing lifecycle; no new registry. |
| Grimoire / Name Forge | Existing vocabulary, protocol and Grimoire-powered name suggestions. | Adopt governance only | Ask the existing naming process to review candidates; do not mint competing vocabulary or claim a name is issued. |
| Siglary / Linguist | Siglary is the issued compressed-notation system; Linguist governs notation and operator registry. | Defer syntax | Do not create a private grammar. Any compact notation requires registry collision review, semantics, parser fixtures and issuance. |
| Loopy Skill / Loop Library | Bounded loops use Observe → Choose → Act → Verify → Record → Repeat/stop and explicit terminal states. | Adopt | Use bounded cycles, measurable progress, explicit stop conditions and no retry-to-green behavior. |
| Termux MCP Project Steward | Read-only by default; apply only on explicit request; clean worktrees; resource-aware operations. | Adopt | Keep reconnaissance read-only, use isolated worktrees for changes, and avoid device-heavy operations without preflight. |
| Jules actions and skills reference (uploaded PDF) | Jules action/skill patterns include issue-triggered work, TDD, scoped subagents, PR review, and isolated cloud VM setup. | Adapt as external patterns | Model agent/workflow recipes with trigger, scope, environment, verification and attribution. Do not treat the PDF examples as deployed repository capabilities. |
| Agent-team routing architecture (uploaded notes) | Team operating system rather than model router; measure outcomes and integration, not model identity alone; separate manager policy from players. | Adopt as design principle | Agent/team recipes include role, assignment, routing policy, tools, handoffs, integration and outcome metrics. |\n| Uploaded operational-methodology report (file named `Notation Registry Proposal.txt`) | Historical PR #523 report covering RECON → ACT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → RECORD, runtime observation, and research/measurement surfaces. Despite its filename, it is not a notation registry proposal. | Adapt as process evidence | Reuse bounded evidence loops and explicit terminal-state discipline; do not cite it as Siglary/notation authority or assume its PR #523 state is current. |
| GitLab sync diagnosis (uploaded notes) | Correct sync-pair identity, single-writer/lease enforcement, idempotency, secret separation and correct comparison endpoints matter. | Adapt | Represent coordination recipes with canonical source-pair identity, authority/lease, idempotency and reconciliation evidence. Never include secret values. |

## External research references

- Stack Overflow, “Algorithms used for programmatic classification of recipes” (2012): https://stackoverflow.com/questions/9265497/algorithms-used-for-programmatic-classification-of-recipes
- “What you use, not what you do: Automatic classification and similarity detection of recipes” (2018): https://doi.org/10.1016/j.datak.2018.04.004
- Bellingeri et al., “The recipe similarity network” (Scientific Reports, 2025): https://www.nature.com/articles/s41598-025-17189-6
- Tree-sitter: https://tree-sitter.github.io/tree-sitter/
- SLSA v1.2 terminology: https://slsa.dev/spec/v1.2/terminology
- OpenTelemetry signals: https://opentelemetry.io/docs/concepts/signals/

## Uploaded source artifacts used

- `Awesome Jules Skills Actions and Workflows for GitHub Development.` (PDF)
- `Diagnose Routing Architecture.txt`
- `Implement GitLab Sync Diagnosis.txt`
- `Notation Registry Proposal.txt` (reviewed; content is a prior operational-methodology/PR #523 report, not a notation-registry source)
- `termux-mcp-project-steward.skill`
- `context-relationship-graph.skill`
- `context-relationship-graph_2.skill`
- `skill-loopy-api-loop-library-skill.json`

Although attachment indexing reported the Jules PDF and Loopy JSON as unparsed, their mounted originals were inspected directly (PDF text extraction and JSON parsing) and are included above. This statement records the actual source path used; it does not claim a live Jules deployment or Loop Library lookup.

## Evidence discipline

For every implementation decision, record source URL/path and revision, retrieval time, evidence class, owner, and confidence. Treat search results and lexical matches as candidates. Re-fetch before consequential edits. Keep source-derived facts, model inference, and experimental results distinct.
