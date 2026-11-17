# ORBIT × SHIELD Provider Arbitration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an observe-only SHIELD context-admission layer and ORBIT dual-accumulator decision layer over the existing provider/endpoint and agent execution populations.

**Architecture:** Add pure stdlib Python helpers for context admission and candidate arbitration, then adapt the existing AR-18 decision envelope in `scripts/model_router.py`. Provider and model identity continue to come from existing registries/catalogs/adapters; this work does not create a competing provider registry or enable new provider invocations.

**Tech Stack:** Python stdlib, pytest, existing GitHub Actions validation.

**Spec:** `docs/superpowers/specs/2026-11-17-orbit-shield-provider-arbitration-design.md`

## Global Constraints

- Reuse `ops/challenge/desk-feed.json`, `ops/quota/registry.json`, reviewed adapter registries, and existing catalog feeds as authoritative inputs.
- A provider×model pair is an endpoint identity; provider brands, agent identities, adapters, and manager policies remain distinct.
- Catalog discovery does not prove a callable endpoint, credentials, authentication, health, quota, or successful inference.
- ORBIT applies hard gates before benefit/risk scoring; failed gates cannot be offset by scores.
- SHIELD does not create a new memory store; reuse `agent-context-store` and the context relationship graph.
- First rollout is observe-only; existing selected provider/model and execution side effects remain unchanged.
- Never emit secrets, raw prompts/completions, cookies, session IDs, or unrestricted context payloads.
- Unknown or missing evidence remains null/unknown, not zero or success.

## Review Focus

- Duplicate provider/model aliases or duplicate endpoint identities must not create duplicate eligible candidates.
- Stale, missing, or catalog-only endpoint evidence must be visible but never invocation-eligible.
- Empty, malformed, or oversized task context must fail closed without crashing the router.
- Prompt-injection-like instructions and secret-bearing fields must be quarantined or denied, never admitted as trusted context.
- Risk/benefit ties and missing uncertainty data must defer rather than choose arbitrarily.

---

### Task 1: SHIELD context capsule and admission policy

**Files:**
- Create: `scripts/shield_context.py`
- Test: `tests/test_shield_context.py`

**Interfaces:**
- Produces: `build_capsule(task: dict, signals: list[dict], max_items: int = 24, max_chars: int = 12000) -> dict`
- Produces: `classify_signal(signal: dict) -> dict`
- Capsule dispositions: `admit`, `quarantine`, `defer`, `escalate`.
- No file, network, environment, or persistence access.

- [ ] **Step 1: Write failing tests** for trusted relevant admission, untrusted/instruction-bearing quarantine, secret-key denial, irrelevant deferral, critical escalation, item/character budget bounds, and stable source-reference preservation.
- [ ] **Step 2: Run the focused tests** with `python3 -m pytest tests/test_shield_context.py -q`; expected RED is import/API failure.
- [ ] **Step 3: Implement the pure SHIELD helpers** with explicit allowlisted metadata and bounded text accounting; never echo secret values or raw untrusted content into the capsule.
- [ ] **Step 4: Re-run focused tests**; expected PASS.
- [ ] **Step 5: Commit** `feat(shield): add bounded task context admission`.

### Task 2: ORBIT dual-accumulator arbitration

**Files:**
- Create: `scripts/orbit_arbitration.py`
- Test: `tests/test_orbit_arbitration.py`

**Interfaces:**
- Produces: `arbitrate(candidates: list[dict], threshold: float = 0.10, max_candidates: int = 128) -> dict`
- Candidate fields include endpoint/specialist identity, capability, hard-gate states, benefit factors, risk/cost factors, and evidence references.
- Decision states: `SELECT`, `DEFER`, `VETO`; output exposes separate benefit and risk/cost accumulators, margin, exclusions, and policy version.

- [ ] **Step 1: Write failing tests** for hard-gate veto, stale/catalog-only deferral, benefit-over-risk selection, tie/uncertainty deferral, deterministic ordering, candidate cap, duplicate identity rejection, and missing-value semantics.
- [ ] **Step 2: Run focused tests** with `python3 -m pytest tests/test_orbit_arbitration.py -q`; expected RED is import/API failure.
- [ ] **Step 3: Implement deterministic pure arbitration**; hard-gate failures never receive a selectable score, and unknown evidence is not coerced to zero.
- [ ] **Step 4: Re-run focused tests**; expected PASS.
- [ ] **Step 5: Commit** `feat(orbit): add dual-accumulator arbitration`.

### Task 3: Integrate SHIELD and ORBIT into the existing observe envelope

**Files:**
- Modify: `scripts/model_router.py`
- Modify: `scripts/capability_spine.py` only if required to preserve the existing envelope
- Modify: `tests/test_model_router.py`
- Test: existing `tests/test_capability_spine.py`

**Interfaces:**
- Consumes Task 1 `build_capsule` and Task 2 `arbitrate`.
- Existing `emit_decision(...)` remains the AR-18 integration point.
- Existing provider/model execution selection remains unchanged; ORBIT result is an additional observe-only output.

- [ ] **Step 1: Write failing integration tests** proving SHIELD capsule and ORBIT decision are emitted, the current provider/model/skip outputs remain identical, disabling observe mode disables only the advisory envelope, and catalog-only/unconfigured candidates cannot be selected by ORBIT.
- [ ] **Step 2: Run focused router/capability tests**; expected RED is missing output/fields.
- [ ] **Step 3: Integrate the pure helpers** into `emit_decision`; preserve existing candidate and execution code paths.
- [ ] **Step 4: Run focused tests** for model router, capability spine, SHIELD, and ORBIT; expected PASS.
- [ ] **Step 5: Commit** `feat(router): observe SHIELD and ORBIT decisions`.

### Task 4: Registry semantics, proposal record, and validation

**Files:**
- Modify: `docs/proposals/active/continuous-capability-evolution-lab/ITEMS.md`
- Create: `docs/ops/ORBIT-SHIELD-ARCHITECTURE.md`
- Modify: `docs/ops/AGENT-TEAM-ORCHESTRATION.md` only for the canonical pointer
- Test: relevant docs/schema or contract tests if the repo already owns them

- [ ] **Step 1: Add CCEL-007 and CCEL-008** with acceptance criteria distinguishing catalog visibility from verified invocation.
- [ ] **Step 2: Document endpoint evidence states and the SHIELD/ORBIT control boundary** without duplicating the provider registry.
- [ ] **Step 3: Run proposal validation, repo gate, Termux smoke, and the full relevant pytest suite** through the PR's existing Actions checks.
- [ ] **Step 4: Re-fetch the exact PR head, check runs, jobs, and logs**; report success only for terminal successful checks on that SHA.
- [ ] **Step 5: Commit** `docs(agents): record ORBIT and SHIELD control contracts`.

## Validation commands

```bash
python3 -m pytest tests/test_shield_context.py tests/test_orbit_arbitration.py tests/test_model_router.py tests/test_capability_spine.py -q
python3 scripts/proposals/validate_registry.py
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```

A full checkout and local shell are unavailable in this session; GitHub Actions on the PR head are the execution evidence. Do not claim a test passed until its actual run output is inspected.

## Delivery boundary

Open a draft PR against `master` after the RED tests are committed, observe the expected test failure, then add implementation commits. Keep the PR open and unmerged. No production routing switch, provider probing, paid inference, credential mutation, auto-merge, or deployment.
