# Gate Admission Optimization — Execution Plan

**Spec:** `docs/superpowers/specs/2026-11-27-gate-admission-optimization.md`  
**Proposal:** `GAO-001` through `GAO-005`  
**Branch:** `feat/gate-admission-optimization-20261127`  
**Base:** `master` at `341ee481f3d829652e816789c0f9dbfc661897fd`

## Global constraints

- Keep `repo-gate` universal and stdlib-only.
- Run Termux smoke only when the canonical surface classifier admits it; manual dispatch runs it.
- Fail closed to smoke when base/head diff evidence is unavailable.
- Keep bucket-headroom PyYAML/pytest dependencies in a separate path-scoped workflow.
- Preserve dangle baseline, `.github/` + `apps/` finding scope, rename mode, and read-only behavior.
- Preserve Vercel project-scoped path selection and quota/cooldown machinery.
- Keep Devin optional; verify no-cost entitlement and referral-credit provenance independently.
- Keep every required result bound to one immutable candidate SHA.
- Record `SKIPPED` as applicability, not as test execution evidence.
- Use the remote feature branch as the isolated workspace; the available GitHub connector provides repository operations, while a local worktree/shell is unavailable in this session. Run verification through repository CI and report its exact evidence.

## Task 1 — Path classifier and downstream PR classification

**Files:** `scripts/ci/gate_admission.py`, `ml/pipelines/production_classify.py`, `ml/pipelines/lanes/classify.py`, corresponding tests.

1. Add failing tests for exact Termux paths, prefix paths, ordinary documentation/code paths, manual dispatch, missing diff evidence, and downstream PR classification.
2. Run the focused tests through PR CI and capture the expected RED result.
3. Implement the stdlib path registry, changed-path diff, fail-closed admission decision, and GitHub output writer.
4. Extend the PR collector to fetch changed file paths, fail closed when the file list is incomplete, and emit `termux_smoke_required`.
5. Update the lane classifier so Termux smoke is required only when the shared predicate matches.
6. Run focused tests and the complete repo-gate suite.

**Expected:** non-Termux PRs can reach `CANDIDATE` with repo-gate evidence alone; Termux PRs require smoke evidence; unavailable path evidence stays `NEED_EVIDENCE`.

## Task 2 — Termux workflow and bucket-headroom separation

**Files:** `.github/workflows/termux-smoke.yml`, new `.github/workflows/bucket-headroom-contract.yml`, `tests/test_bucket_headroom_workflow.py`, workflow contract tests.

1. Update tests to require a dedicated bucket-headroom contract workflow and a Termux workflow with conditional smoke steps.
2. Capture RED through the current Termux workflow test path.
3. Add the admission step to the always-visible Termux check; condition smoke tests, core smoke, and runtime probes on its output.
4. Add the explicit skip reason step.
5. Move PyYAML/pytest installation and bucket-headroom tests into the path-scoped contract workflow.
6. Verify workflow YAML, test wiring, and path scope.

**Expected:** the Termux workflow check remains present; smoke execution is conditional; bucket-headroom tests run only from their own source/workflow paths.

## Task 3 — Dangle target-path coverage

**Files:** `.github/workflows/archwiz-dangle.yml`, `tests/test_gate_admission_policy.py`.

1. Add failing assertions for source and target roots.
2. Extend pull-request path triggers to the relevant reference target roots.
3. Preserve census scopes, baseline, rename mode, and artifact.
4. Run dangle fixture tests and workflow policy tests.

**Expected:** changes that remove/move scripts, docs, ops data, config, app assets, or context references trigger the existing read-only scan.

## Task 4 — Policy and provider alignment

**Files:** `CLAUDE.md`, `CLAUDE.hum.md`, `.agents/skills/superpowers/SKILL.md`, `docs/ARCHW1Z-GATE.md`, `docs/TERMUX-SMOKE.md`, `docs/proposals/PROCESS.md`, proposal template, cadence/roster/classifier docs, gate matrix.

1. Make repo-gate universal and Termux smoke surface-conditional in machine and human instruction sources.
2. Document explicit skip semantics and exact-SHA requirements.
3. Record Vercel as existing project-conditional quota-aware deployment machinery with provider effect awaiting receipts.
4. Record Devin as optional pending fresh entitlement and referral evidence.
5. Align proposal gate coupling and PR lane documentation.

**Expected:** one consistent admission policy across CI, local instructions, proposal lifecycle, and reporting.

## Task 5 — Verification and review

1. Run focused unit tests for admission, PR classification, bucket-headroom contracts, and dangle behavior.
2. Run `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/validate_siglary_mandate.py --base origin/master` on the final head.
3. Run `python3 scripts/ci/termux_smoke.py` on a Termux-surface candidate or manual dispatch; record the conditional skip reason for a non-Termux candidate.
4. Inspect all PR workflow jobs and artifacts on the immutable head SHA.
5. Request one fresh whole-branch review; resolve Critical/Important findings with RED→GREEN tests.
6. Leave the PR open for the operator's merge decision.

## Review focus

- Fork PRs, initial pushes, deleted/renamed paths, missing base/head SHAs, and incomplete GitHub changed-file pagination.
- Workflow check continuity when Termux smoke is skipped.
- Agreement between helper path registry, workflow admission, and PR classifier.
- Bucket-headroom test ownership and package isolation.
- Dangle target-path coverage and unchanged baseline semantics.
- Vercel provider-effect claims and Devin entitlement/referral evidence.
