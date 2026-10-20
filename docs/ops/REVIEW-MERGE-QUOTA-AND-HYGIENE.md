# Review, Merge, Quota, and Repository Hygiene Operating Contract

**Status:** proposed operating contract, evidence snapshot 2026-10-19 UTC  
**Scope:** `timerloggedout-spec/termux-monorepo`  
**Intent:** automate routine review orchestration and safe merges without turning every bot status into approval or letting quota-consuming workflows cancel one another blindly.

## Executive summary

Automation should be the default for *routing, evidence collection, waiting, retries, and merge eligibility*. It must not treat a green bot status as a human approval, and it must not merge merely because a PR is old or a schedule-reduction change appears low risk.

Recommended control loop:

1. **Classify** PR risk and changed paths; detect duplicate/overlapping work.
2. **Request review** from configured CODEOWNERS / trusted reviewers; dispatch existing review bots once per head SHA.
3. **Validate** only checks required for that risk tier; distinguish code failures from provider-capacity failures.
4. **Wait adaptively** on active checks and reviewers. Poll only after a state change, a bounded delay, or a documented timeout.
5. **Enable GitHub auto-merge** only after required protections are verified and the PR is eligible; GitHub merges when branch protection/rules and required reviews/checks are satisfied.
6. **Reconcile** merge result and post-merge health; if a check fails, stop and classify rather than launch an unbounded retry storm.

## Evidence snapshot (not a claim of exhaustive repository enumeration)

### Planning-lane quota PR #1278

- PR: https://github.com/timerloggedout-spec/termux-monorepo/pull/1278
- State at snapshot: open, mergeable, not merged; 4 changed files, 4 commits.
- Intended change: reduce planning-lane scheduled starts by roughly 50/day while preserving event-driven `workflow_run` triggers.
- Review submissions returned by GitHub: **none** at snapshot.
- Devin Review and CodeRabbit status contexts: success.
- Four Vercel contexts (help-wanted-dash, help-wanted-oversight, mcp-hub, termux-monorepo): failure URLs indicate build-rate-limit / provider capacity, not a source-code test failure. Treat as non-gating only if repository policy explicitly classifies them that way.
- Important: **bot status success is not a submitted APPROVED review**. The repo metadata says auto-merge is allowed, but this snapshot does not establish the active branch-protection/ruleset requirements. Therefore, enabling auto-merge before checking protections could merge without a meaningful review if no required review rule applies.

### Related open PRs that need deliberate triage

- #1292 — Actions matrix upgrade and capacity-lag classification; open and non-mergeable at snapshot. It is a broad current operational lane; check overlap with the matrix/skip-cancel work in #1245 and prior extracted fixes before merging.
- #1289 — focused Operations Cadence Audit extraction from #684; open and mergeable. Its audit run succeeded and produced an advisory artifact; findings describe schedule-contract drift, not failed workflow executions. Remaining in-progress checks should be observed before promotion.
- #1288 — authenticated, fail-closed GitLab reconciliation; open and mergeable. No runtime GitLab reconciliation evidence was available in this snapshot. GitLab credentials/configuration are not inspectable through this connector; do not claim a live sync was tested.
- #1287 — session-recon/skills note; open and non-mergeable. Likely low durable value relative to functional work; verify whether its evidence is stale and whether the same note has already landed elsewhere before keeping it open.
- #1286 — temporal integrity / Historical Corpus Explorer proposal lane; separate from cadence and GitLab work. Keep its validation and explorer UI/deployment gap visible.
- #1284 — names-only ML connector probe; separate lane, with an explicitly bounded scope. Verify its current SHA and dual gate, not just its historical notes.
- #1278 — quota/cadence change; requires actual review/branch-policy verification before enabling auto-merge.
- #1274 — draft/reference planning queue; do not deploy merely because it is open.
- #1252 and #1249 — auth/tunnel canary pair; check dependency and evidence freshness together.
- #1246 — procurement-adoption/edge-evidence contracts; verify parent issue/requirements and current checks.
- Older open PRs include #1223, #1201, #1125, #1117 and several #1100-series test additions. Treat age as a **triage signal**, not a close/merge criterion. Compare each diff against current `master`, search for superseding merged PRs, and preserve unique test coverage before deciding.

