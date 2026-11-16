#1185 TRIAGE (side-chat lane, via custom.github-pat, 2026-10-20)
- Title: Sentinel: Fix symlink hijacking in termux DB. State: open, 1 commit, head b65dc80f, base cc3625ab.
- Files (now enumerable via PAT, previously approval-gated): termux-multi-agent/src/db.py (+29 -4), tests/test_termux_db_privileges.py (new, +41).
- Content: adds _ensure_secure_db_path() — rejects symlink DB path and symlink parent, chmods parent 0o700 / file 0o600; init_db calls it before and after table creation, replacing the bare trailing os.chmod.
- Master check: current master db.py (blob dcdca23f) has ONLY the bare os.chmod(DB_PATH, 0o600) at line 49, no symlink guard. NOT superseded.
- Verdict: REBASE-BY-CONTENT candidate, strongest of the three in this lane. Land FIRST in the lane sequence.
- Overlap: its db.py replacement removes the exact chmod block that #404 and #402 patch, so their db.py hunks are moot after this lands.
- Next: build resolved db.py against current master, run its 3 tests locally, stage STAGED.md, publish via PAT.
