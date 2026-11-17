# ORBIT × SHIELD Provider Arbitration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an observe-only SHIELD context-admission layer and ORBIT dual-accumulator decision layer over the canonical 93-provider dispatch population.

**Architecture:** Add pure stdlib Python helpers for context admission and candidate arbitration, project provider identities and evidence from the existing desk-feed/G4F catalogs, then integrate the observe-only result at `scripts/ops/provider_invoke.py`. The provider-invoke route remains manually admitted and unchanged. `scripts/model_router.py` remains a separate role-peer router, not the global provider registry.

**Tech Stack:** Python stdlib, unittest, existing GitHub Actions validation.

**Spec:** `docs/superpowers/specs/2026-11-17-orbit-shield-provider-arbitration-design.md`

## Global Constraints

- Reuse `ops/challenge/desk-feed.json`, `ops/quota/registry.json`, reviewed adapter registries, and G4F catalog evidence as authoritative inputs.
- Preserve the distinct counts and evidence grades: 93 model-lane provider keys in the dispatch class breakdown; 92/93 invoke surfaces; 7,341 provider×model endpoint verified floor; separate G4F universe of 160 providers / 9,588 pairs; 160 sandbox-verified pairs and 83 Actions-verified pairs.
- A provider×model pair is an endpoint identity; provider brands, agent identities, adapters, and manager policies remain distinct.
- Catalog discovery does not prove callable inference, credentials, authentication, health, quota, or current entitlement.
- ORBIT applies hard gates before benefit/risk scoring; failed gates cannot be offset by scores.
- SHIELD does not create a new memory store; reuse existing context-store and relationship-graph owners.
- First rollout is observe-only; existing provider, model, prompt, and execution side effects remain unchanged.
- Never emit secrets, raw prompts/completions, cookies, session IDs, or unrestricted context payloads.
- Unknown or missing evidence remains null/unknown, not zero or success.

## Review Focus

- Duplicate provider/model aliases or duplicate endpoint identities must not create duplicate eligible candidates.
- Stale, missing, or catalog-only endpoint evidence must be visible but never invocation-eligible.
- Empty, malformed, or oversized task context must fail closed without crashing the invocation script.
- Prompt-injection-like instructions and secret-bearing fields must be quarantined, never admitted as trusted context.
- Risk/benefit ties, truncated candidate populations, and missing uncertainty data must defer rather than choose arbitrarily.

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

- [x] **Step 1: Write failing tests** for trusted relevant admission, untrusted/instruction-bearing quarantine, secret-key denial, irrelevant deferral, critical escalation, item/character budget bounds, and stable source-reference preservation.
- [x] **Step 2: Run RED through the Termux smoke workflow**; expected result is ImportError because `scripts/shield_context.py` does not yet exist.
- [x] **Step 3: Implement the pure SHIELD helpers** with explicit allowlisted metadata and bounded text accounting; never echo secret values or raw untrusted content into the capsule.
- [x] **Step 4: Run the focused unittest suite** through the same workflow; expected PASS.
- [x] **Step 5: Commit** `feat(shield): add bounded task context admission`.

### Task 2: ORBIT dual-accumulator arbitration

**Files:**
- Create: `scripts/orbit_arbitration.py`
- Test: `tests/test_orbit_arbitration.py`

**Interfaces:**
- Produces: `arbitrate(candidates: list[dict], threshold: float = 0.10, max_candidates: int = 128) -> dict`
- Candidate fields include endpoint/specialist identity, capability, hard-gate states, benefit factors, risk/cost factors, and evidence references.
- Decision states: `SELECT`, `DEFER`, `VETO`; output exposes separate benefit and risk/cost accumulators, margin, exclusions, and policy version.

- [x] **Step 1: Write failing tests** for hard-gate veto, stale/catalog-only deferral, benefit-over-risk selection, tie/uncertainty deferral, deterministic ordering, candidate cap, duplicate identity rejection, and missing-value semantics.
- [x] **Step 2: Run RED through the Termux smoke workflow**; expected result is ImportError because `scripts/orbit_arbitration.py` does not yet exist.
- [x] **Step 3: Implement deterministic pure arbitration**; hard-gate failures never receive a selectable score, and unknown evidence is not coerced to zero.
- [x] **Step 4: Run the focused unittest suite** through the same workflow; expected PASS.
- [x] **Step 5: Commit** `feat(orbit): add dual-accumulator arbitration`.

### Task 3: Canonical provider-population projection

**Files:**
- Create: `scripts/orbit_provider_population.py`
- Test: `tests/test_orbit_provider_population.py`

