# Source and Evidence — gate-admission-optimization

## Operator direction

On 2026-11-27 the Operator directed: “Yes; gate admission Optimizations; 3xact1y. @Superpowers Do Everything Continue.” The stated policy inputs are:

- Vercel admission remains contextual and quota-sensitive.
- Devin free-tier availability and referral marketing replenishment are operator-reported capacity leads.
- Termux smoke applies to slices intended to execute from the Termux surface.

## Repository evidence at inspected master head

- `.github/workflows/termux-smoke.yml`: pull-request and configured push triggers currently admit every change; its job installs PyYAML/pytest and runs bucket-headroom tests alongside smoke.
- `scripts/ci/termux_smoke.py`: checks Python version, required repository layout, repo-gate and smoke-script compilation, SIM-memory validation, git/bash/TMPDIR, connector smoke, and optional deepcli/archwiz probes.
- `.github/workflows/archwiz-dangle.yml`: current pull-request paths cover the dangle implementation/baseline/test, `.github/workflows/**`, and `apps/**`; the census runs with `--scope .github/ --scope apps/`.
- `scripts/ci/dangle_check.py`: existing baseline ratchet and read-only rename mode are the implementation boundary for reference checking.
- `scripts/ci/vercel_ignore_build.sh` and the three project `vercel.json` files: project-specific source roots and ignore commands are already configured.
- `tests/test_vercel_ignore_commands.py`: regression coverage already checks unrelated-change skips, relevant-change builds, missing SHA fail-open behavior, and project scoping.
- `.github/workflows/vercel-batch-deploy.yml` and `scripts/ci/dispatch_admission.js`: quota-aware batch dispatch, observed-count reconciliation, reserve, and cooldown logic already exist.
- `docs/ops/GATES-REGISTER.md`: current Devin API status is recorded as paid-organization-only/card-blocked for the Free organization.
- `config/referral_programs.json` and `docs/ops/REFERRAL-AUTOMATION.md`: the listed referral programmes do not establish Devin credit eligibility.

## Evidence classification

- **Verified repository facts:** paths and behavior above, read from the inspected repository head.
- **Operator-reported lead:** Devin free-tier availability and referral marketing replenishment, received 2026-11-27.
- **Pending provider evidence:** current Devin account/plan, API quota balance/reset, billing requirements, and referral credit terms.
- **Pending Vercel effect evidence:** provider-side deployment skip/build receipts for an unrelated and a relevant commit.
- **Graph evidence gap:** the context-relationship manifest was not reachable at the expected `workspace/llm_map/context_relationships/manifest.json` path during this pass. Direct file and workflow relationships are used; graph-derived edges remain unverified.
