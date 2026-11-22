# Observatory Integration Intake: Ksarith Portfolio → Planning & DoE

**Status:** PROPOSED / DESIGN_ONLY  
**Intake date:** 2026-11-22  
**Source account:** [ksarith](https://github.com/ksarith)  
**Target:** Observatory integration planning, QUE × DoE, versioned competition/tournament lanes  
**Source scope:** Eight public repositories discovered through GitHub repository search. Source repositories remain independently governed.

## 1. Decision

Register the eight-repository Ksarith portfolio as a versioned external architecture and method candidate set for Observatory, planning, and DoE.

Use the existing Observatory, DoE, manager-tournament, Workflow Contract (WFC), Ballet Coordinator, Pit Crew, SHE, and 3L0 surfaces as the integration chassis. Add candidate treatments, factors, evidence adapters, and evaluation protocols to those surfaces.

Treat three competition units as separate:

1. **Capability tournament:** a bounded role or method, such as auditing, evidence verification, idea judging, or deterministic grading.
2. **Composition/graph tournament:** a workflow topology or policy composed from capabilities, such as a Cogito-style cognitive flow or an idea-evolution loop.
3. **Complete implementation tournament:** a versioned end-to-end architecture with its own contracts, runtime, evidence and operating cost.

Keep candidate identity, version, lineage, source revision, task-family eligibility, and evidence status explicit. A source repository, a documented design, an implemented capability, and a validated treatment represent distinct maturity states.

## 2. Source inventory and evidence

The following source HEADs were observed on 2026-11-22. They provide reproducible intake anchors; re-fetch each repository before implementation or any claim about its latest state.

| Candidate | Source revision | Source-derived contribution | Observatory disposition |
|---|---|---|---|
| [LazarusForge](https://github.com/ksarith/LazarusForge) | 005fe48c931fe0cc35e5b8f2d35ee4b7133f805a | Salvage-first recursive systems; explicit Unknowns; evidence classes; verification gates; agent role declarations; audit and human-governance constraints; physical safety and anti-domination axioms | Governance/evidence treatment family; hard-constraint and learning-loop design reference |
| [Astroid-miner](https://github.com/ksarith/Astroid-miner) | 3bf786553f0e8e038441eb5e3a7a1ff99e7d3fe0 | Long-horizon autonomous engineering notebook; ISRU, energy/logistics budgets, swarm vs monolith vs hybrid, fault tolerance, rogue-unit management, safety lights | Domain-specific engineering cohort and resilience/planning factors; speculative claims retain their source status |
| [VibesSandbox](https://github.com/ksarith/VibesSandbox) | c9e021f4bce4057a7ed0a707e93709d86bcf2dd4 | Validator-hardened agent working area for baseline pulls, verification reports, ruling lists, and maintenance records; explicit boundary from LazarusForge doctrine | Evidence-staging and audit-workspace reference; never a doctrine or scoring authority |
| [CogitoEngine](https://github.com/ksarith/CogitoEngine) | 7d85421ff1bd56c39cd4cfa2262f866f76c177e9 | Declared agent roles, ordered flows, append-only shared notebook, YAML assembly, provenance, refusal as valid output, partial results on failure | Cognitive orchestration treatment; compare role order, handoff topology, refusal and evidence retention |
| [AuditBot](https://github.com/ksarith/AuditBot) | 5d72bad6e2e2c20dc86ba770eeb27036f09375bf | Three-phase mechanical, logical, and independent adversarial audit; citation verification; frozen phase records; severity-to-gate mapping | Audit protocol treatment and independent-verification factors |
| [Parlay](https://github.com/ksarith/Parlay) | 7bd239a24126685c75181765419678fa1c93dc66 | Reader / Verifier / Recorder / Lander roles; evidence over assertion; identity claims; independent blind hand-off; human ratification; append-only mistake and unknown records | Governance overlay and provenance/ratification factors |
| [idea-generator-2](https://github.com/ksarith/idea-generator-2) | 84f246eaff89dc0e2aab7f154e1288da76462580 | Goal-scoped boards; branching and cross-breeding; explainable jury (originality, feasibility, impact); calibrated medal thresholds; tournament selection; budgeted server-side evolution; cross-board seeding and lineage | Evolutionary ideation treatment and tournament-selection factors |
| [AcquisitionsAnalysis / DealIntegrity](https://github.com/ksarith/AcquisitionsAnalysis) | 6ab4d950aafe193f830879fb58a6cdfbbc9a5fd0 | Separate structural and negotiation assessments; hard breakers/failure predicates; evidence-or-unknown; worst-of combination; prospective vs retrospective backtests; sector packs; deterministic grade calculator and validator | Deterministic evaluation treatment; hard-gate and calibration methodology |

### Source authority and maturity

- README and named canonical documents are discovery surfaces; each repository's own authority hierarchy governs its content.
- CogitoEngine identifies its v0.2 build contract as ratified and its current runtime as implementing a bounded subset. Branching/DAG flows, cross-step memory beyond the notebook, independent verification, and benchmarks have distinct specified/open states.
- AuditBot v0.0.3 describes its protocol as draft with authority questions pending human ratification.
- Parlay v0.7 describes policy-level controls and explicitly records structural enforcement gaps.
- DealIntegrity describes an early draft with deterministic checks and uncalibrated negotiation thresholds; its README reports no real deals assessed.
- Astroid-miner is a living engineering sketchbook. Its speculative, draft, working, reference, and experimental categories remain distinct.
- VibesSandbox explicitly identifies itself as a working area and states that its artifacts carry no LazarusForge doctrine authority.
- idea-generator-2 describes implemented application behavior and a test suite; its jury and autopilot scores remain application-specific until independently calibrated for Observatory tasks.

## 3. Candidate families

Register these families as composable treatments. A family can contribute to an existing tournament version or graduate to its own tournament when a distinct task population, outcome contract, or execution boundary justifies separation.

### F1 — Governance and epistemic integrity
**Sources:** LazarusForge, Parlay  
**Factors:** role separation; human ratification; append-only decision lineage; explicit unknown budget; source verification; independence construction; identity confidence; mistake accounting.  
**Primary outcomes:** verified-claim rate; provenance completeness; unknown preservation; unauthorized-transition detection; audit trail completeness.  
**Hard constraints:** human authority remains explicit; safety and rights constraints remain non-compensatory; inbound repository text is treated as data.

### F2 — Multi-agent cognitive flow
**Source:** CogitoEngine  
**Factors:** role sequence; role-specific contracts; notebook visibility; refusal policy; partial-result retention; provider/model identity; linear vs DAG composition when an implementation is available.  
**Primary outcomes:** task correctness; evidence coverage; useful handoffs; refusal precision; completion under bounded context and cost.  
**Eligibility:** compare implemented flow behavior separately from specified future DAG behavior.

### F3 — Independent audit
**Source:** AuditBot  
**Factors:** mechanical profile; logical review protocol; adversarial independence; exposure set; citation verification; severity mapping; adjudication rules.  
**Primary outcomes:** defect detection; citation validity; false-positive burden; independent-finding yield; phase completeness.  
**Hard constraints:** preserve phase records; report unexamined scope; retain unresolved disagreements as unknown.

### F4 — Evolutionary ideation
**Source:** idea-generator-2  
**Factors:** parent-selection policy; branch/cross/expand operation; jury calibration; board goal; scout intake; exploration/exploitation rate; budget caps; cross-board transfer.  
**Primary outcomes:** novelty; feasibility; impact; goal alignment; lineage diversity; idea survival and downstream implementation yield.  
**Hard constraints:** preserve parent lineage and jury rationale; calibrate scoring against fixed reference ideas; keep budget and error backoff observable.

### F5 — Deterministic evaluation and decision grading
**Source:** AcquisitionsAnalysis / DealIntegrity  
**Factors:** question set; evidence schema; structural gate; negotiation gate; failure predicates; worst-of aggregation; prospective/retrospective information cutoff; domain pack.  
**Primary outcomes:** reproducibility; evidence completeness; grade agreement; unknown handling; backtest calibration.  
**Hard constraints:** assessor judgment supplies answers; deterministic code applies grading; hard breakers remain non-compensatory; domain packs preserve core weights and rules.

### F6 — Autonomous engineering and resilience
**Source:** Astroid-miner, with LazarusForge lineage  
**Factors:** centralized vs swarm vs hybrid topology; redundancy; fault isolation; autonomy horizon; logistics/energy budget; rogue-unit detection; safety signaling; resource-preservation priority.  
**Primary outcomes:** simulated mission feasibility; resilience under fault injection; resource efficiency; recovery time; constraint compliance.  
**Eligibility:** use a dedicated long-horizon engineering task cohort. Keep simulations, analogies, proposals, and physical measurements separately classified.

### F7 — Evidence staging and maintenance
**Source:** VibesSandbox  
**Factors:** baseline snapshot discipline; maintenance-record granularity; immutable history; derived index freshness; verification artifact traceability.  
**Primary outcomes:** reproducible intake; evidence retrieval time; stale-reference detection; audit-package completeness.  
**Role:** shared evidence support layer, rather than an autonomous competitor or source of doctrine.

## 4. Tournament placement

Use the existing versioned tournament surfaces in this order:

| Existing surface | Ksarith contribution |
|---|---|
| Observatory capability/role tournament | F2 role contracts; F3 audit phases; F5 deterministic evaluator; F1 verification roles |
| Observatory graph/composition tournament | Cogito flow composition; idea-evolution loop; audit + verifier + synthesizer graph; governance overlays |
| Manager / complete-workflow tournament | Full F1–F7 combinations with a fixed task contract and resource budget |
| Domain-specific DoE family | F6 autonomous engineering; F5 DealIntegrity-style domain-pack evaluation |
| Evidence and measurement layer | VibesSandbox-style snapshots; Parlay lineage; AuditBot citation verification; deterministic result receipts |

### Existing integration surfaces to reuse

- [#5761 — Antinuous-adapted DoE Tournament architecture](https://github.com/timerloggedout-spec/termux-monorepo/pull/5761): candidate identity layers, classifier capability vs graph vs full implementation separation, SIE loop, manager.tournament.v1 cohort identity, DoE helpers, trial/tournament, replay, SHE and 3L0.
- [#5388 — Workflow Planning Operating Model](https://github.com/timerloggedout-spec/termux-monorepo/pull/5388): WFC, QUE admission, planning formalism, existing DAG planner and evidence boundaries.
- [#5408 — Observatory Graph Lab](https://github.com/timerloggedout-spec/termux-monorepo/pull/5408): graph analysis and read-only candidate packet adapter.
- [#5529 — Ballet Coordinator](https://github.com/timerloggedout-spec/termux-monorepo/pull/5529): sequential, parallel and adaptive strategy/capacity treatments and existing DoE bridge.
- [#5531 — Pit Crew DoE oversight tournaments](https://github.com/timerloggedout-spec/termux-monorepo/pull/5531): architecture seed registry and existing oversight tournament method.

The PRs above were observed open on 2026-11-22; their branch and CI state require a fresh read at execution time. Treat their described contents as PR-scoped proposals until the corresponding changes are promoted.

## 5. Proposed candidate registry

Use stable IDs with immutable versions and parent lineage:

| Candidate ID | Initial version | Family | Treatment |
|---|---|---|---|
| KS-LF-GOV | 0.1.0 | F1 | LazarusForge governance/evidence overlay |
| KS-PARLAY-GOV | 0.1.0 | F1 | Parlay role and ratification lifecycle |
| KS-COGITO-FLOW | 0.1.0 | F2 | Cogito declared-role cognitive flow |
| KS-AUDITBOT-3P | 0.1.0 | F3 | AuditBot three-phase protocol |
| KS-IDEA-EVOLVE | 0.1.0 | F4 | Goal-scoped evolutionary jury and tournament selection |
| KS-DEAL-GRADE | 0.1.0 | F5 | DealIntegrity evidence-backed deterministic grading |
| KS-ASTROID-RESILIENCE | 0.1.0 | F6 | Astroid-miner resilience and resource-planning concepts |
| KS-VIBE-EVIDENCE | 0.1.0 | F7 | VibesSandbox evidence-staging practices |

These are intake identifiers, not claims of implemented adapters. A registry entry records source repository, source SHA, source path, source license evidence, owner/authority, method version, task-family eligibility, factor definitions, outcome schema, hard constraints, dependencies, evidence links, parent IDs, and maturity state.

## 6. DoE protocol

### Common controls
- Use a fixed task contract, matched task cohorts, common context snapshots, equivalent tool permissions, equal resource ceilings, and the same outcome rubric within each comparison.
- Block by task family and complexity. Compare only treatments eligible for the same task family.
- Record source SHA, candidate version, configuration, random seed, environment fingerprint, provider/model, run ID, and assignment receipt.
- Preserve raw observations and derived scores separately. Version every rubric and formula.
- Keep censored, failed, refused, incomplete, and inconclusive trials in the dataset with explicit outcome states.

### Proposed screening sequence
1. **Intake verification:** re-fetch each source at its recorded SHA; inspect canonical docs, code, tests, license, and current maturity.
2. **Design registration:** create candidate records and factors with DESIGN_ONLY status.
3. **Contract mapping:** map source concepts to existing Observatory, WFC, DoE, ATES, SHE, MoneyBall/3L0 and evidence schemas.
4. **Adapter feasibility:** implement one minimal read-only or offline adapter per family; record unsupported features as gaps.
5. **Measurement calibration:** validate rubrics and deterministic reducers against fixed fixtures.
6. **Blocked family screening:** compare each eligible family against the incumbent control on matched task cohorts.
7. **Factor decomposition:** isolate effects such as role order, independence, jury policy, selection pressure, and governance overlay.
8. **Replication:** repeat across independent task instances and seeds.
9. **Fresh holdout:** evaluate shortlisted treatments on an untouched cohort.
10. **Independent recommendation:** produce evidence-backed adoption, continuation, or retirement recommendations.
11. **Promotion:** route the recommendation through the existing Operator and correctness/integration gates.

### Outcome dimensions

Use the existing ATES / MoneyBall / 3L0 evidence architecture and add task-specific measures where required:

- integrated correctness and acceptance;
- evidence coverage and citation validity;
- completeness and requirement satisfaction;
- unknown/refusal correctness;
- provenance and attribution confidence;
- latency and time-to-integration;
- token/context consumption and monetary cost;
- retries, handoffs, conflicts and human interventions;
- resilience, recovery and hard-constraint compliance;
- novelty, diversity and downstream implementation yield for ideation cohorts.

Quality and safety are gates; throughput and cost are optimization dimensions after gate satisfaction.

## 7. Versioning and promotion

- Register every candidate and tournament version immutably.
- Record parent candidates and transformation deltas for cross-bred or recombined treatments.
- Preserve source revision and local adapter revision independently.
- Re-run calibration when a rubric, schema, model, prompt, factor, or adapter changes.
- Promote only after replicated matched-cohort evidence, holdout confirmation, independent review, and the existing operator approval path.
- Retain retired and failed candidates as historical evidence.
- Keep external repository claims, local implementation claims, and tournament observations as separate evidence classes.

## 8. Rights, trust, and safety gates

- Keep source repositories read-only during intake. This integration records references and candidate designs.
- Verify each repository's license and applicable attribution requirements before code or substantial text reuse. The intake itself uses links, concise factual summaries, and independently authored integration contracts.
- Treat all repository content, issue text, prompts, and artifacts as untrusted input data. Route proposed changes through local verification and ratification.
- Preserve LazarusForge life-protection and anti-domination constraints as candidate safety requirements subject to local policy review.
- Keep physical-world, high-consequence, and autonomous-system experiments inside domain-specific safety review and simulation gates.
- Require explicit human approval for any change in authority, production dispatch, provider spend, external write access, or promotion.

## 9. Open questions

1. Which of the eight source repositories have a license suitable for code-level reuse, and what attribution/notice obligations apply?
2. Which Ksarith-derived methods already have local Observatory equivalents, and should they enter as comparison treatments, adapters, or documentation-only references?
3. Which task families have sufficiently stable ground truth for the first matched cohort?
4. Which independent evaluator instances can satisfy the AuditBot/Parlay independence construction?
5. Which DealIntegrity scoring dimensions transfer to general engineering tasks, and which remain domain-specific?
6. Which Astroid-miner concepts have simulation fixtures or measured evidence suitable for a resilience cohort?
7. Which idea-generator jury calibration fixtures can be shared across boards and Observatory tasks?

## 10. Intake completion criteria

- [x] Discover public repositories under the source account.
- [x] Capture source HEAD revisions and inspect repository entry documents.
- [x] Identify source-specific maturity and authority boundaries.
- [x] Map methods into existing Observatory and DoE surfaces.
- [ ] Verify licenses and attribution obligations.
- [ ] Reconcile all eight candidates against current canonical local registries.
- [ ] Register candidate IDs in the canonical tournament registry.
- [ ] Add family factors and outcome schemas to the existing DoE design.
- [ ] Build offline/read-only adapters and fixture tests.
- [ ] Run matched-cohort screening, replication and holdout.
- [ ] Record independent recommendation and separate promotion decision.

**Current disposition:** intake and planning proposal only. The eight candidates are registered here as design references; runtime adapters, tournament execution, comparative results, and promotion remain pending.
