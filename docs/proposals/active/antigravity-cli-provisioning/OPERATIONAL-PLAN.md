# agy provisioning: operational plan and honest status

**Device 2 is not yet operationally provisioned by this work.** The original repository baseline is complete; the on-phone observation and pilot remain blocked. A working installation was previously reported, but this run has not verified it. See [issue #1497](https://github.com/timerloggedout-spec/termux-monorepo/issues/1497) and [PR #1498](https://github.com/timerloggedout-spec/termux-monorepo/pull/1498).

## What is complete, and what is not

The original three registered deliverables are complete: source/provenance research, collaborative provisioning proposal, and offline readiness inventory with seven tests. This is **3/3 repository deliverables, not 100% provisioning**. Of the original four stages, only the repository baseline is complete; target observation and a bounded pilot are unproven, and expansion is deferred. These stages differ in size, so a percentage would be misleading.

This follow-up adds a repository-local bounded collaboration skill, a task/result template, an opt-in thin-worktree helper with tests, and this full rollout plan. These are repository deliverables, **not changes installed on a phone**. The helper never invokes agy or supplies native-agent registration.

Nothing in this run changes agy settings, High verbosity, auto-approve, authentication, native subagents, hooks, plugin bundles, remote-control services, schedules, or either phone. No agy model prompts are launched.

## Reviews and changed considerations

At the inspected pre-follow-up head `d7b8022e92c161e8326dbce23611c536d115ffa3`, PR #1498 is OPEN against `master-staging`, reviewDecision APPROVED, with one CodeRabbit APPROVED review and zero inline review comments. Its merge state is UNSTABLE. Repository-gate and Termux-smoke checks succeeded; four Vercel deployment contexts failed: help-wanted-dash, help-wanted-oversight, mcp-hub, and termux-monorepo. Their cause has not been established here. Passing review is not deployment success, and a review on this earlier commit is not proof of approval for subsequent edits. **No merge or auto-merge.**

The earlier independent review found missed legacy `.agent/skills` inventory. Commit `d7b8022e` fixed it and added a regression test. That is a metadata-discovery correction, not proof that a CLI loaded a skill.

The current read-only review found no separate, discoverable document literally defining a thin-worktree protocol. Adapt the existing [change-and-validate process](../../../icm/processes/change-and-validate.md), [agent governance](../../../../AGENTS.hum.md), [Linear lifecycle](../../../LINEAR-AGENT-PROTOCOL.md), and [dual gates](../../../ARCHW1Z-GATE.md), rather than claim an undiscovered protocol was copied. If the owner has a separate protocol, reconcile it before wider rollout.

The original proposal excluded Device 2 entirely. The new operator instruction authorizes attempting its setup, **conditional on proving identity**. This supersedes that earlier exclusion only for the verified secondary phone; it never authorizes Origin or its backup. Preserve High verbosity and auto-approve rather than applying the original research's conservative example. Minimize quota use: version/help/metadata first, no gratuitous model test. Prose, sparse checkout, skills, and Git worktrees are not security sandboxes.

## Distinguish the two BLU B160V phones

Device 2 is the secondary Observer/Controller/Executors handset. Origin is the separate damaged-screen handset and is excluded. Two tailnet peers have the same `B160V` display label; one is online and one offline. Neither labels nor online state prove physical identity. Do not assume the offline peer is Origin.

Keep connection details in private SSH configuration, not repository task records. The established alias `termux-device2` has a dedicated known-hosts entry and pinned ED25519 key. Use strict checking; never replace its pin, trust a freshly scanned key, accept-new, weaken authentication, or try the twin as a fallback.

Observed in this run: tailnet is Running; the known secondary peer answers a Tailscale ping through a relay. One SSH attempt through the existing proxy closes at `kex_exchange_identification`, before a server host key is presented or authentication begins. Consequently no device-local command executes and identity is **not proven**. This establishes a transport/SSH blocker, not an agy failure or a wrong password. No Google login is needed for this diagnosis.

Owner recovery: on the physical secondary handset only, open Termux, run `sshd`, keep Termux and Tailscale active, then request a retry. This is a requested action, not one this run performed. Do not regenerate keys or modify the Origin phone to recover access.

## Full rollout, in order

### 1. Establish the private identity gate — blocked

Use the existing SSH alias with strict pinned host-key checking. After successful key verification, read only account name, home/prefix, product model/device, OS/architecture, and the existing CLI executable path. Match these against the prior Device 2 record and owner-confirmed physical role. Duplicate model names alone fail the gate. On any mismatch or missing binding, stop before configuration reads or writes.

Acceptance: authenticated session with matching pinned key and matching device-local facts. Keep unique identifiers private; public evidence should state pass/fail, not serial numbers or secrets.

### 2. Observe the actual CLI build — pending gate 1

Record supported version/help non-interactively without a conversation. Previous observation was CLI 1.4.4, an existing `~/.local/bin` PATH entry, and authenticated access; those are historical facts, not verification from this run. Confirm actual project skill/native-agent discovery paths and schemas using installed help/UI. Inspect only allowlisted, non-secret configuration fields privately. Preserve settings bytes unless a separately necessary, supported change is explicitly scoped. Do not dump credentials, session stores, tunnel URLs, or full configuration.

Acceptance: observed version, discovery contract, approval/verbosity posture unchanged, no reauthentication and no model prompt. Treat CLI presence separately from authentication and runtime operation.

### 3. Create one bounded thin worktree — repository helper ready after validation

Use one new branch and worktree per implementer, pinned to a recorded full local commit SHA. The helper defaults to a JSON dry-run; `--apply` explicitly creates a new local worktree and a per-worktree sparse checkout. It does not fetch, update submodules, clean/reset the source, or alter agy. Existing branch/destination conflicts fail closed. Partial failures must remain visible for inspection, not trigger destructive cleanup.

Independent review found that Git enables the shared repository extension `extensions.worktreeConfig` during sparse setup. This is Git metadata, not agy configuration, but it must not be silent: if not already enabled, apply requires an additional `--enable-worktree-config` opt-in. The helper rejects ambiguous existing shared sparse/core or dormant worktree configuration before that migration. Ordinary worktree/branch creation also updates Git bookkeeping; preserving the source means preserving its files, index, branch and dirty work, not zero Git metadata writes. Sparse settings remain per-worktree. Later plain Git commands must work without helper-specific environment settings.

Start from the reviewed issue commit for the unmerged pilot; for later independent work use a freshly approved `master-staging` base. Sparse paths contain only the bounded collaboration surface and governing material. Root files may also be included by Git cone mode. Expand the sparse set deliberately when a real task needs more files. A thin checkout is not a claim that all repository-wide tests can run inside it.

Example from an existing local checkout, after reading `--help`:

```bash
BASE=$(git rev-parse HEAD)
python3 scripts/antigravity/thin_worktree.py \
  --repo "$PWD" --destination "../agy-1497-pilot" \
  --branch cue/1497-pilot --base "$BASE"
# Inspect the JSON plan; repeat with --apply only for the intended local target.
# If the plan requires it, explicitly opt in with --enable-worktree-config.
```

Before using this on Device 2, repeat gates 1–2 and confirm local Git sparse-worktree support. Never run the helper against an Origin checkout or backup. Do not automatically remove old worktrees.

### 4. Activate useful collaboration surfaces — pending verified device

The repository skill is `.agents/skills/agy-bounded-collaboration/SKILL.md`; its bundled `templates/task.json` carries task/result records. It is not a plugin or native custom-agent definition. Bring only the reviewed issue commit into the authorized Device 2 task worktree. Confirm build-supported skill reload/listing; do not equate tracked files with successful discovery.

Start with coordinator → implementer → independent verifier. The coordinator specifies objective, registered item, pinned base, allowed paths/actions, exclusions and acceptance. The implementer owns one writable branch; verifier uses the resulting commit/read-only review scope and reports checks without silently rewriting implementation. Add cartographer/researcher/documentation maintainer only when their output is needed. Keep external tools/MCP unconfigured until a bounded task needs a verified service/schema.

Do not author fake native-agent frontmatter or copy a broad community bundle. Create actual custom-agent definitions only after confirming the installed schema and capabilities. Preserve auto-approve while enforcing task scope by explicit ownership and operational checks; do not advertise these instructions as OS enforcement.

### 5. Prove one bounded pilot — blocked until preceding gates

First exercise task handoff, worktree creation, deterministic offline checks, result review, and cleanup without a model prompt. Record dispatch and return separately from native agy execution. If actual native-agent/model dispatch is necessary to establish the requested operational status, use only one explicitly bounded minimal task; do not run a swarm or repeated readiness prompts. Until such actual execution is observed, report native dispatch as UNKNOWN, not PASS.

Acceptance: correct Device 2 identity; supported CLI discovery; task assigned and result returned; minimal scoped diff; independent checks; High verbosity and auto-approve preserved; no Origin or backup access; no unrelated writes; exact rollback/cleanup recorded. Report each acceptance item individually. A deterministic offline rehearsal alone does not establish native subagent runtime.

### 6. Expand only after the pilot — deliberately deferred

Plugin packaging, lifecycle hooks, MCP integrations, persistent remote daemon, and recurring schedules are separate scoped changes. Require build support, auth boundaries, audit/log handling, teardown, and monitoring before enabling them. Keep existing working access intact; do not start or stop a daemon just to claim provisioning progress.

## Validation, rollback, and completion

Run focused `test_antigravity*.py` tests, skill format validation, proposal registry, and both repository gates from the full issue worktree. Record Linux evidence honestly; native Termux acceptance must come from the verified phone. See [VALIDATION.md](VALIDATION.md) for actual outcomes and [ITEMS.md](ITEMS.md) for tracked state.

Rollback repository changes through a normal follow-up revert; never force-push or reset the shared dirty checkout. For an owned clean pilot worktree, inspect `git status` and remove with `git worktree remove` without force; branch deletion is a separate reviewed choice. Retain partial failures and uncommitted work for inspection. No phone rollback is needed in this run because no phone state is changed.

Keep the proposal and issue open. The documented GitHub tracking fallback remains in effect; no Linear identifier or Done status is fabricated. Push issue-scoped commits, report current-head review/check status, and leave merge to explicit owner approval.
