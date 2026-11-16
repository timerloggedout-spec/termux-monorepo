# MOSAIC Brain — Software Recipe Model (SRM) Extension

**Proposal ID:** `MOSAIC-BRAIN.SRM`
**Specification family:** `SRM-*` (Software Recipe Model)
**DoE surface candidate:** `mosaic_brain.recipe_model`
**Status:** MOSAIC Brain domain-model extension proposal — not adopted, awarded, merged, or production-authorized
**Target repository:** `timerloggedout-spec/termux-monorepo`
**Proposal lane:** MOSAIC Brain / CEEL; evaluated through existing QUE → RFP → Delphi → DoE lifecycle
**Version:** 0.2.0-draft
**Authored:** 2026-11-16

---

## 0. Scope correction and executive decision brief\n\n> **Correction:** MOSAIC Brain is an existing repository vocabulary/protocol and run-history/scorebook concept. It is not the name of this proposal. This draft is subordinate to MOSAIC Brain and the existing Monorepo Brain architecture. See SCOPE-CORRECTION.md and the canonical integration design under continuous-capability-evolution-lab. The canonical proposed domain namespace is `mosaic_brain.recipe_model`; no new brain, graph, memory store, experiment ledger, dictionary or promotion authority is created. Honor the owner-supplied `META-brain.rs` → `mosaic.brain.rs` rename and preserve its lineage.\n\n## 0. Executive decision brief

MOSAIC Brain proposes a compositional intelligence layer that treats software systems as **executable, versioned recipes**. A recipe is not merely a file, script, build manifest, workflow, or prompt. It is a typed, evidence-bearing description of how a capability is assembled from ingredients, transformed through ordered operations, executed in a declared environment, evaluated against outcomes, and evolved across revisions.

The culinary analogy is useful because it forces a complete view:

| Culinary concept | Software counterpart |
|---|---|
| Dish / recipe identity | Capability identity + immutable revision |
| Ingredients | Source, dependencies, data, APIs, config, tools, policies |
| Preparation | Parsing, normalization, validation, preconditions |
| Method / steps | Ordered operations, algorithms, branches, concurrency |
| Equipment | Runtime, OS, compiler, container, infrastructure |
| Serving / result | Outputs, interfaces, artifacts, state transitions |
| Taste / quality | Tests, acceptance, quality, performance, safety |
| Substitution | Compatible alternative dependency or implementation |
| Cookbook lineage | Provenance, derivation, supersession, historical corpus |
| Chef's notes | Human annotations, rationale, confidence, unresolved assumptions |

The metaphor is a modeling aid, not a replacement for engineering semantics. Software recipes require formal contracts, machine-verifiable evidence, security boundaries, deterministic identity, and explicit unknown states.

**Recommendation:** admit MOSAIC Brain as a bounded research/design candidate, not as a live autonomous executor. Begin with read-only extraction, identity, taxonomy, graph relationships, and deterministic baselines. Enable execution only in an isolated, policy-constrained environment after reproducibility and safety gates pass.

### What this proposal adds

1. A canonical Software Recipe Model (SRM) and JSON Schema.
2. A stable identity and naming system that avoids collision with generic terms such as `SYSTEM_RECIPE`.
3. A recipe taxonomy and typed relationship graph.
4. A classifier/similarity architecture that separates structural facts from semantic inference.
5. A DoE plan that compares competing representations and methods under controlled, version-pinned conditions.
6. A phased implementation plan integrated with existing repository systems.
7. Acceptance criteria, risk controls, governance, evidence, and source inspirations.

### What it does not claim

- It does not claim that a recipe metaphor is novel in software engineering.
- It does not replace build systems, package managers, SBOMs, workflow engines, ASTs, dependency graphs, or source control.
- It does not assert that similarity means equivalence or that a model prediction is proof.
- It does not authorize production execution, secret access, deployment, autonomous merge, or policy bypass.
- It does not assert any measured performance improvement; the proposed benefits require experiments.

---

## 1. Naming, identity and collision governance

