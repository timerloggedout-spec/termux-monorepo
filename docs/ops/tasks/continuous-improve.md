# REVIEW REQUIRED — first iteration produces PLAN.md

Do NOT execute edits on iteration 1. Write PLAN.md in the worktree
naming 5 concrete improvements, then finish.

---

# Task: continuous repo improvement

## Loop (repeat 8 hours)

Each iteration:

1. Pick the SMALLEST concrete improvement that is additive or surgical,
   has a test to verify it, and cannot regress existing behavior.

2. Target scopes in priority order:
   deepcli/deepcli/         Python modules
   deepcli/tools/hygiene/   shell + Python tooling
   deepcli/tests/           coverage additions
   archwiz/                 forensic tooling

3. One category per iteration:
   missing test, dead code removal, error message clarity,
   input validation, docstring, silent-exception, hardcoded-to-constant,
   duplicate-to-helper, slow-path-to-cache, function-split.

4. For each: gh_worktree create, edit in worktree, run
   python3 deepcli/tests/run.py (must be 20/0), commit_push_pr.

5. Refuse to modify:
   - deepagent.py, _v1_* files touched in last 24h
   - core.py (handled by modularize-core)
   - ~/.gnupg, ~/.deepcli/config.json
   - anything network-touching

6. finish when 8 hours elapse OR 5 consecutive PRs landed with no
   obvious next improvement.

## Hard limits

- max 1 file changed per PR
- max 40 loc delta per PR
- every PR must add or update at least one test
- if any test fails on worktree, remove worktree and pick another
