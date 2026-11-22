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
- [x] GitHub repo gate passed on PR head `9787c614ccb84b02d61134564d22fb52cdef4f0a`.
- [x] GitHub Termux smoke passed on PR head `9787c614ccb84b02d61134564d22fb52cdef4f0a`.
- [x] Re-fetch all 19 changed paths and record the branch comparison with immutable refs. The clean reconstruction starts from current master `bb3d58265f8c4908de8967fc00c79ed72f647b56`. The initial implementation was consolidated into one imperative commit, followed by two small imperative commits for DoE registry regression coverage and plan evidence. The branch remains 3 commits ahead and 0 behind at the latest recorded comparison; re-fetch current master before promotion.
- [x] Open draft PR #5754 citing `Implements: MSM-025` after the explicit PR request.
- [x] Inspect repo-gate, Termux smoke, proposal lifecycle, PR evidence and review findings on the recorded head SHA.
- [x] Preserve the isolated branch for review; promotion follows repository gates and independent review.


### Environment and external-check observations

- The Termux MCP `get_device_info` action is unavailable in this session; Android device pressure and the Termux home checkout remain unobserved.
- GitHub connector writes used an isolated feature branch based on the current `master` tip. The local source-mirror harness passed five focused tests and strict inventory validation across three synthetic slots.
- GitHub repo gate and Termux smoke both passed on PR head `9787c614ccb84b02d61134564d22fb52cdef4f0a`; proposal lifecycle, PR evidence evaluation and refTemplates continuous evaluation also passed on that review cycle.
- Historical review of superseded PR #5754 identified four inline findings and one source-preview edge case. The replacement branch incorporates those remediations; the four prior review threads were resolved before PR #5754 was closed.
- The original branch's DO Statement Style failure came from historical commit subjects. This replacement branch is a single imperative commit from current master; fresh style-gate evidence on the replacement head is pending.
- Advisory CodeQL jobs for Python, JavaScript/TypeScript and Actions reached analysis but failed while publishing because the GitHub App installation API rate limit was exceeded; the workflow marked each job as a configuration error. The workflow declares this CodeQL run advisory and outside the required merge-check set.
- Vercel preview status is non-gating under repository policy. Termux MCP `get_device_info` remains unavailable, so Android device health remains unobserved.