**Interfaces:**
- Produces: `build_population(feed: dict, g4f_working: dict | None = None) -> dict`
- Produces: `load_population(repo_root: Path | None = None) -> dict`
- Produces: `as_orbit_candidates(population: dict) -> list[dict]`
- Reads existing desk-feed and G4F working evidence; creates no new source-of-truth registry and performs no provider requests.

- [x] **Step 1: Write failing tests** for provider-name deduplication, 93-provider population coverage, 92/93 route classification, 7,341 endpoint census floor, separate G4F sandbox/Actions evidence, and unknown score preservation.
- [x] **Step 2: Run RED through the Termux smoke workflow**; expected result is ImportError because the projection module does not yet exist.
- [x] **Step 3: Implement the read-only projection** from `dispatch.provider_catalog.inference_availability`, `inference_wiring`, `endpoint_census`, and `data/g4f-working/working-endpoints.json`.
- [x] **Step 4: Convert provider routes into ORBIT candidates** with endpoint registration evidence and null task-fit/benefit/risk fields where the source cannot establish them. The initial full-population result should DEFER, not fabricate a winner.
- [ ] **Step 5: Run the focused unittest suite** through the same workflow; expected PASS.
- [x] **Step 6: Commit** `feat(orbit): project canonical provider population`.

### Task 4: Observe-only provider-invoke integration

**Files:**
- Modify: `scripts/ops/provider_invoke.py`
- Create: `tests/test_provider_invoke_control_plane.py`
- Modify: `.github/workflows/termux-smoke.yml`

**Interfaces:**
- Consumes Task 1 `build_capsule`, Task 2 `arbitrate`, and Task 3 `load_population` / `as_orbit_candidates`.
- Adds a compact `control_plane` observation to `INVOKE_VERDICT` and `CATALOG_VERDICT`.
- The manually selected provider/model, prompt body, HTTP call count, retry behavior, and completion output remain unchanged.

- [ ] **Step 1: Write failing integration tests** proving the provider population and ORBIT DEFER result are attached, SHIELD emits only capsule metadata/counts, no prompt/token content appears in the verdict, and the existing invocation inputs are unchanged.
- [ ] **Step 2: Run RED through the Termux smoke workflow**; expected result is missing `control_plane` output.
- [x] **Step 3: Integrate the observe-only helpers** before invocation; retain the original prompt and route without transformation or additional provider calls.
- [x] **Step 4: Add the new test module to the existing offline Termux smoke test steps.**
- [ ] **Step 5: Run all SHIELD, ORBIT, provider-population, provider-invoke, repo-gate, and Termux smoke checks**; expected PASS on the same PR head SHA.
- [ ] **Step 6: Commit** `feat(provider-invoke): observe SHIELD and ORBIT decisions`.

### Task 5: Architecture record and validation

**Files:**
- Modify: `docs/proposals/active/continuous-capability-evolution-lab/ITEMS.md`
- Create: `docs/ops/ORBIT-SHIELD-ARCHITECTURE.md`
- Modify: `docs/ops/AGENT-TEAM-ORCHESTRATION.md` only for the canonical pointer

- [x] **Step 1: Preserve CCEL-007 and CCEL-008** acceptance criteria distinguishing catalog visibility from verified invocation.
- [x] **Step 2: Document the 93-provider population, endpoint evidence grades, SHIELD/ORBIT boundaries, and why Gemini/OpenRouter/Jules are not the provider universe.**
- [ ] **Step 3: Run proposal validation, repo gate, Termux smoke, and the provider-invoke contract suite through existing Actions checks.**
- [ ] **Step 4: Re-fetch the exact PR head, check runs, jobs, and logs**; report success only for terminal successful checks on that SHA.
- [ ] **Step 5: Commit** `docs(agents): record ORBIT and SHIELD control contracts`.

## Validation commands

```bash
python3 -B -m unittest discover -s tests -p 'test_shield_context.py' -v
python3 -B -m unittest discover -s tests -p 'test_orbit_arbitration.py' -v
python3 -B -m unittest discover -s tests -p 'test_orbit_provider_population.py' -v
python3 -B -m unittest discover -s tests -p 'test_provider_invoke_control_plane.py' -v
python3 scripts/proposals/validate_registry.py
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```

A local Termux MCP session and a local repository checkout are unavailable in this conversation; GitHub Actions on the PR head are the execution evidence. Do not claim a test passed until its actual run output is inspected.

## Delivery boundary

The draft PR remains open and unmerged. No production routing switch, provider probing, paid inference, credential mutation, auto-merge, deployment, or provider-account provisioning.