### 1.1 Product and technical names

**MOSAIC Brain** is the project identity: *Generative Recipe Intelligence, Memory, Orchestration & Evolution*.

Canonical identifiers:

- Product / program: `MOSAIC Brain`
- System namespace: `grimoire`
- Core capability: `mosaic_brain.recipe_model`
- Canonical model: `SRM` — Software Recipe Model
- Model schema: `mosaic_brain.recipe_model.v1`
- Recipe instance ID: `mosaic-brain://recipe/{namespace}/{slug}`
- Immutable revision: `sha256:{content-digest}`
- DoE surface ID: `mosaic_brain.recipe_model`
- Proposal package: `MOSAIC Brain-SR-PROPOSAL`

`SYSTEM_RECIPE` remains a generic descriptive alias only. It must not be the product namespace, schema identifier, registry key, or globally unique ID.

### 1.2 Naming rules

1. Human-readable names are labels; machine identity is a stable ID.
2. IDs are namespaced, versioned, normalized, and never reused.
3. A recipe's logical identity is separate from its content revision.
4. A rename does not create a new logical recipe; it creates an alias/history event.
5. A fork or materially different capability receives a new logical identity with `DERIVED_FROM`.
6. A revision digest covers canonicalized content and declared semantic fields; volatile telemetry is excluded.
7. Registry uniqueness is enforced on normalized IDs, not display names.
8. Similar names trigger a collision warning; matching IDs are a hard conflict.
9. Reserved namespaces include `mosaic_brain.*`, `srm.*`, and the repository's existing `siglary.*` namespace. MOSAIC Brain must not claim or redefine Siglary operators.
10. The canonical registry records aliases, redirects, ownership, status, and supersession.

### 1.3 Identity layers

| Layer | Example | Mutability |
|---|---|---|
| Program | `MOSAIC Brain` | Governed |
| Surface | `mosaic_brain.recipe_model` | Stable |
| Recipe identity | `mosaic-brain://recipe/build/python-package` | Stable |
| Recipe revision | `sha256:…` | Immutable |
| Execution instance | `run:{provider}:{run-id}` | Immutable record |
| Evaluation record | `eval:{recipe-revision}:{suite}:{run}` | Append-only |
| Display title | “Build Python package” | Mutable alias |

---

## 2. Problem statement and opportunity

Large software repositories contain many overlapping representations of the same capability: source files, functions, packages, workflow YAML, build manifests, infrastructure definitions, tests, runbooks, issue descriptions, telemetry, and historical pull requests. These representations are not consistently connected.

Consequences include:

- Duplicate or near-duplicate implementations that are difficult to discover.
- Dependencies and execution assumptions hidden in code, configuration, environment, or tribal knowledge.
- Multiple fixes that solve similar symptoms using different methods without a clear supersession record.
- Similarity scores being mistaken for behavioral equivalence.
- Weak lineage between an implementation, its tests, its runtime evidence, and its replacement.
- Research findings that do not reliably become reusable engineering knowledge.
- Agent orchestration that selects tools or workflows without a complete capability contract.

MOSAIC Brain's hypothesis is that a normalized recipe representation can connect these artifacts into a searchable, evaluable, evolvable capability graph.

**Research question:** Does a typed, provenance-aware recipe representation improve retrieval, classification, duplication detection, composition quality, reproducibility, and change-impact analysis compared with existing repository representations alone?

---

## 3. Core definitions

- **Recipe:** Versioned declarative record of a capability's intent, ingredients, procedure, execution constraints, outputs, evaluation, and provenance.
- **Ingredient:** A referenced input required or optionally consumed by a recipe.
- **Operation:** A typed action in a recipe procedure. It may be deterministic, conditional, iterative, parallel, or externally delegated.
- **Recipe family:** Logical identity plus its immutable revisions and lineage.
- **Recipe composition:** A recipe that invokes or depends on other recipes through declared contracts.
- **Recipe graph:** Typed graph of recipes, ingredients, operations, artifacts, tests, executions, evaluations, and provenance.
- **Recipe fingerprint:** Digest over canonical recipe content; not a claim of behavioral equivalence.
- **Compatibility:** Evidence that an alternative satisfies a specific declared contract in a specified context.
- **Substitution:** Replacement of an ingredient or subrecipe, with compatibility evidence and a recorded decision.
- **Execution receipt:** Immutable record of the recipe revision, inputs, environment, operations, outputs, status, and evidence.
- **Evaluation:** Comparison of observed outcomes with predeclared acceptance criteria.
- **Evolution:** A new revision or derived recipe based on evidence; never silent mutation of history.

