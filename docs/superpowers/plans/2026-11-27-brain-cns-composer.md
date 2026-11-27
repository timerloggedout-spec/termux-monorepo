# Brain/CNS-Inspired Composer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, auditable Composer that compiles explicit intent into Ballet plans and Conductor cue sheets without taking over execution authority.

**Architecture:** Add one focused Python module that composes existing Observatory primitives. Keep the broader CNS-inspired module taxonomy in architecture documentation; each conceptual module has a narrow contract and existing owner. Publish a versioned JSON Schema for the score and test the compiler with the existing unittest conventions.

**Tech Stack:** Python 3.11+ standard library, dataclasses, typing, json, unittest; existing `deepcli.observatory.ballet` and `deepcli.observatory.conductor`.

**Spec:** `docs/superpowers/specs/2026-11-27-brain-cns-composer-design.md`

## Global Constraints

- Dependency-phase engine owns readiness and dependency barriers.
- Ballet owns deterministic dependency-wave planning.
- QUE owns admission, queue priority, claims, and lifecycle.
- Specialist adapters own execution.
- ATES owns canonical evidence validation and provenance.
- Temporal Intelligence owns assignment windows, phase, cadence, wake, and drift semantics.
- Conductor emits cue sheets and dispatch intent through existing control planes.
- Composer owns only intent normalization, score composition, and decision trace.
- Output authority is `dispatch_intent_only`.
- Keep all runtime dependencies in the Python standard library.
- Commits and PR description cite `Implements: BCC-001`.

## Review Focus

- Duplicate task IDs, unknown dependencies, and dependency cycles: assert rejection or Ballet's canonical validation.
- Missing or malformed assignments and cue metadata: assert actionable errors before any score is emitted.
- Different dictionary insertion orders: assert canonical score equality.
- Caller-supplied context/evidence references: assert exact preservation and no synthesized provenance.
- Dispatch boundary: assert the score remains intent-only and exposes no execution/claim mutation operation.

---

### Task 1: Add the Composer contract and deterministic compiler

**Files:**
- Create: `deepcli/deepcli/observatory/composer.py`
- Modify: `deepcli/deepcli/observatory/__init__.py`
- Test: `deepcli/tests/test_composer.py`

**Interfaces:**
- `ComposerIntent(intent_id: str, objective: str, tasks: tuple[Mapping[str, Any], ...], success_criteria: tuple[str, ...], context_refs: tuple[str, ...] = ())`
- `ComposerPolicy(version: str = "composer.policy.v1", placement: ConductorPlacement = ConductorPlacement.TEMPORAL_INTELLIGENCE, strategy: str = "adaptive", max_parallel: int | None = None)`
- `compose_score(intent: ComposerIntent, assignments: Mapping[str, Mapping[str, Any]], policy: ComposerPolicy = ComposerPolicy()) -> dict[str, Any]`
- Consumes existing `plan_choreography` and `build_cue_sheet`; no new scheduler or dispatch API.

- [ ] **Step 1: Write failing tests** for minimal score composition, preservation of context and success criteria, intent-only authority, and exact cue coverage.
- [ ] **Step 2: Run RED** with `cd deepcli && python -m unittest tests.test_composer -v`; expected failure because `composer` is absent.
- [ ] **Step 3: Implement** immutable input dataclasses, validation, Ballet delegation, Conductor delegation, and a JSON-compatible deterministic score.
- [ ] **Step 4: Run GREEN** for the focused tests, then run `cd deepcli && python -m unittest discover -s tests -v`.
- [ ] **Step 5: Commit** with `feat(composer): compile intent into auditable cue scores Implements: BCC-001`.

### Task 2: Pin input validation, determinism, and ownership boundaries

**Files:**
- Modify: `deepcli/deepcli/observatory/composer.py`
- Test: `deepcli/tests/test_composer.py`

**Interfaces:** Task 1 interfaces remain stable.