PR links are navigable from the repository's Pull requests page. Search results are paginated/limited; this is a prioritization sample, not a complete PR inventory.

### Stale branches and closed work

Branch search returned old dated candidates such as:
- `ops/evidence-led-skill-refresh-2026-09-15`
- `ops/biudl-evidence-substrate-2026-09-27`
- `docs/paper2agent-scientific-factory-proposal-2026-09-29`
- `feat/briefing-2026-09-30-evidence-integration`
- `feat/briefing-evidence-upgrades-2026-09-29`
- `ops/unified-cadence-2026-09`
- session branches from 2026-09-20.

A date in a branch name does **not** prove it is stale. For each candidate, compare merge-base/head with `master`, map it to open PRs, and check whether its unique commits are already reachable from `master`. Delete only after confirming merged/superseded status and after an explicit cleanup policy permits deletion.

Closed PR examples establish useful patterns:
- #1285 and #1282 were merged.
- #1243 was closed as superseded by #1244.
- #1238 was merged to restore the canonical adaptive-wait skill.
These are historical reference points; do not reopen a closed PR when a focused fresh-master extraction is safer.

The stale-issue query returned no matches for the requested age filter, while the connector's recent/closed issue endpoint returned a mixed sample with some records lacking state/timestamps. This is **insufficient evidence** to classify every old issue. Re-query issue state/updated time before closing or relabeling old issues. Historical incident tickets and overflow threads may be deliberate evidence archives rather than actionable bugs.

## How reviews and merges should be ensured

### Required governance controls

1. **Ruleset / branch protection**
   - Require at least one approving review from an eligible reviewer for production code and workflow changes.
   - Dismiss stale approvals after new commits; require approval of the latest push where supported.
   - Require code-owner review for `.github/workflows/**`, `scripts/ci/**`, security/credential paths, and production deployment paths.
   - Require the repository's minimal correctness gates (repo gate, workflow-surface policy, targeted tests, and relevant smoke/portability gate). Keep provider quota failures classified separately only where policy says they are non-gating.
   - Require branch to be up to date or use a merge queue that validates the merge group.
   - Block force pushes and deletion of the protected default branch.
   - Verify the ruleset through the GitHub repository/ruleset API/UI; repository metadata alone does not prove these requirements are active.

2. **Review orchestration**
   - Automatically request CODEOWNERS and the configured reviewer team on ready-for-review PRs.
   - Trigger automated reviews on PR open, ready-for-review, and new head SHA; deduplicate by `(PR number, head SHA, reviewer provider)`.
   - If a provider is rate-limited, record `deferred_capacity` and wait for its next reset; do not repeatedly dispatch the same review.
   - Bot comments and status checks are evidence, not approval votes. Only GitHub review state `APPROVED` by an eligible reviewer counts toward required approval.

3. **Auto-merge**
   - After the PR has a real eligible approval, all required checks are green, no unresolved blocking review threads remain, and the base/head relationship is current, enable GitHub auto-merge.
   - Let GitHub's configured rules decide when the merge becomes possible. Do not have a custom workflow call immediate merge as a substitute for branch protections.
   - For untrusted external/imported code (including GitLab-origin code), require explicit trusted review and run the relevant checks in a constrained context before allowing privileged workflows or secrets.
   - Do not automatically merge stale, broad, non-mergeable, draft, conflicted, or poorly scoped PRs.

4. **Fallback/escalation**
   - If review is absent beyond the configured SLA, request it once and escalate to the maintainers' queue; do not spam mentions.
   - If required checks are waiting on provider capacity, mark the PR `blocked:capacity` and wait. If code checks fail, collect the failing job/step and create one deduplicated repair item.
   - If no eligible reviewer is configured, stop before enabling auto-merge and report the missing governance configuration.

### Immediate next action for #1278

1. Verify active branch protection/rulesets and identify the eligible reviewer team.
2. Request review from that configured team (do not guess individual usernames).
3. Confirm the schedule-only diff and that event-driven triggers remain intact.
4. Check required checks on the current head, explicitly classifying the Vercel build-rate-limit contexts under existing policy.
5. Enable auto-merge only after approval and required checks are demonstrably satisfied.

## Cancellation and trigger efficiency

