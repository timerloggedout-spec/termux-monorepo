# Help-Given Tribute

Implemented Help-Wanted graduation contract.

STAKE != CLAIM != IMPLEMENTATION != SOLUTION != VALIDATED != ACCEPTED.

The lane must revalidate issue eligibility before claiming and again before opening an upstream PR. Closed issues, competing claims/assignments, human-only requirements, and unreadable eligibility evidence must fail closed. A claim comment is not evidence of implementation, and stake-only PRs are retired.

See `scripts/ci/help_wanted_diff_gate.py` for the fail-closed diff-proof gate and `scripts/ci/test_help_wanted_diff_gate.py` for regression coverage. The gate verifies structural patch/evidence quality only; issue-specific acceptance, review resolution, maintainer acceptance, and independently verified downstream impact remain separate lifecycle states.


## Sweep accountability

This lane is governed by `docs/ops/SWEEP-ACCOUNTABILITY.md`. Every historical/future observation or action is recorded as an append-only sweep receipt with version/iteration lineage, findings, actions, effects, provenance, source SHAs, and continuation cursor. Lane receipts remain source evidence; sweep receipts do not replace them.
