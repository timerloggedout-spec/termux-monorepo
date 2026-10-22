# Operational validation — #1497

## Proven on the secondary

The existing pinned SSH route recovered after transient closures. The SSH server public-key fingerprint matched the pre-existing known-host entry; the earlier trusted account/scout context matched. The lineage map distinguishes secondary `tmx-node-55619bd5` from damaged-screen Origin `tmx-node-primary`. No connection to Origin was made.

Installed `agy --version`: **1.4.5**. This task did not install/update the binary. Installed help confirms `--agent`, `--effort`, `--print-timeout`, `--output-format`, `--print`, and the `agents` subcommand. Python, Node and jq were absent from the inspected PATH; no packages were installed.

Only six issue-specific source/provenance files were transferred into a miniature Git repository. Its linked worktree is `$HOME/.local/share/agy-1497-secondary/worktree`; the bare store and two small source bundles are under the same private issue root. The source snapshot commit after review fix is `4e77d048d7da64d51bc3ce74d30e7982efbd768c`, distinct from the monorepo source SHA. Measured issue-root footprint after execution: **288 KiB**. No full monorepo clone/history, source submodules or existing checkout changes were needed.

### One bounded model execution, no retries

From the dedicated secondary worktree:

```bash
bash scripts/antigravity/secondary_pilot.sh preflight
bash scripts/antigravity/secondary_pilot.sh pilot
bash scripts/antigravity/secondary_pilot.sh verify
```

The pilot invokes the installed CLI with `--agent agy-implementer --effort low --print-timeout 90s --output-format json --print <bounded task>`. Returned JSON reports `status: SUCCESS`, `num_turns: 1`, and the created path `pilot-result.txt`. The CLI-reported model duration was 12.216 seconds. There was exactly one model request and no retry.

Independent shell verification confirmed a regular, non-symlink file containing exactly `AGY1497_OK` and one newline (11 bytes). SHA-256: `e61be2a69c087932ddab52c1324f46af2f88b3effe550a562b981eff212edca3`. Binary-safe `cmp` comparison passed. Both tracked and staged Git diffs were empty; `git status --porcelain` showed only `?? pilot-result.txt`. The four deployed code/skill/agent files' SHA-256 values match the tested source snapshot. The settings file's private before/after SHA-256 values matched exactly.

### What this does not prove

At the initial pilot checkpoint, `agy agents` returned exit 0 but no names, including under a terminal. Native enumeration remains **inconclusive**. Explicit `--agent agy-implementer` invocation does not independently prove which manifest/tool restrictions were loaded internally. The later authorized implementer/verifier continuation used real stream-json: the implementer ended INCOMPLETE at transport exit 255 with unknown model/token totals; the verifier completed but missed the deterministic quota regression. See [FILTERING-VALIDATION.md](FILTERING-VALIDATION.md). Nested dispatch, skill reload/discovery UI and entire-monorepo workflows remain unverified. The separate recovery receipt below covers the SSH background service, not production agent success.

Saved verbosity was historically **low** during initial pilot inspection, not requested High; auto-approve was `always-proceed` with `artifactReviewPolicy: agent-decides`. Under the subsequent continuation, live controller inspection verified `verbosity: high`, `toolPermission: always-proceed`, and `artifactReviewPolicy: agent-decides` (settings SHA256 `51edacf50944bcc14bd37aea4e1f38e10f90eb0ff8321b7ee7185a6ea48175ff`), superseding the earlier offline/Low handoff.

## Repository validation

Execution host: Linux x86_64 / Python 3.12.3, not Android.

| Check | Result |
|---|---|
| `python3 -m unittest tests.test_agy_native_contract tests.test_agy_secondary_pilot tests.test_antigravity_readiness -v` | PASS — 19 tests |
| Skill creator `quick_validate.py .agents/skills/agy-native-pilot` | PASS |
| `bash -n scripts/antigravity/secondary_pilot.sh` | PASS on Linux and secondary |
| `python3 scripts/proposals/validate_registry.py` | PASS — 15 proposals |
| `python3 scripts/ci/repo_gate.py --base origin/master-staging` | PASS; existing debt unchanged |
| `python3 scripts/ci/termux_smoke.py` | PASS on Linux; not represented as native Termux Python validation |
| `git diff --check` excluding byte-identical seed inherited from #1498 | PASS |

