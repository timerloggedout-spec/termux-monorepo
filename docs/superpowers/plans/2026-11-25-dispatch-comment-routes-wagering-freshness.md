# Dispatch comment routes and wagering-feed freshness

## Scope and evidence

Base: current `master` at `eb93ae0080107334bd923a3ece1857297936e774`. Work is isolated on `fix/dispatch-comment-routes-wagering-freshness-20261125`.

Registered work items: `QSR-4` (auto-claim comment-route resolution) and `LC-009` (wagering feed freshness/regeneration).

Verified causes: `scripts/dispatch/auto_claim.py` reads SWARM JSON route stamps from only the issue body, then sends every non-build route to the seat queue. Issue #5868's admission comment instead contains the plain stamp `route: project-task-dispatch.yml`. The public wagering feed and its dashboard mirror both carry `generated_at=2026-11-04T09:55:36Z`; the existing surface contract calls a feed stale after 48 hours. The generator derives values from the canonical book feed, challenges book, and append-only ledger. AMD-20 settlement remains null in the source and must stay null.

The focused baseline currently has 17 passing and 5 failing tests in `scripts/dispatch/test_auto_claim.py` plus `tests/test_wagering_book_page.py`. The page-test failures are pre-existing stale expectations (fetch options, family list, ledger count, fixture intake selection, and wall-less source windows); preserve that distinction while implementing the requested fixes.

## Design

1. Preserve explicit `claim-class:` and `executor of record:` precedence. Resolve route stamps from both the issue body and comments, normalize only the documented route names and their `.yml` forms, and fail closed when a route is unknown or conflicting. Do not add new claim classes or alter gating/claim timing.
2. Add a stdlib validator for the existing 48-hour freshness contract and byte identity across the generated feed, dashboard mirror, and test fixture. Reject malformed, timezone-naive, future-dated, or stale timestamps. Keep the freshness test deterministic with an injected `now` value.
3. Make the Tribute deploy workflow regenerate all three copies from canonical inputs and run the validator before each dashboard publication route. Trigger the workflow when book inputs, the generator, or validator change.
4. Regenerate checked-in outputs from the current canonical sources only. Do not change source records, infer settlements, or fill AMD-20's null settlement.

## Test-first implementation steps

1. Add regression tests for route stamps in comments, the plain `.yml` route form, unknown/conflicting-route fail-closed behavior, stale/fresh validator behavior, mirror parity, and deployment workflow wiring. Run and observe the new tests fail for the expected reasons.
2. Implement the smallest parser and validator changes; wire regeneration/validation into the `user-site` and `vercel` jobs and add canonical input triggers.
3. Regenerate `ops/moneyball/wagering-book.json` and `apps/tribute-dashboard/data/wagering-book.json`; verify byte identity and unchanged AMD-20 null settlement.
4. Update only directly affected stale assertions in the existing wagering-page tests if they prevent testing the current source-of-record contract; do not change source data to satisfy old expectations.

## Verification

Run focused dispatch and wagering tests, `git diff --check`, `python3 scripts/proposals/validate_registry.py`, `python3 scripts/ci/repo_gate.py`, and `python3 scripts/ci/termux_smoke.py`. Inspect the complete diff and regenerated settlement values. Do not push, open a PR, merge, or deploy; the requested outcome is a validated reviewable branch before any merge.
