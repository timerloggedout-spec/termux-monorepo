# RinDig / ICM / EDUBA Consolidation

## Source set

The registry covers 10 RinDig repositories: ICM Architect, Interpretable Context Methodology, Content-Agent Routing Promptbase, Cost of Remembering, AuditEngine, GPTmetrics, Reddit evidence/stance analysis, Animation-Workflow, lecture-deck-skill, and MoralABM.

The first seven have owned timerloggedout-spec forks; the last three remain cited upstream references because no corresponding owned fork was found.

## Consolidation decisions

- ICM Architect: compact form-selection and system-map/audit skill.
- ICM Methodology: staged-workspace conventions, contracts, checkpoints/audits, bundled skills, and five-layer context hierarchy.
- Content-Agent Routing: Layer 0–3 selective loading, canonical sources, and one-way dependencies.
- Cost of Remembering: empirical filesystem-memory evidence; retain its stated LongMemEval scope and limitations.
- AuditEngine / EDUBA: psychometric/ethics evaluation surface with validated scales, multi-provider runs, personas, visual-stimulus assessment, model filtering, and CSV/JSON export.
- GPTmetrics: historical LLM survey/scoring pipeline with RWA/RWA2/LWA/MFQ/NFC, repeated calls, provider rate limiting, parsing, reverse scoring, and refusal tracking.
- Reddit evidence: research/reference lane only.
- Animation-Workflow and lecture-deck-skill: reusable media-production skills; reference-only, not monorepo runtime dependencies.
- MoralABM: moral-foundations simulation/research input.

## History and branches

The connector inventory found 151 reachable commit records across 12 branch refs. Interpretable-Context-Methodology exposes main, add-principles-and-builder-update, and add-voice-driven-animation; the other nine repositories currently expose one branch each.

The non-main ICM add-principles-and-builder-update branch adds a principles reference and strengthens workspace-builder discovery/scaffolding. add-voice-driven-animation adds a five-stage voice-led animation workspace with narration, beat extraction, and Remotion rendering skills.

## Fork synchronization

At reconciliation time, the owned forks for Interpretable-Context-Methodology, Content-Agent-Routing-Promptbase, Cost of Remembering, AuditEngine, GPTmetrics, and the Reddit evidence repository match their RinDig upstream heads.

The timerloggedout-spec/icm-architect_fork was one commit behind upstream. It was fast-forwarded to e16cafe6a664dcf6d787a726b452adba77d913f4; the delta contains the field-tested restructure fixes, reference-integrity gate, case-fold destination check, system-map reverse walk, and template/reference updates.

## Actions import

rindig-source-inventory.yml is read-only. It discovers every branch, every reachable commit on each branch, and every GitHub Actions workflow exposed for each registered repository, then publishes the complete result as a short-lived artifact.

The importer is the runtime evidence collector for refreshes. Devin/DeepWiki remains discovery-only and never authorizes a source mutation.

## Boundaries

No secrets, private wiki/session data, or provider keys are imported. Upstream source remains upstream; owned forks are customization boundaries; research references stay outside the runtime control plane unless a later proposal explicitly promotes them.
