# MOSAIC Brain — Software Recipe Model Integration

**Canonical program:** MOSAIC — Methodology Optimization, Self-assessment, Adaptive Intelligence & Calibration  
**Canonical reasoning subsystem:** MOSAIC Brain  
**Parent:** Continuous Capability Evolution Laboratory (CEEL)  
**Methodology family:** Design of Experiments (DoE)  
**Status:** design extension only; no runtime authority or implementation acceptance implied

## 1. Correction and decision

The earlier companion proposal incorrectly treated GRIMOIRE as a new software product/program and proposed grimoire.* as a new canonical namespace. That was a naming and architecture collision. It is withdrawn.

GRIMOIRE already exists in this repository as an established vocabulary, protocol, run-history/scorebook concept and 1337SP3@K ↔ Grimoire ↔ Orchestra crosswalk. Its canonical sources include:

- harmony_hub/config/grimoire/1337_D1CT10N4RY.md
- harmony_hub/config/GRIMOIRE_DICTIONARY.md

The dictionary already assigns terms and meanings, including Grimoire/Scorebook, Spellbook/Task Queue, Rune/Prompt Template, Transmute/Refactor, Scry/Review, Probe/Test, Echo/Fragment Match, and specialist-agent names. ArchWiz Name Forge and Sentinel already consume this vocabulary. We must not redefine Grimoire, take over its namespace, or create a second naming authority.

The software-recipe research is therefore a domain-model extension to the existing MOSAIC Brain architecture, not a new top-level intelligence system.

The repository already defines MOSAIC as the meta-methodology program within the DoE family and CEEL evolution lane; MOSAIC Brain as a bounded, advisory methodology-intelligence subsystem; Monorepo Brain as the broader typed reasoning kernel; Context Relationship Graph (CRG) as the canonical metadata-only relationship graph; and the DoE EXPERIMENT schema as the canonical experiment observation record. Delphi/EGM, SHE, 3L0, MoneyBall, ATES and FA-ADE remain existing evaluation, evidence, governance and promotion surfaces.

The new model is called Software Recipe Model (SRM) as a domain schema, owned by the MOSAIC Brain capability. It is not a new product identity. Canonical proposed namespace: mosaic_brain.recipe_model. Existing Grimoire vocabulary may provide human-facing aliases only where the Linguist/Grimoire owners approve them.

## 2. Existing architecture: reuse, do not fork

| Existing authority | Role in recipe intelligence | Prohibited duplication |
|---|---|---|
| Monorepo Brain kernel (root brain.rs and Brain facade) | Typed reasoning stages, bounded context, plan DAG and policy-gated advisory reasoning | No second repository-wide brain/kernel |
| MOSAIC Brain (archwiz/mosaic_brain/, crate mosaic-brain, scope methodology_intelligence) | Methodology and capability reasoning; recommendation only | No parallel methodology engine |
| Owner-specified rename META-brain.rs → mosaic.brain.rs | Canonical identity transition to preserve in source paths, module references and lineage | Do not resurrect old META-brain identity or introduce a third brain name |
| CRG | Canonical typed, evidence-qualified relationship graph; recipe nodes/edges are a projection/extension under its owner | No second graph database or graph authority |
| ICM / proposal registries | Ownership, navigation, lifecycle and source routing | No new registry |
| docs/ops/corpus/EXPERIMENT.schema.json | Canonical experiment/run observations | No SRM-specific experiment ledger |
| DoE family / MOSAIC | Pre-registration, comparison, calibration, uncertainty and method-version evaluation | No second DoE family or score system |
| Delphi / EGM | Independent challenge and admission | No self-review or self-admission |
| SHE / 3L0 / MoneyBall / ATES | Outcome, quality, cost and operational evidence projections | No copied telemetry authority |
| Linguist / Siglary / Grimoire | Canonical notation, dictionary, aliases and crosswalk governance | No private Siglary dialect or competing dictionary |
| Commit Replay / Repo Replay | Existing fragment, pointer, composition and replay primitives | No reimplementation of replay/index primitives |
| Kahn DAG / existing planners | Dependency ordering and plan validation | No competing DAG planner |

### Brain naming and path rule

Honor the owner-supplied rename META-brain.rs → mosaic.brain.rs as the current naming direction. Rename lineage must be explicit: historical references to the old name remain searchable and attributable, but new references use the new identity. Reconcile the rename with the already documented archwiz/mosaic_brain/src/brain.rs crate module and root brain.rs kernel; do not create a second kernel or silently move ownership. The exact filesystem/module mapping is a source-owner decision and must be confirmed against the rename commit before any path-changing implementation.

## 3. Recipe model as a MOSAIC Brain domain capability

An SRM record is a typed, immutable, provenance-bearing description of a capability:

1. Identity: capability ID, revision digest, schema version, owner, aliases and lineage.
2. Intent: objective, scope, expected decision/output and acceptance contract.
3. Ingredients: source files, modules, dependencies, APIs, data, configuration references, tools, policies and sub-capabilities.
4. Preparation: parsing, normalization, validation, preconditions, environment checks and unresolved assumptions.
5. Procedure: typed operations, ordering, dependencies, branches, loops, parallel groups and effect classes.
6. Execution context: runtime/toolchain/OS/container identity, resource limits, network policy and reproducibility assumptions.
7. Outputs: typed results, artifacts, interfaces, invariants and declared side effects.
8. Evaluation: tests, independent review, correctness, reliability, security, cost, latency and uncertainty.
9. Provenance/evolution: source commit, content digest, extraction method, evidence references, parent revision, supersession and rollback history.

The recipe model is descriptive and evidence-bearing. It does not itself execute operations or grant authority.

### 3.1 Recipe as a projection, not a new system of record

SRM records reference existing artifacts and observations by immutable identifiers/digests. They do not copy canonical PR/issue bodies, traces, raw prompts, credentials, experiment observations or telemetry payloads. Recipe graph relationships are published through CRG's existing compiler/publisher and scope governance.

### 3.2 Typed relations

Candidate relation vocabulary: CONTAINS, REQUIRES, PRODUCES, TRANSFORMS, IMPLEMENTS, TESTED_BY, EXECUTED_BY, DERIVED_FROM, SUPERSEDES, ALTERNATIVE_TO, SIMILAR_TO, CONFLICTS_WITH.

These are proposed edge semantics, not permission to add a competing graph schema. CRG ownership must review mapping, edge direction, provenance and cardinality. SIMILAR_TO never implies equivalence; compatibility requires contract or execution evidence.

## 4. Intelligence and learning model

The research algorithms are candidate adapters and experimental treatments, not one monolithic classifier:

- Deterministic rules/predicates: known identities, explicit metadata, declared constraints.
- Naive Bayes / logistic regression: low-cost multi-label classification baselines.
- TF-IDF / cosine / embeddings: lexical and semantic similarity, separately evaluated.
- Tree-sitter / AST / CST: structural facts and operation extraction.
- Dependency and call graphs: ingredient and impact relationships.
- Graph traversal / centrality / community detection: relationship analysis.
- Sequence/state-machine analysis: operation order and workflow patterns.
- Outlier detection: anomalous dependency, configuration or runtime patterns.
- Ranking / constraint optimization: candidate composition under declared contracts.

Each inference carries source, extractor/model version, confidence, timestamp and evidence class. Unknown/ambiguous states remain unknown. The classifier must abstain where evidence is inadequate.

## 5. DoE competition design

The existing DoE family and canonical EXPERIMENT record govern all trials.

| Arm | Treatment |
|---|---|
| A0 | Existing repository search/metadata baseline |
| A1 | SRM deterministic extraction and rules |
| A2 | A1 + statistical multi-label classification |
| A3 | A2 + CRG relationship projection |
| A4 | A3 + semantic similarity/reranking |
| A5 | A4 + separately admitted sandbox execution evidence |

A5 is not admitted by this proposal. Do not dispatch, infer through paid providers, write external accounts or execute untrusted recipes under this filing.

Measure retrieval relevance, classification precision/recall and calibration, duplicate-detection precision/recall, compatibility false positives, change-impact accuracy, reproducibility, resource cost and human rework. Use frozen cohorts, version-pinned treatments, preregistered outcomes, independent evaluation and held-out confirmation. Preserve per-dimension results and uncertainty; do not create an opaque composite winner score.

## 6. Work package mapping: SRM-000 through SRM-015

The original SRM work identifiers are retained for traceability but are subordinate to MOSAIC Brain and the existing MOS/CEEL plan.

