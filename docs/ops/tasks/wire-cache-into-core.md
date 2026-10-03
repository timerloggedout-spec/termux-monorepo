# Task: wire _v1_cache into core._cache_save

Bound first dispatch. Small, verifiable, produces a PR.

## Context

- `deepcli/deepcli/_v1_cache.py` exists and exports `atomic_json_dump`,
  `read_session`, `last_msg_ts`, `is_fresh`.
- `deepcli/deepcli/core.py::_cache_save` currently does:
      with open(path, "w") as f:
          json.dump(messages, f, indent=2)
  Non-atomic — readers can see a truncated file mid-write.
- `deepcli/deepcli/core.py` is on the agent's PROTECTED_PATHS list.
  You cannot `write_file` to it. Use `gh_worktree` + PR.

## Steps

1. `read_file` on `~/deepcli/deepcli/_v1_cache.py` — confirm the
   exported names.

2. `read_file` on `~/deepcli/deepcli/core.py` — locate `_cache_save`
   (around line 85) and read 20 lines of context above and below.

3. `gh_worktree` action=create branch=`fix/core-atomic-cache-save`
   base=`feat/dashboard-lanes-v2`.

4. In the worktree, edit `deepcli/deepcli/core.py`:
   - At the top with the other imports, add:
         from ._v1_cache import atomic_json_dump
   - Inside `_cache_save`, replace the `with open(path, "w")` block with:
         atomic_json_dump(path, messages, indent=2)

   Use `run` with `python3 -c` or `sed -i` — do NOT use `write_file`
   on core.py (it's protected).

5. `run` a syntax check on the edited file:
       python3 -m py_compile ~/.deepcli/worktrees/fix-core-atomic-cache-save/deepcli/deepcli/core.py

6. `run` the test suite from within the worktree:
       cd ~/.deepcli/worktrees/fix-core-atomic-cache-save && python3 deepcli/tests/run.py

   All 20 tests should pass.

7. `gh_worktree` action=commit_push_pr branch=`fix/core-atomic-cache-save`
   message=`fix(core): atomic write in _cache_save via _v1_cache`
   title=`fix(core): atomic write in _cache_save`
   body=`Replaces truncate-then-write with atomic_json_dump (mkstemp →
   fsync → os.replace). Readers tolerate partial writes as of the
   recent _v1_cache module; this eliminates the race at the source.`

8. `finish` with a summary that names:
   - the PR URL from the previous step
   - branch name
   - test result (20 passed / 0 failed)