### 3.1 Distinguish adjacent concepts

| Existing concept | Relationship to SRM | Boundary |
|---|---|---|
| Function / procedure | May be an operation or a small recipe | SRM adds intent, environment, outputs, evaluation, provenance |
| Build recipe | A specialized recipe | Do not overload SLSA's build terminology |
| Workflow | A sequence/graph of operations | Workflow remains execution authority |
| Package manifest | Ingredient/dependency declaration | SRM references it; does not replace it |
| SBOM | Inventory of components | SRM adds purpose, procedure, outcomes, lineage |
| AST/CST | Structural evidence source | AST is not a semantic recipe by itself |
| Dependency graph | One projection of ingredient relationships | SRM graph has richer typed edges |
| Runbook | Human-readable procedure | SRM can link and normalize it without discarding narrative |
| Prompt/agent skill | A recipe ingredient or operation contract | Prompt text is untrusted input, not policy authority |
| Commit Replay / Repo Replay | Related content-addressed recipe/pointer work | MOSAIC Brain models system capability; it must reuse and not duplicate replay primitives |

---

## 4. Canonical Software Recipe Model

Every recipe MUST support the following sections. Optionality is explicit; absence is not silently interpreted as a negative fact.

### 4.1 Identity

- `recipe_id`: stable URI-like identifier.
- `revision`: immutable content digest.
- `schema_version`: SRM schema generation.
- `kind`: capability, build, test, deploy, analysis, data-transform, agent, research, policy, or composite.
- `title`, `summary`, `intent`, `owner`, `status`.
- `aliases`, `supersedes`, `derived_from`.

### 4.2 Ingredients

Each ingredient records:

- Stable reference and type.
- Role: required, optional, conditional, secret-reference, runtime, policy, data, source, dependency, service, tool, or subrecipe.
- Version/range or immutable digest where available.
- Origin and retrieval provenance.
- License/security classification where known.
- Constraints and compatibility contract.
- Whether it is observed, declared, inferred, or unresolved.

Secret values are never serialized into a recipe. Only secret references and policy metadata may appear.

### 4.3 Preparation

Preparation captures parsing and preflight:

- Input validation and normalization.
- Environment checks.
- Preconditions and invariants.
- Required permissions and trust boundaries.
- Missing/ambiguous inputs.
- Deterministic setup operations.

### 4.4 Procedure

Operations form an ordered directed acyclic graph where possible. Cycles are represented explicitly as bounded loops or state-machine transitions, never smuggled into an acyclic plan.

Operation fields:

- `op_id`, `type`, `intent`, `inputs`, `outputs`.
- `depends_on`, `condition`, `loop_policy`, `parallel_group`.
- `timeout`, `retry_policy`, `idempotency_key`.
- `effect_class`: pure, read, write, external, privileged, destructive.
- `policy_ref`, `evidence_ref`.

Operation order is semantically significant unless a declared commutativity rule proves otherwise.

### 4.5 Execution environment

Declare:

- Runtime, language, version, OS, architecture.
- Toolchain and container/image digest.
- Network requirements and egress policy.
- Resource limits and execution lane.
- External services and provider adapters.
- Reproducibility level and known nondeterminism.

### 4.6 Outputs and contracts

Each output declares:

- Name, type, schema/contract reference.
- Expected invariants.
- Artifact location or content digest.
- Side effects and state changes.
- Acceptance criteria.
- Whether the output is required, optional, or conditional.

### 4.7 Evaluation

