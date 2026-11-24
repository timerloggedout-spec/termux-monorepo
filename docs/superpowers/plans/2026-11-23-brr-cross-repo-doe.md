# BRR Cross-Repository DoE Implementation Plan

> **For agentic workers:** Execute task-by-task in this branch. Steps use checkbox syntax.

**Goal:** Establish `brr-cross-repo-doe`, a separate reproducible DoE campaign that measures how well existing BRR, commit, regression, and context-graph evidence discovers relevant cross-repository branches and commits.

**Architecture:** Reuse the existing BRR v2 exports, #5552 regression feature map, #5640 joined evidence, and canonical context-relationship graph. Add a campaign-specific offline evaluator and immutable EXPERIMENT records; keep collection, scheduling, queue, graph ownership, and promotion authority in their existing systems.

**Tech Stack:** Python 3.10+ standard library; JSON; existing `docs/ops/corpus/EXPERIMENT.schema.json`; GitHub Actions for validation.

**Spec:** `docs/proposals/active/brr-cross-repo-doe/MANIFEST.md`

## Global Constraints

- BRR remains read-only and keeps `branch-reconciliation-registry/v1`.
- Reuse existing collectors, graph stores, regression suite, queue, scheduler, and DoE schema.
- One executed task/treatment run emits one EXPERIMENT record.
- Preserve source repository, source SHA, source timestamp, coverage, and evidence URLs.
- Candidate relationships remain distinct from verified relationships.
- Missing/private source data is UNKNOWN or BLOCKED, never empty/zero/complete.
- No new scheduler, queue, collector, dashboard, or merge authority.
- Commit and push each file write to this branch.

## Review Focus

- Partial or stale cross-repository BRR exports remain explicitly partial.
- Missing local Git refs and inaccessible private-store exports remain unresolved.
- Cross-repository same-name branches remain distinct by repository identity.
- Candidate graph edges never count as verified retrieval hits.
- Regression states `untestable` and `no-benchmark` never count as green.

---

### Task 1: Register the lane and its work item

**Files:**
- Create: `docs/proposals/active/brr-cross-repo-doe/MANIFEST.md`
- Create: `docs/proposals/active/brr-cross-repo-doe/ITEMS.md`
- Modify: `docs/proposals/registry.yaml`
- Modify: `docs/proposals/README.md`

- [ ] Register proposal `brr-cross-repo-doe` and item `BRRDOE-001`.
- [ ] Record operator authorization, reuse boundaries, and blocked private-source runtime dependency.
- [ ] Commit each write to the feature branch.

### Task 2: Preregister the DoE campaign

**Files:**
- Create: `experiments/doe/brr-cross-repo-doe/DESIGN.json`
- Create: `experiments/doe/brr-cross-repo-doe/README.md`
- Create: `experiments/doe/brr-cross-repo-doe/dataset.schema.json`
- Modify: `docs/ops/DOE-FAMILY.md`

- [ ] Define four retrieval arms: lexical baseline, BRR ancestry, context graph, fused evidence.
- [ ] Define blocked tasks, primary and secondary outcomes, decision rule, source identity, automation dependency, and honest design-only state.
- [ ] Register the campaign as design-only until the VM export and automation receipts are available.
- [ ] Commit each write to the feature branch.

### Task 3: Implement the offline evaluator

**Files:**
- Create: `scripts/doe/brr_cross_repo_doe.py`
- Create: `tests/test_brr_cross_repo_doe.py`
- Modify: `.github/workflows/repo-gate.yml`

**Interface:**
- `evaluate_dataset(dataset: dict) -> dict`
- `validate_dataset(dataset: dict) -> None`
- `build_experiment_records(result: dict, baseline_sha: str, candidate_sha: str, observed_at: str) -> list[dict]`

- [ ] Write tests for deterministic ranking, repository-qualified identity, verified/candidate separation, partial coverage, and untestable regression states.
- [ ] Implement deterministic offline evaluation using only supplied frozen evidence.
- [ ] Emit records conforming to the canonical experiment schema.
- [ ] Run focused tests and the owning validation suite in GitHub Actions.

### Task 4: Integrate and verify

**Files:**
- Modify: `docs/proposals/active/brr-cross-repo-doe/ITEMS.md`

- [ ] Validate JSON, schema conformance, Python syntax, proposal registry, and repository gates.
- [ ] Open a PR with `Implements: BRRDOE-001`.
- [ ] Re-fetch checks against the exact PR head SHA; preserve blocked runtime inputs as explicit gaps.
- [ ] Update the item ledger with commit, PR, and check evidence.
