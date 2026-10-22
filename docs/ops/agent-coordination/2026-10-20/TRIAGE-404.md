#404 TRIAGE (side-chat lane, via custom.github-pat, 2026-10-20)
- Title: sec(sentinel): skip chmod when cache/db/log path is a symlink. State: open, 1 commit, head 30740f60, base 8e9839f9.
- Files: multi-ai-cli/ci_mode.py (+4 -2), termux-multi-agent/src/db.py (+2 -1), termux-multi-agent/src/telemetry.py (+3 -2). Total +9 -5, no tests.
- Content: guard each os.chmod with an islink check (skip chmod on symlinks).
- Verdict: PARTIALLY MOOT after #1185. The db.py hunk patches the chmod block #1185 replaces with stronger rejection logic. Remaining real value: ci_mode.py (2 guards) and telemetry.py (1 guard).
- Next: after #1185 lands, rebase-by-content with ONLY ci_mode.py + telemetry.py hunks; verify against current master versions of those files first.
