# Vultr Inference Catalog Reference Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Register the two pinned Vultr catalog SDK references and produce a repository-grounded improvement specification for the existing provider Inference catalogue.

**Architecture:** Add a metadata-only reference slot, connect it to existing refTemplates navigation and ICM, and enforce its metadata contract through the existing inventory validator. Record the comparative analysis separately; keep runtime catalog and routing behavior unchanged.

**Tech Stack:** Markdown, JSON metadata, Python standard-library inventory script, pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-11-21-vultr-inference-catalog-reference-design.md`

## Global Constraints

- Base branch: `master`; work on an isolated feature branch.
- Proposal scope: `MSM-025` under the existing model-selection-market proposal.
- Reference slot: `refTemplates/19_Provider_Inference_Catalogs/`; slot 18 is reserved by open PR #5753.
- Source pins: Python `4a414ab26e1f596cb98b3974a7d12182bf62dab3`; TypeScript `6e55057cb718213937c4c118271f5a2ca1779d0d`.
- Metadata-only references; keep runtime, credentials, inference, quotas, schedules and routing unchanged.
- Preserve provider catalog, credential, entitlement, quota, health and inference evidence as independent states.
- Retain repo gate and Termux smoke as required promotion gates.

## Review Focus

- Source revision drift: keep the full immutable commit SHA in each source record.
- License drift: retain the license evidence and re-check before any future vendoring.
- Slot collision: preserve the open PR #5753 ownership of slot 18 and use slot 19.
- Validator compatibility: retain the existing `research_children` inventory field for current consumers.
- Catalog semantics: distinguish exact provider source facts from monorepo recommendations and policy.

---

### Task 1: Extend reference metadata validation

**Files:**
- Modify: `scripts/ci/refTemplates_inventory.py`
- Create: `tests/test_refTemplates_inventory.py`

**Interfaces:**
- Preserve the existing `inventory_entry(slot) -> dict` and `validate(entries) -> list[str]` interfaces.
- Preserve `research_children` output for slot 15.
- Add metadata-child validation for `15_Research_Repo_Templates`, `18_Vector_Databases` and `19_Provider_Inference_Catalogs`.

- [x] Write a failing test proving a slot-19 child missing `SOURCE.txt` is reported.
- [x] Run the focused test and confirm the expected assertion failure (RED observed in the isolated source-mirror harness).
- [x] Implement the shared metadata-child collection/validation while preserving the slot-15 output contract.
- [x] Add a passing fixture with both required files and regressions for slot-15 and slot-18 compatibility.
- [x] Run the focused tests (5 passed) and strict inventory mode (3 synthetic slots, 0 contract failures) in the isolated source-mirror harness.

### Task 2: Register pinned Vultr references

**Files:**
- Create: `refTemplates/19_Provider_Inference_Catalogs/README.md`
- Create: `refTemplates/19_Provider_Inference_Catalogs/vultr-model-catalog-python/README.md`
- Create: `refTemplates/19_Provider_Inference_Catalogs/vultr-model-catalog-python/SOURCE.txt`
- Create: `refTemplates/19_Provider_Inference_Catalogs/vultr-model-catalog-python/metadata.json`
- Create: `refTemplates/19_Provider_Inference_Catalogs/vultr-model-catalog-typescript/README.md`
- Create: `refTemplates/19_Provider_Inference_Catalogs/vultr-model-catalog-typescript/SOURCE.txt`
- Create: `refTemplates/19_Provider_Inference_Catalogs/vultr-model-catalog-typescript/metadata.json`

- [x] Record exact source URLs, commit SHAs, default branch and MIT license evidence.
- [x] Mark both references metadata-only and research-only.
- [x] Re-fetch all source metadata and reference files; final CI remains the authoritative repository validation.

### Task 3: Connect repository navigation and ICM

**Files:**
- Modify: `refTemplates/00_Index/README.md`
- Modify: `refTemplates/00_Index/SOURCE-MAP.md`
- Modify: `docs/icm/objects/knowledge/reference-inputs.md`
- Modify: `docs/ops/REFTEMPLATES-WORKFLOW-HOOKS.md`

- [x] Link slot 19 from the refTemplates index and source map.
- [x] Record the provider-catalog reference class in the ICM knowledge card.
- [x] Extend the metadata integrity checklist to cover slot 19 and the existing slot 18 contract.

### Task 4: Publish the comparative RECON

**Files:**
- Create: `docs/ops/VULTR-INFERENCE-CATALOG-REFERENCE-RECON.md`

- [x] Compare the Vultr wire schema, normalized model, media catalog, cache, parser tolerance and shared fixture strategy with the existing v5 collector/adapters.
- [x] Separate verified source facts, current monorepo facts and recommendations.
- [x] Prioritize v6 design opportunities without changing runtime behavior.

### Task 5: Record proposal scope and authorization

**Files:**
- Modify: `docs/proposals/active/model-selection-market/ITEMS.md`
- Modify: `docs/proposals/active/model-selection-market/DEBATE.md`

- [x] Add MSM-025 with metadata-only scope and dependencies.
- [x] Record the operator's task-scoped authorization; preserve the proposal-wide lifecycle state.

### Task 6: Verify and prepare review

- [x] Run the focused inventory tests in the isolated source-mirror harness: 5 passed.
- [x] Run `python3 scripts/ci/refTemplates_inventory.py --strict` in the isolated source-mirror harness: 3 slots validated, 0 failures.
- [ ] Run `python3 scripts/ci/repo_gate.py`.
- [ ] Run `python3 scripts/ci/termux_smoke.py`.
- [x] Re-fetch all 18 changed paths and compare the final branch against current `master`: ahead of current `master`, 0 commits behind; final head recorded separately.
- [ ] Open a PR citing `Implements: MSM-025`.
- [ ] Inspect repo-gate, Termux smoke, proposal validation and any review findings on the same immutable head SHA.
- [x] Preserve the isolated branch for review; promotion follows repository gates. PR creation awaits an explicit request.


### Environment and external-check observations

- The Termux MCP `get_device_info` action is unavailable in this session; Android device pressure and the Termux home checkout remain unobserved.
- GitHub connector writes used an isolated feature branch based on the current `master` tip. The local source-mirror harness passed five focused tests and strict inventory validation across three synthetic slots.
- Full repository `repo_gate.py` and `termux_smoke.py` remain pending a repository-native run. An intermediate commit returned a Vercel build-rate-limit status; the final head currently has no combined status checks, so that earlier preview-capacity observation is not a final-head result.
- The Termux stewardship skill reserves PR creation for an explicit PR request; this task prepared the branch and records the PR gate as pending.
