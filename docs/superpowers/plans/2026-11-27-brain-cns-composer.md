# Brain/CNS Composer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic Brain/CNS-inspired Composer and pure coordination modules to PR #5939.

**Architecture:** Small pure Python modules under `deepcli/deepcli/observatory/brain/`. Composer consumes the existing Ballet plan and delegates cue generation to Conductor. It returns declarative data while control-plane authority remains with current owners.

**Tech Stack:** Python standard library, unittest, existing Observatory modules.

**Spec:** `docs/superpowers/specs/2026-11-27-brain-cns-composer-design.md`

## Global Constraints

- Preserve dependency-phase readiness, QUE admission and claims, specialist-adapter execution, and ATES evidence authority.
- Composer returns declarative data through pure transformations.
- Identical normalized inputs and policy version produce identical score content and score ID.
- Signal confidence remains descriptive metadata; control-plane policy governs authorization.
- Timing feedback and wake selection remain observational recommendations.
- Keep Python implementation within the standard library.
- Cite `Implements: RS-006` in commits and PR metadata.

## Review Focus

- Conflicting duplicate signal IDs fail with a clear validation error.
- Context truncation preserves explicit episode evidence references and every focused signal record within the context budget.
- Candidate selection stays deterministic under equal priorities and overlapping write paths.
- Past event/window boundaries yield a future wake recommendation.
- Cue-sheet compilation preserves dependency IDs and temporal/evidence metadata.
- Timing feedback resolves a canonical ATES receipt envelope plus task_id and actual_duration_ms; the resolver return shape is specified in the design doc.
- Composer derives expected_duration_ms from the assignment and verifies the resolved task ID before calculating drift.
- The plan distinguishes the implemented pure library contract from the follow-on production workflow caller.
- A mismatched receipt resolver result or task identity fails closed.
- Expected duration comes from the assignment; actual duration comes from the resolved canonical receipt payload.
- Composer score identity captures attention policy and focus budget, action-selection policy version and max_parallel, including cases where the resulting shortlist remains equal.

---

### Task 1: Signal intake, attention, context, and executive intent

**Files:** create `deepcli/deepcli/observatory/brain/{__init__,signals,attention,context,executive}.py`; test `deepcli/tests/test_brain_system.py`.

**Interfaces:** `normalize_signals(signals)`; `build_context(signals, episodes=(), max_items=64)`; `normalize_intent(intent)`.

- [ ] Write tests for ordering, identical deduplication, conflicting duplicate rejection, confidence bounds, bounded attention ranking and focus-budget identity, evidence retention, truncation, goal validation, and priority range.
- [ ] Run the focused test file; expected: imports fail before module creation.
- [ ] Implement the pure modules and public exports.
- [ ] Run focused tests; expected: Task 1 assertions pass.

### Task 2: Action selection, prediction error, and homeostasis

**Files:** create `action_selection.py`, `prediction.py`, and `homeostasis.py` in the Brain package; extend `test_brain_system.py`.

**Interfaces:** `select_actions(candidates, max_parallel=1)`; `timing_error(expected_duration_ms, actual_duration_ms)`; `plan_wake(now_ms, event_deadline_ms=None, window_close_ms=None, max_wait_ms=60000)`.

- [ ] Write tests for priority ordering, write conflicts, invalid candidate IDs, signed timing drift, negative/non-finite values, and earliest future wake boundary.
- [ ] Run focused tests; expected: missing module imports fail before implementation.
- [ ] Implement pure helpers with deterministic ordering and explicit validation.
- [ ] Run focused tests; expected: Task 2 assertions pass.

### Task 3: Composer and Conductor integration

**Files:** create `brain/composer.py`; modify `deepcli/deepcli/observatory/conductor.py`, `deepcli/deepcli/observatory/__init__.py`, and `deepcli/tests/test_conductor.py`.

**Interfaces:** Composer consumes normalized intent, signals, context, existing `ConductorPlacement`, and `build_cue_sheet`; it wires `select_actions`, `timing_error`, and `plan_wake` through optional action candidates, timing observations, and wake context.

- [ ] Write tests for deterministic score identity, score schema, authority map, cue metadata preservation, action shortlisting, timing feedback, and wake recommendations.
- [ ] Run tests; expected: cue metadata regression fails against current Conductor output.
- [ ] Update Conductor task records to include phase, open length, dependency barriers, evidence references, dependency IDs, and wake conditions.
- [ ] Implement deterministic Composer score and canonical SHA-256 score ID.
- [ ] Run focused tests; expected: Composer and Conductor contracts pass.

### Task 4: Proposal integration and verification

**Files:** update `docs/ops/RHYTHMIC-SYSTEMS-TEMPORAL-INTELLIGENCE.md`, proposal `ITEMS.md` and `MANIFEST.md`; create this design and plan; export Brain functions from the Observatory package.

- [ ] Register RS-006 with acceptance evidence and update architecture/specification links.
- [ ] Run `python -m unittest discover -s tests -v` from `deepcli/`; expected: focused Observatory tests pass.
- [ ] Run `python -m compileall -q deepcli tests` from `deepcli/`; expected: exit 0.
- [ ] Run repository gate, Siglary validator, and Termux smoke on the exact pushed SHA.
- [ ] Commit with `docs(brain): register Composer architecture Implements: RS-006`.

## Review and release

- Verify all files and the exact branch SHA after each remote commit.
- Re-fetch PR #5939 checks and review threads after the final commit.
- Resolve only review findings proven addressed by the new tests and code.
- Keep PR #5939 open until required checks and existing critical review findings are dispositioned.