| SRM | Work | Existing owner / integration | Gate |
|---|---|---|---|
| SRM-000 | Identity, collision and overlap census | MOSAIC Brain + Grimoire/Linguist + CRG owners | Confirm current names, paths, namespace and no duplicate authority |
| SRM-001 | Canonical recipe model | MOSAIC Brain domain model | Review semantics, unknowns, provenance and scope |
| SRM-002 | Schema and validator | MOSAIC Brain crate/contract tests | Schema validation + positive/negative fixtures |
| SRM-003 | Taxonomy and Siglary bridge | Linguist/Notation Matrice | Candidate notation only until admitted |
| SRM-004 | Provenance and revision identity | Git/CRG/ICM source refs | Immutable source commit and digest |
| SRM-005 | Read-only extraction | Existing repository/index adapters | Evidence provenance on every extracted fact |
| SRM-006 | AST/CST extraction | Tree-sitter adapter | Parser version and parse gaps explicit |
| SRM-007 | Deterministic/statistical classifier | MOSAIC experimental treatment | Frozen labels, held-out metrics, calibration |
| SRM-008 | Similarity and duplicate retrieval | Existing search/CRG projections | Precision/recall; no equivalence claims |
| SRM-009 | Typed relationship projection | CRG canonical graph | Owner-approved mapping and publisher path |
| SRM-010 | Retrieval and composition | Brain plan DAG + existing Kahn planner | Reject incompatible/unknown contracts |
| SRM-011 | Evaluation receipts | Canonical DoE EXPERIMENT + evidence refs | Recipe → run → result lineage |
| SRM-012 | DoE comparison | Existing DoE/MOSAIC | Pre-registration and independent analysis |
| SRM-013 | Sandboxed execution | Separate future safety proposal | Explicit owner admission; not authorized here |
| SRM-014 | Bounded evolution | MOSAIC Brain advisory recommendation | No self-approval or autonomous promotion |
| SRM-015 | Operational integration | SHE/Corpus/ATES/MoneyBall/ICM/CRG | Existing authorities remain authoritative |

## 7. Governance and safety invariants

- MOSAIC Brain recommends; existing repository governance decides.
- Recipe definitions are untrusted descriptive input, not executable authority.
- Secret values never enter recipes, embeddings, graph metadata, logs or evaluation records.
- Tool/effect permissions are references to existing policy authorities, never copied as new policy.
- Unknown provenance, stale graph snapshots and missing evidence remain explicit.
- Historical records are append-only; rename and schema migrations preserve aliases and lineage.
- No automatic merge, deploy, external write, provider inference, credential access or production routing.
- No self-authored acceptance criteria, self-evaluation, self-admission or self-promotion.
- Execution requires a separate sandbox/security RFP and owner admission.

## 8. Repository integration sequence

1. Reconcile this extension with MOSAIC Brain RFP MOS-BRAIN-001 and design MOS-001..MOS-006.
2. Confirm the META-brain.rs → mosaic.brain.rs rename commit and exact module path with the source owner.
3. Add SRM domain types inside the existing MOSAIC Brain capability only after the crate owner accepts the extension.
4. Add a read-only CRG adapter; let the canonical publisher update graph artifacts.
5. Reuse canonical DoE EXPERIMENT records for evaluation.
6. Benchmark extraction/classification/similarity against A0 before any model or graph complexity is promoted.
7. Keep execution, autonomous evolution and production integration outside this scope until separately admitted.

## 9. Decision requested

Accept or reject SRM as a MOSAIC Brain domain-model extension. Do not register GRIMOIRE as a new component. Do not create a new brain, graph, memory store, experiment ledger, notation dictionary or promotion authority. Require review from the MOSAIC Brain owner, CRG owner, DoE expert and Linguist before implementation.

## 10. Source basis

### Repository source-of-truth documents

- harmony_hub/config/GRIMOIRE_DICTIONARY.md
- harmony_hub/config/grimoire/1337_D1CT10N4RY.md
- archwiz/name_forge.py
- archwiz/sentinel.py
- docs/superpowers/specs/2026-11-16-mosaic-meta-methodology.md
- docs/superpowers/specs/2026-11-16-mosaic-brain-design.md
- docs/proposals/active/continuous-capability-evolution-lab/MOSAIC-BRAIN-RFP.md
- docs/architecture/TERMUX-MONOREPO-BRAIN-OWNERSHIP-MAP.md
- docs/architecture/TERMUX-MONOREPO-BRAIN-SUBSYSTEM-MAP.md
- docs/ops/DOE-FAMILY.md
- docs/ops/corpus/EXPERIMENT.schema.json

### External research inspirations

- Stack Overflow, “Algorithms used for programmatic classification of recipes” (2012): feature engineering, Bayesian baselines, train/test validation and redundant-feature caution. https://stackoverflow.com/questions/9265497/algorithms-used-for-programmatic-classification-of-recipes
- “What you use, not what you do: Automatic classification and similarity detection of recipes” (2018): ingredient/text features, classification and similarity as related but distinct tasks.
- 2025 recipe similarity-network research: weighted ingredient similarity and graph/community analysis.
- Tree-sitter documentation: structural parsing as an extraction source, not semantic proof. https://tree-sitter.github.io/tree-sitter/
- SLSA specification: provenance/build integrity concepts; do not overload its build-recipe terminology. https://slsa.dev/spec/v1.0/
- OpenTelemetry documentation: optional runtime observation adapter; telemetry remains in its existing authority. https://opentelemetry.io/docs/

External papers and standards are methodological inspiration. They do not establish repository compatibility or measured benefit; those require the proposed controlled DoE.
