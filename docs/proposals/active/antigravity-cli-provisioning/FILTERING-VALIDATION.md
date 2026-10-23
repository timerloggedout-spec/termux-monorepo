# Filtering validation — AGY-1497-09

## Controller telemetry/archive follow-up

This follow-up adds schema-v1 event rows flushed as source lines arrive, keeps step usage separate from authoritative terminal usage, and adds an age archive/JIT comparison utility plus a disabled-by-default reviewed Hindsight outbox. It is controller repository code only. No Device 2/Origin connection, AGY invocation, model request, Hindsight network request, real archive, or key was used.

| Check | Result |
|---|---|
| Focused AGY fixtures (`python3 -m unittest discover -s tests -p 'test_agy*.py'`) | PASS: 142 tests, including immediate emission, allowlist, malformed/oversized/repeated events, snapshot/final semantics, schema migration, fake-age round trip/no plaintext file, outbox append/idempotency/ambiguous ack/restart recovery, external-only output paths, and no-network-by-default |
| Readiness tests (`test_antigravity_readiness.py`) | PASS: 7 tests |
| Changed Python compilation | PASS: all five production modules and three focused fixture files |
| `python3 scripts/proposals/validate_registry.py` | PASS: 15 proposals |
| `python3 scripts/ci/termux_smoke.py` | PASS on controller Linux/Python 3.12.3 (`termux=False`); not native Android validation |
| `python3 scripts/ci/repo_gate.py --base origin/master-staging` | PASS: 45 complete-PR paths; `py=19`, `sh=3`, `json=3`, no symlinks; refreshed base `1a5af217f3ef9815ce31068d547ad28b69dd8ac7` |
| Complete `python3 -m unittest discover -s tests` | BLOCKED by unrelated missing imports: `curl_cffi` for `test_multi_ai_ci` and `dashboard` for `test_telemetry_optimized`; 197 tests ran with those two module-import errors. No packages were installed. |
| Real age binary/runtime encryption | BLOCKED: `age` is not installed in this controller; only a synthetic fake-age fixture ran. |

The archive helper requires an externally supplied recipient and private identity for real use. The Hindsight adapter requires separate owner consent, endpoint/bank/model and retention/privacy review; all tests use stubs, and no live send is available by default. See [TELEMETRY-PIPELINE.md](TELEMETRY-PIPELINE.md) for the detailed status map and sources. This branch has not deployed continuous telemetry on Device 2.

## Current bounded delegated execution receipt

The owner's subsequent authorization permitted exactly one `agy-implementer` run and one sequential `agy-verifier` run on verified secondary `tmx-node-55619bd5`. Both ran from the live project at `~/.local/share/agy-1497-secondary/worktree`, using the controller-side private stream runner. No additional prompt or pilot replay is authorized. Existing High and approval settings were preserved; Origin was excluded.

The implementer receipt (`agy-1514-native-implementer`) is **INCOMPLETE**, with `producer_exit_code: 255` and no terminal usage. Its model and token totals are unknown. Partial output and recovered scoped edits are not evidence of production-task success. The separate verifier receipt (`agy-1514-native-verifier`) has terminal SUCCESS and producer exit 0, but its review PASS was contradicted by deterministic tests: 92 of 93 passed, with `capture.py` accepting quota `NaN` and returning INCOMPLETE/2 instead of rejecting the quota with 64. Model review is not a substitute for repository gates.

The controller repair rejects non-finite quota constants before capture; regression cases include `NaN`, `Infinity` and `-Infinity`. Raw model streams and diagnostics stay private and outside Git. Earlier test counts below are historical receipts, not counts for this repair.

### Controller repair checks

| Check | Result |
|---|---|
| `TMPDIR=/dev/shm/agy-1514-tests PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_agy*.py' -v` | PASS: 93 tests, including all three non-finite quota constants |
| Readiness discovery (`test_antigravity_readiness.py`) | PASS: 7 tests |
| Changed Python compilation / changed shell `bash -n` | PASS |
| `python3 scripts/ci/repo_gate.py --base origin/master-staging` | PASS: 35 complete-PR paths; syntax, secret/artifact hygiene and debt ratchets passed against refreshed base `1a5af217f3ef9815ce31068d547ad28b69dd8ac7` |
| `python3 scripts/ci/termux_smoke.py` | PASS on controller Linux/Python 3.12.3, `termux=False`; not native Android validation |
| `python3 scripts/proposals/validate_registry.py` | PASS: 15 proposals |
| `git diff --cached --check` / exact staged path allowlist | PASS: 15 authorized follow-up paths; unrelated `.serena/` excluded |

Shellcheck is unavailable; shell validation here is Bash syntax and deterministic fixtures, not a Shellcheck result. Hosted CodeQL/PR checks are not claimed by these local gates. This repair used no new device connection, model prompt, settings change, Origin access or merge.

## Historical controller-runner receipt (before delegated execution)

