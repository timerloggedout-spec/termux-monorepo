# Operational plan and status — Antigravity #1497

## Latest approved continuation

The owner approved restoring High verbosity and chose a programmatic filter rather than reducing diagnostics. [SECONDARY-RECOVERY.md](SECONDARY-RECOVERY.md) records completed High restoration and pinned SSH recovery, superseding the offline blocker. The dedicated project is live at `~/.local/share/agy-1497-secondary/worktree`. The later authorized implementer/verifier pair consumed real stream-json through the controller filter: the implementer stream ended INCOMPLETE at transport exit 255, with unknown model/token totals; the verifier completed but missed a deterministic quota regression. [FILTERING-VALIDATION.md](FILTERING-VALIDATION.md) separates those receipts from production-task success, which is not claimed. No additional model prompt is authorized. Earlier pilot boundaries below are historical, not current outage claims.

## What was actually delivered before this follow-up

PR #1498 delivered three repository items: immutable research/provenance, a staged collaboration proposal, and a metadata-only readiness utility with seven tests. It did not modify the installed CLI, settings, skills, flows, tasks, native agents, hooks, plugins, or either device. Three of three registered repository items are delivered; that is not 100% of live provisioning.

This follow-up is isolated from concurrent changes in the original issue checkout and from the unrelated dirty shared checkout. Its branch starts at PR #1498's head, retaining the recorded `master-staging` base. It does not absorb newer work from other branches. Nothing is merged or automatically promoted.

## Full plan and acceptance

| Phase | Deliverable | Acceptance |
|---|---|---|
| 1. Reconcile | Issue, formal reviews, inline comments, checks and existing changes | Distinguish approvals from unavailable reviews and deployment failures |
| 2. Identify | Resolve opaque secondary/origin lineage; verify pinned SSH key and local execution context | Never identify a phone from model/display name alone; never connect to Origin |
| 3. Observe | Installed version/help, supported discovery command, minimal settings allowlist | No reinstall, global config writes, new tunnel, daemon, or invented command |
| 4. Define | Project skill, native implementer and verifier, bounded manual task | Source-confirmed manifest fields; no broad community pack or MCP credentials |
| 5. Isolate | Source-only miniature Git repository with a linked worktree | Only issue assets; private local bare object store; no full monorepo/history download |
| 6. Prove discovery | Run installed `agy agents` from the dedicated worktree | Both exact native agent names returned; no model call required |
| 7. Prove execution | One explicit low-effort implementer prompt creates the exact pilot file | Exact bytes verified independently; no retries after ambiguous submission |
| 8. Verify boundaries | Compare settings hash, tracked source hashes and worktree changes | Global settings unchanged; only pilot result untracked; no unrelated devices/files touched |
| 9. Publish | Focused tests, both repository gates, evidence, commits and GitHub PR | Keep issue open for remaining work; no merge; no fabricated Linear ID |
| 10. Expand later | Full project deployment, native delegation, hooks/plugins/MCP/telemetry/automation | Separate bounded acceptance; do not infer these from a successful tiny pilot |

## Two distinct devices

`tmx-node-55619bd5` is the secondary. `tmx-node-primary` is the damaged-screen Origin and is excluded. The map is grounded in `docs/ops/DEVICE-ACCESS-DIRECTORY.md` at `acb85fc9` and its opaque-name revision `ce536260`, not in peer display names. These files are present in repository lineage but absent from the current staging ancestor; do not claim they were added by this PR. The old home-checkout description is not assumed current: present inspection found no repository marker within the bounded paths checked.

The secondary was reached using the existing pinned SSH route. Host public-key fingerprint matched the pre-existing known-host entry; account context and pre-existing scout workspace corroborated the earlier trusted session. Private connection details and hashes of local account configuration stay out of Git. Transient SSH closures recovered through the existing tailnet route, without enrolling a new machine or changing networking.

The observed installed CLI is **1.4.5**, not historical 1.4.4. This task did not install or update it. Version/help and `agy agents` are supported non-model operations. The phone lacks Python, Node and jq on the inspected PATH; do not claim the Python readiness tests ran natively there or install packages to hide that gap.

## Settings discrepancy (historical) and current verified state