A cancelled Actions run is not always a trigger that was "called in order to cancel it." Two separate costs exist:

- **Run creation cost:** an event/schedule starts a workflow run.
- **Supersession cost:** a newer run enters the same concurrency group and GitHub cancels an older in-progress run when `cancel-in-progress: true`.

A job-level `if:` on a `workflow_run` event can skip the job, but GitHub has already created the workflow run record. Avoid creating runs only to skip them whenever the event can be narrowed earlier; where the platform still creates the run, keep the gate cheap and read-only.

### Policy

- **Do not use `cancel-in-progress: true` by default.** Use it only for replaceable, idempotent work where the newest input supersedes the older one (e.g. a single per-PR-head advisory report). Use `false` for queues, release/promotion, evidence writes, migrations, and work whose partial cancellation loses value.
- Key concurrency on the true unit of replacement: PR number + head SHA, or repository + immutable input version. Avoid a global group that makes unrelated PRs cancel each other.
- Narrow `workflow_run` parents to the smallest required set; keep event-driven triggers where they replace polling.
- Prefer one scheduled reconciler over multiple schedules that each poll the same inventory. Keep the existing workflow ID when consolidating schedules; do not create duplicate cron workflows.
- Schedule work at staggered UTC minutes; do not align many jobs at minute 0. Add timezone explicitly where supported by the repository's schedule contract.
- Before dispatching, inspect recent run state once and skip only when an equivalent run is already active for the same immutable input.
- For quota APIs, use conditional requests/ETags where supported, pagination only when needed, bounded retries with exponential backoff and jitter, and respect `Retry-After` / rate-limit reset headers. Do not repeatedly fetch the full run list or all PR checks in a tight loop.
- Poll by state transitions, not a fixed high-frequency loop: wait for `workflow_run`, `check_suite`, review, or PR events first; use a bounded adaptive wait only as fallback.
- Treat cancelled runs as an audit outcome. Determine whether they were superseded, manually cancelled, or cancelled by a timeout/runner; then verify a successful successor for the same input before marking the cancellation expected.

### Preflight checklist before any trigger/dispatch

- Is there already an active run for this same input?
- Is this run idempotent and safely replaceable?
- Will this event fan out into another workflow via `workflow_run`?
- Does the run need a schedule, or is an event trigger already sufficient?
- Can a single aggregator read a cached/conditional inventory instead?
- What is the quota budget and retry-after/reset time?
- What evidence will prove completion, and what is the timeout/escalation path?

## Collaboration and evidence format

Every automation lane should publish a compact, machine-readable record with:
- `subject` (PR/issue/workflow/run identifier)
- `input_sha` or immutable input version
- `decision` (`run`, `wait`, `skip_duplicate`, `defer_capacity`, `escalate`, `enable_auto_merge`)
- `reason` and the exact policy/rule that permitted the decision
- `checks` and review states, with timestamps
- `superseded_by` for cancelled work
- `next_action_at` rather than repeated immediate polling
- links to the evidence artifact and relevant PR/issue.

Keep the human-readable matrix as the index and store full run evidence as bounded artifacts. Avoid putting tokens, secrets, private device mappings, or sensitive payloads in the record.

## Explicit limits of this audit

- This is a read-only evidence snapshot plus operating recommendations. It does not change repository rulesets, request a reviewer, enable auto-merge, merge or close PRs, or delete branches.
- The GitHub connector can report repo-level `allow_auto_merge`, but the snapshot did not verify branch-protection/ruleset requirements.
- GitLab secret/config state and actual authenticated GitLab reconciliation were not accessible through the available connector.
- Search results are bounded and some issue results lacked state/timestamps. Confirm current state before any destructive cleanup.


## Implemented: fail-closed PR auto-merge readiness gate

This PR now includes an event-driven implementation:

- `.github/workflows/governed-pr-auto-merge-readiness.yml`
- `scripts/ci/pr_merge_readiness.py`
- `tests/test_pr_merge_readiness.py`

The workflow requests a configured review team on PR open/reopen/ready-for-review events (when `GOVERNED_REVIEW_TEAM` is set), deduplicating the request by reading the requested-reviewers endpoint. Submitted reviews (only an `APPROVED` event) or explicit workflow dispatch trigger the merge-readiness evaluation. It has no cron and no automatic polling loop. It gathers one bounded PR/protection/review snapshot, runs the deterministic evaluator and its unit tests, publishes a JSON decision to the Actions job summary, and enables GitHub auto-merge only when every gate passes.

