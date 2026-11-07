# Development run — repo-gate YAML ratchet diagnostics

- **Run date:** 2026-11-07 UTC
- **Repository:** `timerloggedout-spec/termux-monorepo`
- **Priority:** P0 — issue [#5053](https://github.com/timerloggedout-spec/termux-monorepo/issues/5053)
- **Branch:** `fix/repo-gate-yaml-ratchet-diagnostics-2026-11-07`
- **Base:** `master` at `314b8f8e81fedf7967ad1a6a37fc44efef6b9dcb`
- **Implementation head before this record:** `93578d4a14a2bad044d1d06d6183da36d5abeb60`
- **Status:** diagnostic improvement committed; CI validation pending; underlying YAML fault not yet repaired

## Evidence and diagnosis

The captured `repo gate` job (run [42393889866](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/42393889866), feature head `e3be7da679fa708faa405c4247057ef25b97ac48`) reported:

- `invalid_control_plane_yaml=1`
- baseline allowance: `0`
- ratchet failure: `invalid_control_plane_yaml rose 0 -> 1`

The same log printed `yaml-structure=1` in the hard-check summary. That value is the number of changed YAML files scanned, not a failure count. No changed-file `yaml-structure` failure was emitted for the modified `docs/schemas/agent-roster.yaml`.

A separate PR #5056 comment also recorded a repo-wide ratchet increase after the changed-file YAML structural check passed. The current gate reports only the count, so the exact offending path is not visible in its failure output. Raising the baseline would conceal the debt and is explicitly rejected.

## Work implemented

Updated `scripts/ci/repo_gate.py` so that when the `invalid_control_plane_yaml` ratchet exceeds its baseline, the gate emits the offending repository path and line numbers. It deliberately does not echo YAML line contents, avoiding disclosure of potentially sensitive configuration values.

Added `test_ratchet_reports_offending_control_plane_yaml_path` to `tests/test_repo_gate_workflow_yaml.py`. The fixture creates a malformed workflow in a temporary Git repository, sets the counter baseline to zero, runs `--ratchet-only`, and asserts that the path and line numbers are reported.

## Validation

- No local tests were run; the isolated Sprite executor remains unavailable pending organization billing setup, and the local container cannot resolve GitHub.
- The new regression test is committed and awaits GitHub Actions execution on this branch.
- The diagnostic is not a fix for the offending YAML. The next run must use the emitted path/line evidence to correct the source, then verify the repo-wide counter returns to zero without changing the baseline.

## Next actions

1. Inspect the current-head `repo gate` output for the exact YAML path and line number.
2. Verify the file with the repository's available YAML parser/oracle and identify whether the fault is real or a structural-check false positive.
3. Correct the source or the structural heuristic, with a regression fixture.
4. Require the current-head repo gate and Termux smoke to pass; do not change the baseline to mask the issue.
5. Close issue #5053 only after a subsequent master run passes or the fix PR is linked and the failure is accurately classified with evidence.

## Second pass — source identified and repaired

The diagnostic build on PR #5059 identified the exact offender:

- Path: `.github/workflows/certification-validation.yml`
- Location: line 82
- Fault: flush-left heredoc body and terminator escaped the YAML `run: |` block, so the structural scanner interpreted the heredoc payload as YAML structure.

Corrected the workflow by indenting the heredoc body and `EOF` terminator to the YAML block-scalar indentation. YAML removes the common indentation when constructing the shell script, so the shell still receives a correctly positioned heredoc terminator.

- Repair commit: `fe596ea7f28a5cb91b1ffa0ce9ec355f75778e55`
- The repository baseline remains unchanged at zero.
- Current-head CI is pending; no local test result is claimed.