Independent review found the first exact-byte check could accept a NUL suffix because Bash command substitution discards NULs. Replaced content comparison with binary-safe `cmp`; added `test_nul_suffix_rejected`; all 19 focused tests pass. The fixed runner was fast-forwarded into the clean secondary linked worktree **before** the sole model pilot. No unresolved correctness finding remains from that review.

## Integration status

The original issue checkout gained concurrent unrelated-to-this-follow-up edits while it was being inspected. They were preserved. This follow-up uses `/workspace/termux-agy-operational-1497` and branch `cue/1497-operational-device2`, based on #1498 head `d7b8022e`. It includes the original three proposal/readiness commits because they have not merged into staging. No shared worktree reset/clean, force push, merge or auto-merge was performed.

Original PR #1498: CodeRabbit approved, no inline comments, applicable repository checks passed, four untriaged Vercel deployment status failures. Other unavailable bot reviews are not approvals. These statuses must not be silently reused as approval of the new follow-up commit. Linear remains unresolved under the recorded GitHub fallback. Keep the issue open for native discovery/skill/full-workspace and reliable production-completion gaps; High restoration and explicit verifier invocation supersede the older pending claims.

## Secondary recovery continuation — AGY-1497-09/10

This supersedes the earlier saved-Low and no-Boot/no-service status only for the identity-verified secondary. See [SECONDARY-RECOVERY.md](SECONDARY-RECOVERY.md) for implementation, diagnosis, limits and rollback.

- Strict pinned SSH verification and local canonical marker/account/model matched the secondary. Origin was not contacted; Tailscale settings and SSH keys were unchanged.
- Installed termux-services 0.13-1 and runit 2.3.1; deployed dedicated recovery wrapper/logger, log rotation, WakeLock-first Boot hook and non-killing `reconnect` alias. Original manual listener remains alive; recovery wrapper waits for its exit. No live crash/reboot test.
- Native syntax/config checks, fresh SSH, log/status checks, fresh-zsh alias, exact source hashes and idempotent reinstall passed. Reinstall preserved the complete `.zshrc` hash and manual listener PID.
- Boot installation confirmed for Android user 0. First-launch activation/reboot delivery unverified; owner should open Boot once on the secondary if not already done.
- High restored using the authorized AGY-1497-09 helper and strict controller-side JSON transformation. Whole post-write file matched the candidate; unrelated bytes and `always-proceed`/`agent-decides` unchanged. No new CLI/model prompt or pilot.
- **78 focused Linux fixture tests PASS**, including 13 recovery tests. Proposal registry: 15 proposals PASS. Repo-gate against `origin/master-staging` PASS; Termux smoke PASS on Linux (`termux=False`); Bash syntax and whitespace checks PASS. Fixture tests are not native Android Python/model evidence.
- Broader tests initially failed because the shared root filesystem could not allocate temporary files. Rerunning with `TMPDIR=/dev/shm/agy-1514-tests` passed. Shared-cache cleanup was canceled while waiting for another task's lock; no repository/worktree or in-use cache was deleted.
- Self-review fixed installer-lock descriptor inheritance before deployment. No extra reviewer/model request, broad ADB access, merge, auto-merge, force push or shared reset/cleanup. Pre-existing untracked `.serena/` untouched.

Recorded online/SSH-success evidence does not prove Tailscale never crashed earlier. Historical outage cause remains unestablished. Real filtered stream consumption and explicit verifier invocation are now evidenced, but the implementer stream was incomplete and the verifier PASS missed a deterministic failure. Discovery, internal restrictions, nested dispatch and full provisioning remain open. No additional phone connection, model prompt or settings change was made for the controller repair. PR #1514 stays open and unmerged.
