# PLAN.md — continuous repo improvement, iteration 1 (REVIEW ONLY)

Branch: `plan/continuous-improve-iter1` (base `master`)
Author: DeepAgent, iteration 1. No edits executed this iteration, per
`deepcli/tasks/continuous-improve.md`.

## Constraints inherited from the task

- max 1 file changed per PR
- max 40 LOC delta per PR
- every PR must add or update at least one test
- test gate: `python3 deepcli/tests/run.py` must be green (currently 20 tests/0 failures)
- do NOT touch: `deepagent.py`, `_v1_*` files touched in last 24h,
  `deepcli/deepcli/core.py`, `~/.gnupg`, `~/.deepcli/config.json`, network code
- one category per iteration

## Current baseline (read during iteration 1)

- `deepcli/tests/run.py` — unittest loader, discovers `test_*.py`, 20 tests.
- `deepcli/tests/test_cache.py` — 5 tests over `_v1_cache`.
- `deepcli/tests/test_events.py` — 4 tests over `_v1_events.extract`.
- `deepcli/deepcli/_v1_cache.py` — `atomic_json_dump`, `read_session`,
  `last_msg_ts`, `is_fresh`; module constants `MIN_BYTES=40`,
  `RETRY_SLEEP=0.15`, `TS_KEYS`.
- `deepcli/deepcli/_v1_events.py` — `extract`, `message_text`,
  `scan_session`, `scan_dir`; `RULES` table.
- `deepcli/deepcli/__init__.py` — re-export shim from `.core`.

## Five concrete improvements

Each entry is self-contained: target file, category, exact change,
verification test, invariant preserved, and why it cannot regress.

---

### 1. Missing test — `is_fresh()` has no coverage

- File: `deepcli/tests/test_cache.py`
- Category: missing test
- Change: add `test_is_fresh_recent` and `test_is_fresh_stale`.
  Build a session with `inserted_at = time.time()` (assert True) and one
  with `inserted_at = time.time() - 10_000` (assert False). Also assert
  `is_fresh(missing_path) is False`.
- Verifies: `deepcli/deepcli/_v1_cache.py::is_fresh`
- Invariant: no source change; test-only PR. `is_fresh` is already in
  `__all__` but untested.
- LOC delta: ~12, 0 source. Cannot regress: adds assertions only.

---

### 2. Missing test + input validation — `read_session` dict envelope

- File: `deepcli/tests/test_cache.py`
- Category: missing test
- Change: add `test_read_dict_envelope` covering the `_v1_cache.py`
  branch at lines ~99–104 that accepts a dict wrapper and probes
  `messages` / `conversation` / `data` / `history`. Parametrize over all
  four keys plus a dict with none of them (expect `[]`).
- Verifies: `read_session` dict-unwrap path, currently untested.
- Invariant: source unchanged; documents the documented-but-unproven
  contract in the `_v1_cache.py` docstring.
- LOC delta: ~14, 0 source.

---

### 3. Input validation — `last_msg_ts` rejects bool timestamps

- File: `deepcli/deepcli/_v1_cache.py`
- Category: input validation
- Change: in `_coerce_ts`, `isinstance(v, bool)` is a subclass of `int`,
  so `inserted_at=True` currently coerces to `1.0` (epoch 1970) and is
  returned as a real timestamp. Add an explicit bool guard returning
  `None` before the numeric branch.
- Test: `deepcli/tests/test_cache.py::test_ts_bool_ignored` — write
  `[{"inserted_at": True}]`, assert `last_msg_ts(p) is None`.
- Invariant: real numeric and ISO timestamps unchanged; only the
  degenerate bool case changes, and it was never a valid timestamp.
- LOC delta: ~2 source + ~4 test.

---

### 4. Silent-exception clarity — `scan_session` swallows all errors

- File: `deepcli/deepcli/_v1_events.py`
- Category: silent-exception
- Change: `scan_session` does `except Exception: return []` with no
  signal. Narrow to `except (OSError, ValueError, json.JSONDecodeError)`
  and keep returning `[]`, but attach the reason to a module-level
  `LAST_SCAN_ERROR` for observability (no logging dependency, no print).
- Test: `deepcli/tests/test_events.py::test_scan_missing_file_sets_error`
  — call `scan_session('/nonexistent/x.json')`, assert `[]` returned
  and `LAST_SCAN_ERROR` is a non-empty string.
- Invariant: return value identical on every previously-handled path;
  only genuinely unexpected exceptions now propagate (which is the
  desired behavior and is not exercised by current callers).
- LOC delta: ~6 source + ~6 test.

---

### 5. Hardcoded-to-constant — magic numbers in `read_session` retry loop

- File: `deepcli/deepcli/_v1_cache.py`
- Category: hardcoded-to-constant
- Change: the retry loop uses the literal `(0, 1)` and `attempt == 0` to
  express "two attempts, sleep between them". Introduce `MAX_ATTEMPTS = 2`
  next to `MIN_BYTES`/`RETRY_SLEEP` and drive the loop from `range(MAX_ATTEMPTS)`,
  replacing the `attempt == 0` checks with `attempt < MAX_ATTEMPTS - 1`.
- Test: `deepcli/tests/test_cache.py::test_read_session_attempts_constant`
  asserts `_v1_cache.MAX_ATTEMPTS == 2` and that a truncated file still
  yields `[]` (behavioral guard on the refactor).
- Invariant: exactly 2 attempts before, exactly 2 after. Same sleep
  placement. Pure mechanical extraction; existing
  `test_small` / `test_missing` already cover the two-attempt path.
- LOC delta: ~6 source + ~4 test.

---

## Iteration ordering (next 5 PRs)

1. (test-only) `is_fresh` coverage
2. (test-only) `read_session` dict envelope
3. (validation) bool-timestamp guard
4. (silent-exception) `scan_session` error surfacing
5. (constant) `MAX_ATTEMPTS` extraction

Each ships on its own branch `<category>/<slug>`, one file + its test,
test gate green, then `commit_push_pr`. If any worktree fails the test
run, remove the worktree and take the next item.

## Explicitly out of scope this series

- `core.py` modularization — owned by `deepcli/tasks/modularize-core.md`
- any `_v1_*` file modified within 24h of this plan
- network-touching code paths and credential stores