Historically during the initial pilot phase, the secondary's saved `verbosity` was **low**, with `toolPermission: always-proceed` and `artifactReviewPolicy: agent-decides`. That earlier state conflicted with the requested High verbosity. Under the subsequent approved continuation, live controller inspection verified `verbosity: high`, `toolPermission: always-proceed`, and `artifactReviewPolicy: agent-decides` (settings SHA256 `51edacf50944bcc14bd37aea4e1f38e10f90eb0ff8321b7ee7185a6ea48175ff`), superseding the earlier offline/Low handoff. Auto-approve is preserved. No sandbox containment is asserted for Android.

## Native configuration versus workflow prose

Official [custom-agent documentation](https://antigravity.google/docs/subagents/) defines `.agents/agents/<name>.md`, YAML metadata, exact tool names, and optional main/subagent selection. [Skills documentation](https://antigravity.google/docs/skills/) defines `.agents/skills/<name>/SKILL.md`. Those are the only native customization surfaces added here.

The implementer and verifier inherit the active model and global policy; neither changes the saved permission posture. Tool-list scoping reduces exposed tool names but `run_command` can still perform broad shell operations. Instructions and opaque marker files are not an OS security sandbox. A discovered `subagent: true` manifest is not proof of a completed nested delegation.

The initial flow was an explicit manual sequence: preflight → discovery → one writer → independent deterministic verifier → result/limits. It was not a native task scheduler or durable queue. The subsequent recovery deployed a dedicated SSH supervisor and Boot hook; Boot activation/reboot delivery remain unverified. The telemetry layer is now integrated on the controller and has consumed real secondary output, not run natively as Python on the phone. No cron, webhooks, plugins, MCP servers or global agents are claimed. The separate authorized native verifier run does not replace deterministic acceptance tests.

## Thin-worktree adaptation

Adapt the source/config/active-work principle from `docs/ops/LEAN_TERMUX_MONOREPO.md`, and the device-derived worktree lineage in commit `188bbbdd`. Do not copy that older runbook's destructive branch-cleanup or aggressive pruning commands into an active shared checkout.

Transfer only the two agent manifests, the pilot skill, the bounded runner and a provenance marker into a miniature Git bundle. Its commit is a source snapshot, **not** the monorepo commit SHA. Retain the upstream source SHA separately. On the verified secondary, clone this small bundle into a private issue-local bare object store and create one linked worktree. Do not clone the entire monorepo, touch `$HOME/.git`, switch an existing branch, initialize submodules, or copy secrets/session stores. This proves an operational harness, not that all monorepo tools are installed on the phone.

## Reviews and modified considerations

At the audited #1498 head `d7b8022e`, CodeRabbit formally approved; inline review API returned no comments. The earlier independent review found legacy `.agent/skills` detection, fixed in `d7b8022e` with a regression test. Registry, repository gate, Termux smoke on Linux and CodeQL passed. Linux smoke does not establish native Android support.

Four Vercel project deployment statuses failed: `termux-monorepo`, `help-wanted-oversight`, `help-wanted-dash`, and `mcp-hub`. GitHub supplied deployment links and log-inspection hints, not root causes. They remain untriaged deployment failures; do not label them caused by this change or resolved. Other review bots did not complete reviews. ECC security/taxonomy notices passed; its reference-readiness report describes corpus coverage, not a demonstrated defect in the offline checker. Formal approval does not mean all reviews or checks are green.

Modified considerations: operator now authorized secondary operational work, superseding the earlier proposal's blanket Device 2 exclusion. Origin exclusion, no-merge boundary, settings preservation and minimal quota remain. Native schema is now checked against official sources and installed discovery, replacing the earlier instruction to defer agent files until the schema was known. Tracking remains the documented GitHub fallback because Linear requires login. Do not mark it Done or invent a TER ID.

## Rollback and remaining boundaries

Use the exact private issue root `$HOME/.local/share/agy-1497-secondary` only. Before removal, inspect worktree status and preserve any user edits/results. Remove the linked worktree with Git only after confirming it contains no new work, then remove the issue-local bare store and source bundle if retained. Never run `git clean`, forced worktree removal, global garbage collection or reset in another checkout. The controller repair changes no global configuration; recovery rollback is documented separately in [SECONDARY-RECOVERY.md](SECONDARY-RECOVERY.md). Preserve approved High and existing approval policies unless separately authorized. Revert repository commits normally; never force-push.

Runtime results and exact validation commands belong in `OPERATIONAL-VALIDATION.md`; pending steps must not be described as successful before execution.
