#402 TRIAGE (side-chat lane, via custom.github-pat, 2026-10-20)
- Title: Sentinel: Fix symlink hijacking vulnerability on os.chmod permission operations. State: open, 5 commits, head e02cdc10, base 8e9839f9 (same base as #404).
- Files: 49 total, but 44 are stale-base noise — deletions of ops/github-telemetry/raw JSON and churn in docs/ops/generated files. Those deletions must NOT land.
- Real content (5 files): multi-ai-cli/ci_mode.py (+4 -2, same as #404), termux-multi-agent/src/db.py (+2 -1, same as #404), termux-multi-agent/src/telemetry.py (+2 -1, same guard as #404), tests/test_sentinel_privileges.py (+12 -4, the only unique content), plus docs/ops/DOCS-BRANCH-INDEX.md churn.
- Verdict: DUPLICATE of #404 (+#1185 for db.py). Do NOT rebase wholesale. Close as superseded once #1185 and the reduced #404 land, after checking whether its test_sentinel_privileges additions are already covered on master — salvage them into the #404 rebase if not.