Record:

- Test suites and versions.
- Functional, integration, security, performance, reliability, and reproducibility outcomes.
- Metrics, units, thresholds, uncertainty, and missing evidence.
- Baseline and candidate identifiers.
- Evaluator identity and independence.
- Verdict: pass, fail, partial, inconclusive, unavailable, or not-run.

### 4.8 Provenance and evolution

Append-only provenance includes:

- Source repository, path, commit, and immutable ref.
- Extraction tool/version and timestamp.
- Authoring or derivation agent/human identity.
- Evidence references and content digests.
- Parent revision and change rationale.
- Review, validation, promotion, rollback, and supersession records.

---

## 5. Recipe taxonomy

Taxonomy is hierarchical and multi-label. A recipe may be both `build` and `security`, or `data-transform` and `research`. Classification must not force one mutually exclusive category.

### 5.1 Primary kind

`capability | build | test | deploy | analysis | data-transform | orchestration | agent | research | policy | observability | recovery | composite`

### 5.2 Domain labels

- `language/*`: Python, JavaScript, TypeScript, Rust, Go, Shell, YAML, SQL, etc.
- `system/*`: CI/CD, build, packaging, deployment, infrastructure, storage, network.
- `data/*`: ingestion, normalization, indexing, graph, retrieval, lineage.
- `quality/*`: test, static-analysis, performance, reliability, security.
- `intelligence/*`: classification, similarity, recommendation, planning, learning.
- `agent/*`: tool-use, delegation, routing, memory, evaluation.
- `research/*`: literature, benchmark, experiment, FOSS discovery.
- `governance/*`: authorization, policy, provenance, audit, promotion.

### 5.3 Execution/effect labels

`pure | read-only | writes-local | writes-repository | external-call | privileged | destructive | human-review-required`

### 5.4 Evidence labels

`declared | extracted | inferred | tested | observed | independently-verified | disputed | stale | unavailable`

A label must carry provenance and confidence. Human-confirmed facts, parser-extracted facts, model-inferred facts, and runtime-observed facts must remain distinguishable.

---

## 6. Classification and similarity engine

MOSAIC Brain uses an ensemble of specialized methods. No single algorithm is treated as universally best.

### 6.1 Feature families

1. Lexical: names, identifiers, comments, docs, issue/PR titles.
2. Structural: AST/CST node types, call graph, control flow, module boundaries.
3. Ingredient: imports, package dependencies, APIs, environment variables by name only, data sources.
4. Procedural: operation sequence, state transitions, control-flow patterns.
5. Contract: input/output types, schemas, invariants, error behavior.
6. Runtime: observed traces, metrics, logs, execution receipts.
7. Historical: commits, diffs, issue/PR lineage, supersession, revert and repair history.
8. Contextual: repository lane, domain, owner, trust boundary, deployment target.

### 6.2 Candidate algorithms

| Task | Baseline | Advanced candidate | Caution |
|---|---|---|---|
| Taxonomy classification | Rules + TF-IDF/logistic regression | Calibrated transformer classifier | Keep multi-label and abstention |
| Similarity retrieval | Token/identifier TF-IDF + cosine | Embeddings + reranking | Similarity is not equivalence |
| Structural matching | AST fingerprints | Graph edit distance / tree kernels | Language and parser coverage vary |
| Dependency similarity | Weighted ingredient overlap | Typed graph embeddings | Normalize for recipe size |
| Duplicate detection | Exact digests + normalized hashes | Hybrid near-duplicate ranking | Preserve false-positive review |
| Community discovery | Connected components / modularity | Clique/percolation and graph clustering | Threshold choice changes topology |
| Anomaly detection | Deterministic constraints | Isolation Forest / robust statistics | Explain signals and avoid opaque verdicts |
| Recommendation | Contract-filtered ranking | Contextual bandits after evidence | No unsafe substitution |
| Workflow planning | Kahn topological order | Cost-aware scheduling / optimization | Preserve cycle and dependency diagnostics |
| Evolution | Human-reviewed diffs | Bounded search / evolutionary optimization | No self-promotion or unrestricted mutation |