`scripts/antigravity/run.py` now makes the filter callable around one **explicitly supplied, separately authorized** producer command. It has no default task and no retries. Complete stdout and stderr are archived privately while the producer runs; normalized final usage and three-line steering stay separate. Process exit is retained independently of the reported CLI status, including SUCCESS followed by transport failure. `capture.py` and `telemetry.py` remain passive. [The complete end-to-end command](FILTERING.md#one-end-to-end-command-for-a-future-authorized-task) uses only the existing pinned secondary SSH alias and shell/CLI on the phone; Python stays on the controller.

The [official headless docs](https://antigravity.google/docs/cli/headless/) were opened and checked for `--print`, output formats, stdout/stderr separation, `init` / `step_update` / `result`, optional model identity, settings-based permissions and cumulative session counters. The example stays with flags recorded in the installed 1.4.5 help; no newer multi-turn input flag is assumed. The last `result.usage` is retained, never summed with step snapshots. Per-run tokens, explicit manual `/usage` observations and unrelated router invocation counters remain distinct; no quota, cost, or default model is invented.

| Current check | Result |
|---|---|
| `TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_agy*.py'` | PASS: 87 tests, including 16 new one-shot runner fixtures |
| Readiness suite (`test_antigravity_readiness.py`) | PASS: 7 tests |
| `python3 scripts/ci/repo_gate.py --base origin/master-staging` | PASS: 35 changed paths across the complete PR, refreshed staging ref |
| `python3 scripts/ci/termux_smoke.py` | PASS on controller Linux, not native Android |
| `python3 scripts/proposals/validate_registry.py` | PASS: 15 proposals |
| Documented Bash examples / `git diff --check` | PASS: syntax only; no example producer was executed |

Fixtures launch only local Python test producers. Coverage includes full binary stdout/stderr, permissions, oversized output, large stderr without pipe deadlock, zero/nonzero/signal exits, contradictory SUCCESS/transport failure, launch failure, missing final result, exclusive directory/symlink rejection before launch, literal argv, stdin forwarding, no retries, invalid quota before launch, cumulative result handling, and stopping the local producer on archive failure. A small read-only boundary review identified the same failure/argv/privacy cases; no external model API or device was used. The shared root disk was near capacity, so temporary fixtures and gate logs used memory-backed `/dev/shm`; no unrelated work was removed.

This continuation made **no `agy` invocation, model request, phone connection, runtime installation, settings edit or Origin access**. Existing High/auto-approve and the unrelated untracked `.serena/` were preserved. Issue registration: https://github.com/timerloggedout-spec/termux-monorepo/issues/1497#issuecomment-6340211852 . PR #1514 remains open/unmerged.

### Exact remaining operational gaps

1. The wrapper has now consumed real secondary stream-json output on installed 1.4.5. The implementer stream was incomplete at transport exit 255; model/token totals remain unknown for that run. The verifier completed, but its PASS missed a deterministic regression. Reliable production-task completion is not established. Do not replay either run or manufacture telemetry from the older JSON pilot.
2. Termux:Boot is installed, but first-launch activation and boot delivery remain unconfirmed. The owner may need to open Termux:Boot once on **Device 2**; a reboot test has not occurred. Whole-app/Android force-stop recovery is not guaranteed.
3. Explicit native implementer and verifier invocation have occurred. Native enumeration/skill UI discovery, internal manifest/tool-restriction loading, nested delegation and full-repository provisioning remain unverified; invocation alone does not prove those surfaces.

The earlier offline/Low handoff below is historical. [SECONDARY-RECOVERY.md](SECONDARY-RECOVERY.md) supersedes it: the pinned secondary was reconnected; High restored with auto-approve byte-preserved; runit replaced its supervised SSH child after controlled `sv term`; fresh pinned SSH and `reconnect` were verified. Neither a new phone check nor a reboot is claimed here.

## Historical passive-filter receipt

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

## Historical outage — superseded by secondary recovery

At that earlier checkpoint, the existing pinned SSH route failed before remote execution and the tailnet reported the secondary offline, last seen at `2026-10-22T08:20:00Z`. Identity inspection, the High correction, source transfer and actual-device filter use had not yet succeeded. This is not current status: recovery and High restoration are recorded above, followed by the bounded delegated stream receipts. No alternate device or Origin was contacted.

The recovery procedure required the existing pinned host key and local canonical marker/account/model before writes, preserved the worktree and pilot result, and used private hash-pinned settings candidates. The completed recovery receipt supersedes that pending procedure; it is not an instruction to repeat settings writes or replay the pilot. Keep candidates and rollback snapshots private.

The phone previously lacked Python on PATH. Run the passive Python filter in the controller against an **existing** secondary stream-json capture if no native runtime exists; preserve its complete stdout/stderr capture and write the concise steering artifact separately. Do not fabricate stream-json from a JSON-format pilot or label a synthetic fixture real telemetry. Installing Python, making a new model request, or claiming a native phone run is outside this continuation.

## GitHub boundary

Issue #1497 is the tracking record using the documented GitHub fallback. Live PR #1514 is on `cue/1497-operational-device2`, targeting `master-staging`; the handoff's older provisioning branch is not its live head. Scope registration: https://github.com/timerloggedout-spec/termux-monorepo/issues/1497#issuecomment-6336367544 . Leave the issue open and PR unmerged until the owner decides otherwise. Offline integration is not full provisioning completion.
