# Synchronization Audit Report

**Repository:** [`timerloggedout-spec/termux-monorepo`](https://github.com/timerloggedout-spec/termux-monorepo)
**Audit date:** 2026-08-21 UTC
**Prepared by:** Manus AI
**Publication branch:** `manus/sync-audit-2026-08-21`

> **Decision:** The controlled promotion path is **blocked**. `master` is locally dual-gate clean and its current Render deployment is live, but no named GitHub repository-gate or Termux-smoke run was found for its exact current SHA. `master-staging` has a current local Termux-smoke pass but fails the local repository gate on a Python syntax error and has no successful staging deployment. `termux-smoke` has an exact-head successful GitHub smoke run and a local repository-gate pass, but remains materially divergent from staging. No branch rewrite, merge, closure, redeploy, or tracker mutation was performed.

## Scope, evidence rules, and completion standard

This report supersedes the 2026-08-18 audit as a **fresh evidence pass**. GitHub PR, issue, Actions, Git history, Linear, and Render data were queried again on 2026-08-21. Where exact-head GitHub gate evidence was missing, the declared scripts were executed only in clean, detached, disposable worktrees. The audit did not reuse an earlier conclusion as present evidence.

A relationship is **verified** only when GitHub exposes a native issue-closing link or when Linear contains an explicit GitHub PR URL, including a Linear attachment URL. A textual PR number, matching branch name, or similar title is a **candidate** only; candidates are not used to justify tracker changes. This audit made no tracker writes.

A work item is not complete merely because its PR merged. Completion requires relevant checks, presence on the intended staging spine, aligned GitHub and Linear state, and appropriate successful deployment evidence. The live operational proposals in Issues [#175][10], [#192][11], and [#268][9] are therefore not completion evidence for an individual change.

| Evidence source | Fresh coverage | Result |
|---|---:|---|
| GitHub pull requests | 209 total | 31 open, 120 merged, and 58 closed without merge. [1] |
| Open-PR readiness | 31 open | 2 `CLEAN`, 17 `DIRTY`, 6 `UNSTABLE`, and 6 `UNKNOWN`; only 6 have an approved review decision, while 6 have changes requested. [1] |
| Native GitHub issue links | All PR states | 23 PRs expose one or more native closing links: 4 open, 11 merged, and 8 closed-unmerged. [1] |
| GitHub issues | 70 total | 64 open and 6 closed; Issue [#50][8] remains the controlled-spine recovery tracker. [8] |
| Linear | 275 work items | 137 Done, 114 Triage, 11 In Progress, 7 Todo, 5 Backlog, and 1 Canceled. Ten active items have neither assignee nor delegate. |
| Render | 4 matching web services | One `master` service is live at the current production SHA; all three `master-staging` services lack a successful current deployment. [6] [7] |

## Spine health

| Spine | Exact head and divergence | Repository-gate evidence | Termux-smoke evidence | Deployment evidence | Verdict |
|---|---|---|---|---|---|
| `master` | [`3ee4b9e50911a59561a5f199ca9a22c2deb780d5`][3]. It is 61 commits ahead of and 18 behind `master-staging`. | No named GitHub run was returned for the exact SHA. The fresh local disposable-worktree execution of `python3 scripts/ci/repo_gate.py` exited 0. | No named GitHub run was returned for the exact SHA. The fresh local disposable-worktree execution of `python3 scripts/ci/termux_smoke.py --json` exited 0. | `termux-readme-extractor` deployed this exact SHA and is `live`. [6] | **Locally dual-gate healthy, but GitHub exact-head gate evidence is missing.** This does not authorize promotion while the other controlled spines remain unhealthy. |
| `master-staging` | [`d33842a807f83bf88041f28ee3775ab4d6e03f2c`][4]. It is 18 commits ahead of and 61 behind `master`; it is 387 ahead of and 5 behind `termux-smoke`. | No named GitHub run was returned for the exact SHA. Fresh local gate exited 1: `archwiz/linear_sync.py:237: invalid syntax`. | No named GitHub run was returned for the exact SHA. Fresh local `termux_smoke.py --json` exited 0. | v3 and v2 both `build_failed` at this exact SHA. v1 has no deployment for this SHA; its latest recorded deployment is an earlier staging commit and also failed. [7] | **Unhealthy and ineligible for promotion.** The repository-gate failure and missing successful current deployment are hard blockers. |
| `termux-smoke` | [`d5116612803ab8207f7aa37902a383e269f57926`][5]. It is 5 commits ahead of and 387 behind `master-staging`. | No named GitHub repository-gate run was returned for the exact SHA. Fresh local gate exited 0. | Exact-head GitHub `termux smoke` run [`31895158871`][2] succeeded. | No Render service tracks this branch. | **Gate-evidenced but unsynchronized.** Do not regard a successful smoke run as promotion readiness while its staging divergence remains 387 commits. |

The staging gate no longer exhibits the prior report's `repo_gate.py` indentation failure. The fresh failure is instead a Python syntax failure in `archwiz/linear_sync.py`; the prior explanation must not be carried forward.

## GitHub PR and issue reconciliation

The current PR inventory contains 31 open PRs, 120 merged PRs, and 58 PRs closed without merge. The open set has only two `CLEAN` merge states, but `CLEAN` is not enough for completion: PR [#34][16] targets `termux-smoke` and has successful listed checks but no recorded review decision, while PR [#7][17] targets `master-staging`, has only its recorded review automation check, and its explicitly linked Linear work item is still `Todo` and unowned. Neither qualifies as Done.

| Open PR / GitHub relationship | Current condition | Verified relationship and tracker state | Completion decision |
|---|---|---|---|
| [#92][12] | Targets `master`; `DIRTY`; current listed checks include failed `review / review` and failed GitLab CI. | **Verified:** Linear `TER-120`, `TER-67`, and `TER-69` each attach the same explicit GitHub PR URL. All are In Progress, assigned to LoggedOut Timer, and delegated to Devin. [13] [14] [15] | **Not complete.** Its head is absent from both `master-staging` and `master`; it also lacks clean merge state and current passing checks. |
| [#48][13] | Targets `master-staging`; `DIRTY`; `sync-linear`, `review / review`, and Aikido checks are failed. | **Verified:** Linear `TER-71` attaches the explicit repository PR URL; it is In Progress, assigned to LoggedOut Timer, and delegated to Devin. [15] | **Not complete.** Its head is absent from staging and production, and it has no clean/passing PR evidence. |
| [#8][14] | Targets `master-staging`; `DIRTY`; only `Devin Review` is listed as successful. | **Verified:** Linear `TER-11` attaches the explicit repository PR URL; it is In Progress, assigned to LoggedOut Timer, and delegated to Codex. Its description records the dirty staging base as a blocker. [14] | **Not complete.** The head is absent from staging and production; staging itself fails the repository gate. |
| [#6][18] | Targets `master-staging`; `DIRTY`; listed hygiene and smoke checks pass. | **Candidate only:** Linear `TER-9` mentions “PR #6,” but the audited metadata does not supply an explicit repository PR URL. `TER-10` is Backlog. | **Not complete.** Do not use the candidate association for tracker changes; the PR head is absent from staging and production. |
| [#69][19] | Targets feature branch `feature/proposal-vote-promote`; `DIRTY`; failing workflow checks. | **Candidate only:** Linear `TER-116` is In Progress but no explicit repository PR URL was verified in its audited metadata. | **Outside the controlled spines.** It cannot support a promotion decision. |

The four open native GitHub closing links are [#143 → #117][20], [#137 → #109][21], [#131 → #129][22], and [#125 → #124][23]. These are GitHub issue relationships, not evidence of any Linear relationship.

Issue [#50][8] remains open and is the verified GitHub recovery surface for the three spines. Its last audit comment predates this report, so the fresh SHA, local-gate, and Render findings above supersede its head-specific observations. Issue [#268][9] tracks residual Actions observability and bot-trigger noise; its latest update states that the missing `workflow_call` inputs were fixed and does not identify a current master-breaking defect. Issue [#192][11] remains a broad Actions-refinement proposal, while Issue [#175][10] is the operator priority matrix. Both are relevant planning context but do not replace the required gate-and-deployment evidence.

## Linear reconciliation

The Linear workspace has 275 work items. The active recovery records with verified GitHub URLs are the three PR #92 security items, `TER-71` ↔ PR #48, `TER-11` ↔ PR #8, and `TER-21` ↔ PR #7. The latter is explicitly linked but remains `Todo` with neither assignee nor delegate, so it is not aligned with a `CLEAN` PR as a completed work item.

| Linear condition | Fresh finding | Operational implication |
|---|---|---|
| In-progress work | 11 items are In Progress. Five have no delegate: `TER-9`, `TER-7`, `TER-116`, `TER-27`, and `TER-14`. | Ownership is incomplete for several active items; no delegation was changed in this audit. |
| Active and unowned | Ten started/unstarted items have neither assignee nor delegate, including `TER-7`, `TER-27`, `TER-21`, `TER-22`, `TER-23`, `TER-24`, `TER-14`, `TER-3`, `TER-1`, and `TER-4`. | These are stale or unowned work-management gaps, not authority to assign agents automatically. |
| Verified security recovery | `TER-120`, `TER-67`, and `TER-69` are each assigned to LoggedOut Timer, delegated to Devin, and attach PR #92. [13] [14] [15] | The ownership exists, but the GitHub PR is dirty and not on either controlled spine. |
| Verified submodule recovery | `TER-11` is assigned to LoggedOut Timer, delegated to Codex, and attaches PR #8. [14] | Its own description records the dirty staging base; it remains blocked pending gate recovery. |
| Verified hub recovery | `TER-71` is assigned to LoggedOut Timer, delegated to Devin, and attaches PR #48. [15] | Its required next steps demand green repository-gate and smoke evidence before merge to `master-staging`. |

No fresh Linear delegation was applied. The narrow delegation exception was not used because no existing item both clearly owned a newly verified blocker and identified an unambiguous available specialist suitable for a write.

## Render deployment matrix

| Service | Branch and current service configuration | Latest deployment evidence | Verified result | Completion effect |
|---|---|---|---|---|
| [`termux-readme-extractor`][6] | `master`; root directory is repository root; build `cat README.md`; start `python -m http.server $PORT`. | Deploy `dep-da3qb19t0dsc739uk3kg` checked out `3ee4b9e` and is `live`. [6] | **Live on current production SHA.** | Satisfies deployment evidence for that production commit, but not the broader controlled-path completion standard. |
| [`termux-monorepo_render-webService-v3`][7] | `master-staging`; root directory is empty; build `poetry install`; start `poetry run ./setup.sh`. | Deploy `dep-da3hp3jm8hqs739rtoag` checked out `d33842a` and is `build_failed`. [7] | Build log: Poetry could not find `pyproject.toml` in `/opt/render/project/src` or its parents. | **Hard staging deployment blocker.** |
| [`termux-monorepo_render-webService-v2`][24] | `master-staging`; root directory is empty; build `pip install -r requirements.txt`; start `./setup.sh`. | Deploy `dep-da3hp3jm8hqs739rtod0` checked out `d33842a` and is `build_failed`. [24] | Build log: `requirements.txt` was not found. | **Hard staging deployment blocker.** |
| [`termux-monorepo_render-webService`][25] | `master-staging`; root directory is empty; build `pip install -r requirements.txt`; start `./setup.sh`. | Latest recorded deploy `dep-da3hod3m8hqs739rstog` checked out prior staging SHA `8a699ea`, is `build_failed`, and no deploy for current `d33842a` was returned. [25] | Build log: `requirements.txt` was not found. | **Failure plus current-SHA deployment evidence gap.** Auto-deploy is configured, but a successful current deployment cannot be inferred. |

No deployed service tracks `termux-smoke`. Render configuration was inspected only; no service was redeployed, modified, suspended, or deleted.

## Verified blockers and ordered recovery

The following blockers are evidenced directly by the fresh audit and are ordered by dependency.

| Order | Verified blocker | Required recovery evidence |
|---:|---|---|
| 1 | `master-staging` repository gate fails on `archwiz/linear_sync.py:237: invalid syntax`. | A focused, reviewable repair followed by successful repository-gate and Termux-smoke results on the resulting staging SHA. |
| 2 | Staging v3 cannot find `pyproject.toml`; staging v2 cannot find `requirements.txt`; staging v1 cannot find `requirements.txt` and has no deployment for current `d33842a`. | Validated root directory and build/start commands for each service, followed by successful automatic deployments for the corrected staging SHA. |
| 3 | `termux-smoke` is 387 commits behind staging despite an exact-head smoke success. | A focused reconciliation PR, current gate successes on the resulting smoke head, and divergence reduced under branch policy. |
| 4 | Explicitly linked PRs #92, #48, and #8 are all dirty and their heads are absent from staging and production. | Rebase or replace each narrowly, then require clean merge state, relevant passing checks, explicit Linear/GitHub alignment, staging presence, and applicable deployment evidence. |
| 5 | Ten active Linear items have neither an assignee nor delegate; several records and PRs are stale. | Deliberate human-directed triage or explicit specialist delegation; do not infer ownership from branch names or mentions. |

The audit found no evidence permitting force-pushes, automatic merges, automatic closures, branch retargeting, protected-branch changes, Render changes, or bulk tracker updates.

## References

[1]: https://github.com/timerloggedout-spec/termux-monorepo/pulls "Current GitHub pull-request inventory"
[2]: https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/31895158871 "Exact-head termux smoke success for d511661"
[3]: https://github.com/timerloggedout-spec/termux-monorepo/commit/3ee4b9e50911a59561a5f199ca9a22c2deb780d5 "Current master commit"
[4]: https://github.com/timerloggedout-spec/termux-monorepo/commit/d33842a807f83bf88041f28ee3775ab4d6e03f2c "Current master-staging commit"
[5]: https://github.com/timerloggedout-spec/termux-monorepo/commit/d5116612803ab8207f7aa37902a383e269f57926 "Current termux-smoke commit"
[6]: https://dashboard.render.com/web/srv-d9pq9pajnfac73a73sh0 "termux-readme-extractor Render service"
[7]: https://dashboard.render.com/web/srv-d9pphvdbedkc73e2im00 "termux-monorepo_render-webService-v3 Render service"
[8]: https://github.com/timerloggedout-spec/termux-monorepo/issues/50 "Controlled-spine recovery issue"
[9]: https://github.com/timerloggedout-spec/termux-monorepo/issues/268 "Actions hygiene and Gemini Dispatch issue"
[10]: https://github.com/timerloggedout-spec/termux-monorepo/issues/175 "Operator priority matrix issue"
[11]: https://github.com/timerloggedout-spec/termux-monorepo/issues/192 "Actions refinements proposal"
[12]: https://github.com/timerloggedout-spec/termux-monorepo/pull/92 "Open security recovery PR"
[13]: https://linear.app/termux-monorepo-linear/issue/TER-120/prompt-injection-in-github-workflows-action "TER-120 with explicit PR #92 attachment"
[14]: https://linear.app/termux-monorepo-linear/issue/TER-11/integrate-codex-termux-fork-as-submodule-deepcli-bridge-native-codex "TER-11 with explicit PR #8 attachment"
[15]: https://linear.app/termux-monorepo-linear/issue/TER-71/ter-llm-api-hub-adekai9000-split-ter-41 "TER-71 with explicit PR #48 attachment"
[16]: https://github.com/timerloggedout-spec/termux-monorepo/pull/34 "Open clean PR targeting termux-smoke"
[17]: https://github.com/timerloggedout-spec/termux-monorepo/pull/7 "Open clean PR targeting master-staging"
[18]: https://github.com/timerloggedout-spec/termux-monorepo/pull/6 "Open PR targeting master-staging"
[19]: https://github.com/timerloggedout-spec/termux-monorepo/pull/69 "Open PR targeting feature/proposal-vote-promote"
[20]: https://github.com/timerloggedout-spec/termux-monorepo/pull/143 "Open PR with native close of issue #117"
[21]: https://github.com/timerloggedout-spec/termux-monorepo/pull/137 "Open PR with native close of issue #109"
[22]: https://github.com/timerloggedout-spec/termux-monorepo/pull/131 "Open PR with native close of issue #129"
[23]: https://github.com/timerloggedout-spec/termux-monorepo/pull/125 "Open PR with native close of issue #124"
[24]: https://dashboard.render.com/web/srv-d9pph1qjobas73etpmrg "termux-monorepo_render-webService-v2 Render service"
[25]: https://dashboard.render.com/web/srv-d9oeqmvqj5pc738ke09g "termux-monorepo_render-webService Render service"