### 6.3 Classifier output contract

Every prediction returns:

- Label(s), confidence, and calibration metadata.
- Evidence features supporting the label.
- Model/rule version and training corpus snapshot.
- Known limitations and abstention reason.
- Whether it is inferred or human-confirmed.
- Timestamp and immutable source refs.

Unknown is a first-class state. A classifier must abstain when evidence is insufficient or contradictory.

### 6.4 Similarity is not equivalence

A similarity result may be used for discovery only. Equivalence requires matching declared contracts plus sufficient test or execution evidence in the relevant environment. Compatibility is scoped to version, context, inputs, policies, and expected outputs.

---

## 7. Relationship graph

### 7.1 Node classes

`RecipeIdentity`, `RecipeRevision`, `Ingredient`, `Operation`, `Artifact`, `Contract`, `TestSuite`, `Execution`, `Evaluation`, `Evidence`, `Repository`, `Commit`, `Issue`, `PullRequest`, `Agent`, `Environment`, `Policy`.

### 7.2 Typed edges

- `HAS_REVISION`
- `CONTAINS`
- `REQUIRES`
- `CONSUMES`
- `PRODUCES`
- `TRANSFORMS`
- `DEPENDS_ON`
- `IMPLEMENTS`
- `TESTED_BY`
- `EXECUTED_BY`
- `EVALUATED_BY`
- `DERIVED_FROM`
- `SUPERSEDES`
- `ALTERNATIVE_TO`
- `SIMILAR_TO`
- `CONFLICTS_WITH`
- `VALIDATED_BY`
- `OBSERVED_IN)
- `GOVERNED_BY)

Edges carry evidence, direction, validity interval, confidence, and source revision. A `SIMILAR_TO` edge never implies `ALTERNATIVE_TO`; neither implies `SUPERSEDES`.

### 7.3 Graph projections

The same canonical graph supports:
- Recipe lineage and revision history.
- Ingredient/dependency impact.
- Capability discovery and reuse.
- Duplicate and supersession analysis.
- Test/evidence coverage.
- Execution and failure analysis.
- Communities and research maps.
- Change-impact and risk analysis.

The graph is a derived knowledge layer, not a replacement for Git, issue ledgers, workflow state, or the canonical source artifacts.

---

## 8. Architecture and repository integration

### 8.1 Logical components

1. **Extractor:** repository/file/API adapters; read-only first.
2. **Normalizer:** canonical identity, feature and schema normalization.
3. **SRM registry:** recipe identities, revisions, aliases, schema validation.
4. **Classifier:** rule, statistical, and semantic adapters.
5. **Graph builder:** typed nodes/edges with provenance.
6. **Retriever:** lexical, structural, graph, and embedding search.
7. **Composer:** contract-checked recipe composition and dependency planning.
8. **Executor adapter:** isolated execution only after explicit admission.
9. **Evaluator:** tests, outcomes, uncertainty, baseline comparisons.
10. **Memory/evolution ledger:** append-only revisions, findings, and decisions.
11. **Governance plane:** policy, DoE, Delphi, QUE and promotion integration.
12. **Observability:** OpenTelemetry-compatible traces, metrics and logs.

### 8.2 Existing project integration map

The following are integration targets, not claims that MOSAIC Brain is already wired into them:

| Existing system | MOSAIC Brain relationship |
|---|---|
| Historical Corpus | Historical recipe source, revisions, lineage and evidence backfill |
| Context Relationship Graph | Canonical typed recipe/ingredient/operation graph |
| SHE | Quality, execution and system-health projections |
| ATES / WTCV / MoneyBall | Comparative outcome, effort, latency, rework and attribution |
| 3L0 | Quota/cost-aware execution constraints; no authority escalation |
| Kahn DAG | Reuse canonical topological planning; do not fork the planner |
| Bayesian routing | Candidate confidence/value-of-information input, not truth authority |
| Markov trellis lab | Optional dynamics research factor; not assumed production-ready |
| Tree-sitter | Structural extraction provider |
| OpenTelemetry | Runtime signals and correlation context |
| Docker / approved sandbox | Reproducible execution substrate |
| CI/CD | Recipe validation and execution evidence |
| QUE | Admission, ranking and claim authority |
| Delphi | Independent proposal adjudication |
| DoE | Experiment design and versioned comparison |
| Commit Replay / Repo Replay | Reuse content-addressed and pointer/operation concepts; do not duplicate replay engines |