### Fail-closed eligibility contract

All conditions must hold:

1. Repository variable `GOVERNED_AUTO_MERGE_ENABLED=true`.
2. Repository variable `GOVERNED_AUTOMERGE_APP_CLIENT_ID` and secret `GOVERNED_AUTOMERGE_APP_PRIVATE_KEY` are configured for a dedicated GitHub App installation with narrowly scoped Administration:read, Pull requests:write, Contents:read, Checks:read, and Commit statuses:read permissions. The App token is minted only when the opt-in variable is true; missing credentials fail before mutation. Optional variable `GOVERNED_REVIEW_TEAM` holds the configured team slug for automatic review requests; if absent, no team is guessed or pinged.
3. The target branch protection can be read; missing/forbidden protection data blocks.
4. At least one approving review is required by branch protection.
5. Stale approvals are dismissed or approval of the latest push is required.
6. At least one required status check is configured.
7. Required conversation resolution is enabled.
8. PR is open, non-draft, merge state is `CLEAN`, and carries the explicit `automerge:eligible` label.
9. The current head SHA has enough approvals from distinct, non-bot human reviewers other than the PR author; each counted approval must reference that exact head SHA.
10. A current-head human `CHANGES_REQUESTED` review blocks the decision.

If the API cannot prove a prerequisite, the evaluator returns `wait`; it does not merge, comment, or start a retry loop. GitHub's own required checks and protections still govern the eventual merge after auto-merge is enabled.

### Security boundary and activation

The workflow checks out policy code from the trusted default branch, not the reviewed PR head. This prevents an untrusted PR from replacing the evaluator and then executing modified policy code with a write-capable token. The new workflow becomes active after its code lands on the default branch. Do not enable the repository variable until the branch protection requirements above are verified. Add the `automerge:eligible` label only to deliberately opted-in, appropriately scoped PRs; never blanket-label the backlog.

The initial implementation reads the classic branch-protection endpoint. If the repository uses rulesets without equivalent classic protection data, it fails closed. Add and test a ruleset-aware reader before relying on auto-merge for that configuration. The dedicated App must be installed on this repository and granted the permissions listed above; a permission/endpoint error is deliberately treated as "not verified". This is intentionally not implemented with a long-lived personal access token.

### Validation status

The evaluator has nine deterministic unit tests covering the eligible path, disabled switch, unavailable protection, stale-head approval, bot/author exclusion, latest review precedence, missing checks, missing conversation-resolution policy, and missing opt-in label. The tests are included in the workflow before any mutation. A successful remote workflow run is still required to validate GitHub's actual permission and branch-protection behavior; this PR does not claim that the auto-merge gate is active in production.

## Reconciliation map and sequencing

Use this order to minimize duplicate work and preserve unique changes:

| Lane | Related PRs | Harmonization rule |
|---|---|---|
| PR review / merge governance | #1293, #1278 | Land and verify the guard before enabling the repository variable; require an explicit opt-in label |
| Cadence audit | #1289, #684, #1292, #1290 | Prefer the focused audit extraction; compare cadence changes by workflow path before taking the broad matrix PR |
| GitLab sync | #1288, #311 | Treat #1288 as the safer reconciliation direction; require a real authenticated dry run before considering any write-capable sync |
| Actions matrix / cancellation | #1292, #1260, #684 | Preserve workflow IDs and existing event triggers; consolidate only after diff-level overlap review |
| Temporal integrity | #1286 | Keep independent validation and Explorer/deployment evidence separate from quota changes |
| Tunnel/auth canary | #1252, #1249 | Review as a dependency pair; don't promote either on stale status alone |
| Research / planning | #1284, #1274, #1246 | Keep experimental and procurement contracts separate from production promotion gates |

For each older PR or branch, compare the unique commit set against `master`, inspect its changed-file overlap with active PRs, check for a merged replacement, and record one disposition: `keep`, `extract`, `superseded`, `blocked`, or `archive`. Age is evidence for triage, not a disposition by itself.