- [ ] **Step 1: Add failing tests** for blank IDs/objectives, empty success criteria, duplicate IDs, invalid policy values, invalid parallel capacity, missing assignment metadata, unknown dependencies, non-JSON-compatible context, and insertion-order-independent score output.
- [ ] **Step 2: Run RED** on the named tests and confirm each fails for its intended reason.
- [ ] **Step 3: Implement** the smallest explicit validation needed; preserve Ballet and Conductor as canonical validators for their domains.
- [ ] **Step 4: Run GREEN** for focused tests and the complete Observatory suite.
- [ ] **Step 5: Commit** with `test(composer): enforce deterministic score and authority contracts Implements: BCC-001`.

### Task 3: Publish the score schema and architecture map

**Files:**
- Create: `docs/schemas/composer.score.v1.schema.json`
- Create: `docs/architecture/BRAIN-CNS-COMPOSER.md`
- Create: `docs/architecture/BRAIN-CNS-COMPOSER.mmd`

**Interfaces:**
- Schema top-level fields: `schema_version`, `intent`, `policy`, `plan`, `cue_sheet`, `context_refs`, `success_criteria`, `decision_trace`, `authority`.
- Schema version literal: `composer.score.v1`.
- Architecture map identifies sensory gateway, relay, context memory, executive planner, salience annotation, temporal predictor, coordinator, motor interface, homeostasis monitor, and error-correction loop as analogy-labeled modules with explicit ownership.

- [ ] **Step 1: Write schema validation tests** using Python's standard-library JSON parser and structural assertions for required fields and authority marker.
- [ ] **Step 2: Run RED** and confirm schema artifact is missing.
- [ ] **Step 3: Add** JSON Schema draft 2020-12 with required properties, enums, and `additionalProperties: false` at the score envelope.
- [ ] **Step 4: Add** architecture docs and Mermaid source; describe analogies as analogies and show the existing authority boundaries.
- [ ] **Step 5: Run GREEN** for schema structure and Mermaid syntax sanity checks; inspect every documented owner against the design.
- [ ] **Step 6: Commit** with `docs(composer): document CNS-inspired coordination modules Implements: BCC-001`.

### Task 4: Add an end-to-end Composer example and public exports

**Files:**
- Create: `deepcli/examples/composer_score.py` (or the existing examples directory if repository inspection identifies a different canonical path)
- Modify: `deepcli/deepcli/observatory/__init__.py`
- Test: `deepcli/tests/test_composer.py`

**Interfaces:** Import `ComposerIntent`, `ComposerPolicy`, and `compose_score` from `deepcli.observatory`.

- [ ] **Step 1: Add failing export and example contract tests.**
- [ ] **Step 2: Run RED** and confirm the public import/example contract fails.
- [ ] **Step 3: Export** the three public Composer symbols and add a small offline example that prints canonical JSON.
- [ ] **Step 4: Run GREEN** for import/example tests and the full Observatory suite.
- [ ] **Step 5: Commit** with `feat(composer): expose score compiler example Implements: BCC-001`.

### Task 5: Final verification and review

**Files:**
- Review all files above.
- Run repository-prescribed gates on the exact candidate SHA.

- [ ] **Step 1:** Run `cd deepcli && python -m unittest discover -s tests -v`.
- [ ] **Step 2:** Run Python compile checks for the touched package and tests.
- [ ] **Step 3:** Run repository gates: `python3 scripts/ci/repo_gate.py`, `python3 scripts/ci/validate_siglary_mandate.py --base origin/master`, `python3 scripts/ci/termux_smoke.py`, and proposal-lifecycle validation where available.
- [ ] **Step 4:** Inspect the exact diff and verify all commits cite `Implements: BCC-001`.
- [ ] **Step 5:** Request independent review; resolve Critical and Important findings with TDD.
- [ ] **Step 6:** Report exact SHA, tests, gates, review status, and remaining blockers. Preserve the branch for review; do not merge without the required promotion evidence.