### 8.3 Important overlap finding: existing replay work

Repository search surfaced existing Commit Replay work, including:
- PR #3711 — fragment index, `compose()`, pointer-created demo.
- PR #3725 — symbol-only recipe resolution over the fragment index.
- PR #3734 — surgical recipe operations and edit flow.
- PR #3749 — extraction record and lineage condition.

These are material prior art inside this repository. MOSAIC Brain must not reimplement their pointer/index/edit primitives. Its distinct layer is the higher-order capability model: purpose, contracts, ingredients, execution environment, evaluation, learning and lifecycle. Integration should use adapters and typed references to the replay system.

### 8.4 Data flow

```text
Repository / Corpus / APIs / Runs
             |
        READ-ONLY EXTRACT
             |
     Normalize + provenance
             |
       SRM validation
             |
  +----------+-----------+
  |          |           |
Classify  Similarity   Graph build
  |          |           |
  +----------+-----------+
             |
       Recipe retrieval
             |
    Contract-aware composition
             |
     Policy / admission check
             |
    Isolated execution adapter
             |
      Receipts + telemetry
             |
    Evaluation + DoE analysis
             |
  Append-only learning / revisions
```

---

## 9. Execution, security and trust model

### 9.1 Progressive authority

- P0/P1: read-only extraction and analysis.
- P2: graph and recommendation, no execution.
- P3: sandboxed execution of explicitly admitted recipes.
- P4: bounded automated revision proposals and experiments.
- Production promotion remains governed by existing independent policy and review.

### 9.2 Hard constraints

- Never store secret values in recipe records, embeddings, logs, or graph attributes.
- Untrusted source text, issue bodies, comments, prompts, and tool output remain data—not policy.
- No recipe may grant itself permissions or modify governance roots.
- Destructive or external side effects require explicit policy admission.
- Retry only idempotent operations or those with a declared idempotency contract.
- Timeouts, resource limits, network egress, and artifact retention are explicit.
- A failed, partial, stale, unavailable, or unverified result cannot be upgraded to pass.
- Model output cannot override deterministic policy.
- No self-approval, self-merge, secret provisioning, production deploy, or autonomous promotion is introduced by this proposal.
- All execution is attributable to an immutable recipe revision and execution receipt.

### 9.3 Reproducibility levels

- R0 — descriptive only; environment unknown.
- R1 — inputs and declared dependencies recorded.
- R2 — toolchain and environment pinned.
- R3 — isolated replay produces equivalent declared outputs.
- R4 — independently reproducible by a separate execution lane.

A recipe's reproducibility level is evidence-derived and scoped to a tested revision.

---

## 10. DoE versioning competition

### 10.1 Competition question

Which representation and analysis strategy yields the best verified utility for discovering, classifying, comparing, composing, and maintaining software capabilities?

### 10.2 Candidate arms

- **A0 Baseline:** repository search + existing metadata; no SRM.
- **A1 SRM-Rule:** canonical recipe schema + deterministic extraction and rules.
- **A2 SRM-Stat:** A1 + TF-IDF/logistic-regression multi-label classifier and calibrated confidence.
- **A3 SRM-Graph:** A2 + typed graph and weighted ingredient/structural similarity.
- **A4 SRM-Hybrid:** A3 + embeddings and semantic reranking, with abstention.
- **A5 SRM-Execution:** A4 + execution receipts and outcome-conditioned evaluation (only after safety admission).

Do not assume the most complex arm wins. The baseline remains a valid candidate.

### 10.3 Factor candidates

