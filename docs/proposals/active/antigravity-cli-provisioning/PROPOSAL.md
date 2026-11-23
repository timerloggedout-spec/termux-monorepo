# Antigravity CLI: collaborative utilization and initial provisioning

**Operational follow-up:** the operator subsequently authorized identity-verified secondary work. See [full operational plan](OPERATIONAL.md) and [actual device results and limits](OPERATIONAL-VALIDATION.md). That authorization supersedes the earlier Device 2 exclusion below, not the Origin exclusion or no-merge/settings boundaries. The original stages below describe #1498's historical delivery, not the follow-up's current runtime status.

Issue [#1497](https://github.com/timerloggedout-spec/termux-monorepo/issues/1497) now has a versioned research baseline and a non-mutating readiness tool. This is initial repository provisioning, not a claim that Antigravity has been installed or configured on a device.

Keep the user's existing **high verbosity and auto-approve**. Do not apply the seed's conservative settings example. No model prompt is needed to prepare this lane. [Source checks and corrections](source.md) distinguish documented capabilities, user-reported observations, and proposals.

## Useful collaboration first

| Use case | Responsibility split | Success evidence |
|---|---|---|
| Repository reconnaissance | Cue scopes the issue; cartographer identifies only the relevant entry points | Paths and bounded dependency notes, no whole-home crawl |
| Documentation research | Researcher checks official sources; verifier challenges assumptions | Claim/source matrix with target-build uncertainties |
| Bounded code maintenance | Implementer owns one issue worktree; verifier runs focused tests | Minimal patch, exact commits, tests and dual gates |
| MCP inventory | Researcher lists tool names/scopes without credentials | Explicit read/write/auth boundaries; no inferred connector from remote access |
| Documentation synchronization | Maintainer compares interfaces with docs | Source-backed changes attached to a registered item |
| Mobile supervision | Cue coordinates host-local execution through an already authorized channel | Host/session identity checked privately; no tunnel URLs in git |

Start with coordinator, one implementer, and an independent verifier. These are proposed responsibilities, not installed native agents. Do not manufacture agent files, hooks, or plugins until the installed build's actual discovery/schema contract is established.

## Initial provisioning stages

1. **Repository baseline (this PR).** Fresh `master-staging` ref, clean issue worktree, registered work items, immutable seed, source corrections, readiness command, focused tests, validation record. Push every issue commit; no merge or auto-merge.
2. **Target-host observation (pending, not executed).** On a separately authorized host, record `agy --version` and help output without starting a conversation; inspect current configuration privately, capturing only allowlisted non-secret facts. Confirm the build supports these non-interactive flags before invoking wrappers. Preserve verbosity and approval settings exactly. Record OS/architecture and whether execution is native Termux or another host. Never access Device 2 or Origin backup under this issue.
3. **One bounded pilot (pending).** After explicit target-host execution authorization, use the supported project discovery path. Reuse existing repository procedures rather than install a broad community bundle. Confirm discovery through build-supported UI/help. Have one implementer and a verifier use separate ownership boundaries. Do not execute a model pilot under the present no-prompts restriction.
4. **Expansion (separate item/authorization).** Only after the pilot proves dispatch, return, verification, and teardown: consider plugin packaging, hooks, remote daemon lifecycle, and scheduling. None is enabled here. Any recurring automation requires its own execution/monitoring design.

## Read-only readiness command

From the issue worktree:

```bash
python3 scripts/antigravity/readiness.py --workspace "$PWD"
python3 -m unittest discover -s tests -p 'test_antigravity_readiness.py' -v
python3 scripts/proposals/validate_registry.py
python3 scripts/ci/repo_gate.py --base origin/master-staging
python3 scripts/ci/termux_smoke.py
```

The inventory uses only Python's standard library, local path metadata, and executable discovery on PATH. It never executes `agy`, reads configuration contents, scans the home directory, contacts services, or writes files. It accepts a `.git` directory or worktree marker file. JSON reports only booleans/counters: workspace/repository marker, CLI availability, and presence of project skills/agents/hooks (including legacy `.agent/skills`). Presence is not validity or trusted containment. It does not follow or parse a gitdir reference and does not validate plugin/agent/hook schemas.

Exit **0** means repository marker and CLI executable are present; exit **2** means a prerequisite is missing. Neither means runtime functionality: `runtime_verified` remains false. An absent CLI is an actionable observation, not a reason to auto-install. Python runtimes may create import bytecode during tests; the inventory itself does not write.

## Proposed task/result contract

This is a handoff design, not a native API or deployed configuration:

```yaml
task_id: AGY-1497-example
issue: https://github.com/timerloggedout-spec/termux-monorepo/issues/1497
item_id: AGY-1497-02
objective: One issue-scoped change with measurable acceptance criteria
workspace: Explicit clean issue worktree
base_sha: Recorded current master-staging SHA
owner: One implementer
verifier: Independent reviewer
allowed: [read scoped files, edit scoped files, run offline tests, commit, push issue branch]
excluded: [merge, unrelated pushes, live settings changes, model prompts, Device 2, Origin backup]
posture: Preserve existing high verbosity and auto-approve
acceptance: [minimal diff, focused tests, dual-gate outcomes, provenance]
result:
  outcome: PASS-or-FAIL-or-UNKNOWN
  commits: []
  changed_paths: []
  checks: []
  unresolved: []
```

Keep credentials and session URLs out of handoffs. Issue-scoped GitHub commits/pushes are already authorized; do not introduce approval pauses for those actions. Auto-approve does not extend the assigned task scope. Hooks and prose are not an OS security sandbox.

## Acceptance and rollback

Repository delivery is accepted when the seed matches its recorded hash, verified claims have direct sources, the readiness contract tests pass, gate evidence is recorded, and all issue commits are on the isolated remote branch. Keep inherited staging defects separate; do not repair unrelated code to obtain a green badge. Runtime readiness remains unknown until a separately authorized target-host check and bounded pilot succeed.

Rollback is an ordinary revert of this issue's commits on a follow-up branch; do not force-push, rewrite history, reset the shared checkout, or change installed configuration. Since this lane does not provision runtime state, there is no daemon, settings migration, or device state to undo. Linear tracking remains unresolved under the documented GitHub fallback; do not mark it Done or fabricate a TER ID.
