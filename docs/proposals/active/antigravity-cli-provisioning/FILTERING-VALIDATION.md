# Filtering validation — AGY-1497-09

## What is implemented

The no-model prototype is integrated as `scripts/antigravity/telemetry.py` plus a passive `capture.py` entry point. Full input bytes and optional stderr remain in private files; normalized metadata and the three-line steering view are separate. Adversarial events, malformed/manual quota, oversized lines and private output permissions have offline coverage. Controller-side `settings.py` prepares a strictly JSON-validated, byte-preserving High candidate; the narrowly guarded `secondary_settings.sh` helper applies only that exact hash-pinned candidate. These are tested against mocked identity and settings, not against a live phone.

## Executed offline checks

| Check | Result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_agy*.py'` | PASS: 58 tests; includes original native contracts and no-replay pilot tests |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_antigravity_readiness.py -v` | PASS: 7 tests |
| `bash -n scripts/antigravity/secondary_settings.sh` | PASS |
| `git diff --check` | PASS |
| `PYTHONDONTWRITEBYTECODE=1 python3 scripts/ci/repo_gate.py --base origin/master-staging` | PASS: 27 changed paths in complete PR; index-based checks and debt ratchets passed |
| `PYTHONDONTWRITEBYTECODE=1 python3 scripts/ci/termux_smoke.py` | PASS on Linux; not a native Android run |
| Independent code review | PASS after replacing text-based settings manipulation with strict JSON preparation and hash-pinned apply |

All inputs were synthetic local fixtures. No `agy` model prompts, pilot replays, quota refreshes or model switching occurred. Shellcheck is not installed; shell syntax and execution were checked with Bash. A transient full root filesystem interrupted initial new-file writes; both affected new files were completely rewritten and their tests passed after capacity recovered. No unrelated work was deleted or reset.

The unqualified default repository gate was also run. It selected `origin/master`, not this PR's `master-staging` base, and failed on six inherited findings: syntax in two `harmonizer-prod_cli/workspace/provision_agent*.py` files, and existing `.bak` files in `appliedSxi/maxc/src_prototype_bidir`, `deepcli`, and `termux-multi-agent/src`. Those unrelated files were not changed. The explicit PR-base gate above passed; no claim that the default-base debt was repaired is made.

Review rejected the initial grep/sed-only settings approach; it is not the shipped implementation. The final controller parser requires the actual top-level property, rejects duplicate keys and invalid/non-finite values, and preserves unrelated bytes, including nested settings. The phone apply step trusts only the validated before/after receipts. External pinned-host verification and avoiding concurrent interactive edits remain operational requirements, not promises of a shell sandbox.

## Device 2 is blocked, not deployed

The existing pinned SSH route failed before remote execution. The tailnet reports the secondary offline, last seen at `2026-10-22T08:20:00Z`; no alternate device was contacted. Fresh device identity, settings inspection, the High correction, source transfer and actual-device filter use have **not** succeeded. The owner's requested saved High value remains pending; existing auto-approve was not modified by this follow-up. Origin and its backup were untouched.

Bring only the secondary `tmx-node-55619bd5` online with its existing Tailscale/Termux SSH. Then verify the existing pinned host key and local canonical marker/account/model before writes; preserve the current worktree and pilot result. Privately capture settings on the controller, prepare the High candidate with `settings.py`, and transfer only that private candidate and scoped source files into the dedicated issue workspace. Use the exact validated receipts with the settings helper; abort on any mismatch. Re-read and JSON-validate installed High settings and compare the complete candidate hash to prove byte-for-byte preservation of unrelated settings. Keep candidates and rollback snapshots private. Do not replay the pilot.

The phone previously lacked Python on PATH. Run the passive Python filter in the controller against an **existing** secondary stream-json capture if no native runtime exists; preserve its complete stdout/stderr capture and write the concise steering artifact separately. Do not fabricate stream-json from a JSON-format pilot or label a synthetic fixture real telemetry. Installing Python, making a new model request, or claiming a native phone run is outside this continuation.

## GitHub boundary

Issue #1497 is the tracking record using the documented GitHub fallback. Live PR #1514 is on `cue/1497-operational-device2`, targeting `master-staging`; the handoff's older provisioning branch is not its live head. Scope registration: https://github.com/timerloggedout-spec/termux-monorepo/issues/1497#issuecomment-6336367544 . Leave the issue open and PR unmerged until the owner decides otherwise. Offline integration is not full provisioning completion.