- Representation: file-centric / recipe-centric / hybrid.
- Feature set: lexical / structural / ingredient / contract / runtime / combined.
- Classifier: rules / logistic regression / tree / calibrated ensemble.
- Similarity: token / ingredient overlap / AST / graph / embedding / hybrid.
- Provenance: minimal / full immutable lineage.
- Evaluation: static fixtures / held-out repository tasks / replayed execution.

### 10.4 Blocking and controls

Block by repository/language, capability family, task difficulty, and source age. Split train/test by repository or time where possible to prevent leakage. Freeze corpus snapshots, feature extraction versions, prompts, model versions, and thresholds. Use the same task set and budget per arm. Randomize assignment within blocks. Record every dispatched run as one observation with source SHA, trigger, arm, config, and result.

### 10.5 Primary outcomes

1. Correct top-k recipe retrieval against adjudicated relevance.
2. Multi-label classification macro/micro F1 and calibration.
3. Duplicate detection precision/recall with human-reviewed false positives.
4. Contract compatibility precision (unsafe false-positive rate is a hard constraint).
5. Change-impact recall and precision.
6. Reproducibility success rate on eligible recipes.

Secondary: tokens, elapsed time, compute, cost, graph build time, index size, rework, review burden, false abstentions, and maintenance overhead.

### 10.6 Governance and promotion

- Delphi admission score is an admission signal, not proof of utility.
- DoE outcome is determined by predeclared metrics and verified run evidence.
- Keep each component's evaluation separate; do not hide a weak component inside an aggregate.
- Use held-out confirmation for candidate winners.
- A candidate winner becomes a recommendation, not an automatic production promotion.
- Preserve no-change, inconclusive, unavailable, and failed outcomes.
- Keep proposal authors, builders, evaluators, and approvers distinct where the current governance contract requires it.

---

## 11. Delivery roadmap — SRM work packages

### SRM-000 — Charter and identity
Freeze program identity, namespace, ownership, collision rules, scope and non-goals. Deliver naming registry and decision record.

### SRM-001 — Canonical model
Define SRM v1 entities, required fields, optionality, unknown states, canonicalization and compatibility rules.

### SRM-002 — Schema and validation
Publish JSON Schema, golden fixtures, negative fixtures, schema-version policy and validator.

### SRM-003 — Taxonomy and notation
Publish hierarchical multi-label taxonomy, reserved IDs, aliases, status vocabulary, typed operator notation and examples.

### SRM-004 — Provenance and revision identity
Define immutable revision digests, source refs, derivation, signature/attestation hooks and append-only history.

### SRM-005 — Extraction adapters
Implement read-only Git/repository, manifest, workflow, test, documentation, issue/PR and telemetry extractors. Emit source locations and parser confidence.

### SRM-006 — Structural analysis
Add Tree-sitter and language-specific AST providers; preserve parser/provider versions and parse gaps.

### SRM-007 — Classification baseline
Implement deterministic rules and a statistical baseline; establish labeled corpus and train/test split.

### SRM-008 — Similarity and duplicate detection
Implement lexical, ingredient, structural and contract similarity; produce ranked candidates with evidence and abstention.

### SRM-009 — Typed relationship graph
Build graph nodes/edges, integrity constraints, provenance, incremental updates and graph snapshots.

### SRM-010 — Retrieval and composition
Implement retrieval, dependency planning, contract checks, conflict detection and substitution proposals.

### SRM-011 — Evaluation and receipts
Define execution receipt, test/evaluation contracts, runtime evidence, reproducibility levels and baseline comparisons.

### SRM-012 — DoE competition
Run blocked experiments, publish results, evaluate uncertainty, compare arms, record winner/loser/inconclusive dispositions.

### SRM-013 — Sandboxed execution
Only after explicit admission: run selected recipes in constrained environments with immutable inputs and bounded side effects.

### SRM-014 — Evolution and memory
Create revision proposals from evidence, compare variants, append findings, support rollback/supersession and controlled learning.

### SRM-015 — Operational integration
Integrate approved projections into SHE, Historical Corpus, Context Relationship Graph, ATES/MoneyBall and governance feeds.

---

## 12. Acceptance criteria

### Foundation
- Every recipe validates against a pinned schema version.
- Stable identity is independent of display title and file path.
- Revisions are immutable and content-addressable.
- Unknown and unavailable values remain explicit.
- No secret values are accepted by schema or ingestion.

### Extraction
- Every extracted field has source path, immutable source ref, extractor version and evidence class.
- Parser failure is reported; no fabricated semantic completion.
- Re-running extraction against the same immutable source and tool version is deterministic where the provider claims determinism.

### Classification and retrieval
- Baseline metrics are reported by label and task family.
- Calibration and abstention are measured.
- Similarity never implies compatibility or equivalence.
- False-positive duplicate/compatibility rates are explicitly reported.

### Graph
- Every edge type is registered and validated.
- No dangling references in a published snapshot.
- Incremental graph updates reconcile against full rebuild fixtures.
- Historical edges are not silently rewritten.

### Execution
- Every run binds to recipe revision, environment, inputs, outputs, and evidence.
- Unsafe operations fail closed.
- Reproducibility claims are backed by independent replay evidence.
- Failed or unavailable runs are not promoted to pass.

### DoE
- Factors, levels, blocks, outcomes, exclusion rules, and analysis are preregistered.
- Source snapshots and configurations are immutable.
- Results include uncertainty, negative outcomes and limitations.
- Winner selection requires held-out confirmation.

### Governance
- No automatic merge, deploy, secret provisioning or permission expansion.
- Proposal, implementation, evaluation and promotion are separate records.
- Every promoted revision links to its accepted evidence and authorizing decision.

---

## 13. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Recipe metaphor becomes vague | Strict schema, typed operations and contracts |
| Duplicate of existing replay engines | Reuse Commit Replay/Repo Replay primitives; MOSAIC Brain stays at capability-model layer |
| Taxonomy drift | Versioned taxonomy, aliases, deprecation and migration rules |
| Model hallucination | Evidence-bearing predictions, abstention, deterministic validation |
| Similarity mistaken for equivalence | Separate edge types and contract-backed compatibility |
| Data leakage through embeddings | Secret scrubbing, sensitivity classes, access-aware indexing |
| Graph explosion | Incremental extraction, edge budgets, scoped projections |
| Non-reproducible execution | Pinned environments, receipts, independent replay |
| Evaluation gaming | Held-out sets, predeclared metrics, independent evaluator |
| Unsafe autonomy | Progressive authority and explicit policy gates |
| Schema lock-in | JSON Schema, canonical JSON, exportable records, migration tooling |
| Stale lineage | Immutable refs and freshness status; never infer currentness |

---

## 14. Decision requested

Admit `mosaic_brain.recipe_model` as a **research/design candidate** for DoE evaluation, with initial authority restricted to read-only extraction and analysis.

Requested next decisions:
1. Accept or reject the MOSAIC Brain naming/identity proposal.
2. Accept SRM v1 as a candidate schema contract or request competing variants.
3. Register the surface for independent Delphi/DoE review.
4. Approve the bounded baseline experiment, not execution authority.
5. Require explicit overlap review against Commit Replay, Repo Replay, the existing Context Relationship Graph, and the existing DoE component registry before implementation promotion.

**No-change is an acceptable outcome.** If an existing system already satisfies a requirement, MOSAIC Brain should reference it rather than duplicate it.

---

## 15. Sources and inspiration

The proposal's conceptual inspiration and technical foundations are documented in `SOURCES.md`. The central transfer is not that software literally is food; it is that recipes demonstrate how composition, ingredients, ordered procedure, environment, outputs, and evaluation can be modeled together. Research on recipe classification and recipe similarity networks supplies testable methods for feature engineering and graph analysis. Software engineering standards and tools supply the formal contracts and provenance needed to make the analogy operational.

---

## 16. Version history

- 0.1.0-draft — initial independent proposal; no implementation authority.
