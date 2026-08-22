# Synchronization Audit Report

**Repository:** [`timerloggedout-spec/termux-monorepo`](https://github.com/timerloggedout-spec/termux-monorepo)
**Audit date:** 2026-08-22 UTC
**Prepared by:** Manus AI
**Publication branch:** `manus/sync-audit-2026-08-21-r2`

> **Decision:** The promotion path remains **blocked**, but its character has changed since the prior audit. Fresh local disposable-worktree validation passes both required gates on all three current spines. Production is live on its current SHA. The controlling blockers are now the three failed current `master-staging` Render deployments and material divergence among the controlled spines; GitHub does not expose a named exact-head repository-gate or Termux-smoke run for `master` or `master-staging`. No GitHub, Linear, or Render state was altered.

## Evidence discipline and completion standard

This is a new, read-only evidence pass after both `master` and `master-staging` advanced. The earlier report was treated only as history. GitHub pull requests, GitHub issues, Actions runs, Git history, Linear items, Render service configuration, Render deployments, and build logs were queried again on 2026-08-22. When named exact-head GitHub gate evidence was absent, the declared repository gate and Termux smoke commands were run only in clean disposable worktrees.

A relationship is **verified** only when GitHub exposes a native issue-closing link or Linear includes an explicit GitHub PR URL, including an attachment. A matching PR number, branch name, or title is a **candidate** only and is not authority for a tracker write. A PR merge alone is not Done: the full completion standard additionally requires relevant checks, intended staging presence, aligned GitHub and Linear state, and successful applicable deployment evidence.

| Evidence source | Fresh result |
|---|---|
| GitHub PR inventory | 227 total: 32 open, 135 merged, and 60 closed without merge. [1] |
| Open-PR readiness | 2 `CLEAN`, 22 `DIRTY`, 6 `UNSTABLE`, and 2 `UNKNOWN`; four open PRs carry native GitHub issue-closing links. [1] |
| Native closing links by state | 4 open, 14 merged, and 8 closed-unmerged PRs expose native closing links. [1] |
| GitHub issues | 79 total: 73 open and 6 closed. Issue [#50][8] is the controlled-spine recovery tracker; Issues [#175][10], [#192][11], and [#268][9] are open operational context. |
| Linear | 275 items: 137 Done, 114 Triage, 11 In Progress, 7 Todo, 5 Backlog, and 1 Canceled. Ten active items have no assignee and no delegate. |
| Render | One `master` service is live on the current production SHA. All three `master-staging` services failed their current-sha automatic deployment. [6] [7] [24] [25] |

## Current controlled-spine verdicts

| Spine | Exact SHA and divergence | Repository-gate evidence | Termux-smoke evidence | Deployment evidence | Verdict |
|---|---|---|---|---|---|
| `master` | [`0c70299529ecf3e2da0573103f856319e20fa4f4`][3]; 91 commits ahead of and 42 behind `master-staging`. | No named exact-head GitHub run was returned. Fresh local `python3 scripts/ci/repo_gate.py` exited 0. | No named exact-head GitHub run was returned. Fresh local `python3 scripts/ci/termux_smoke.py --json` exited 0. | `termux-readme-extractor` deployment `dep-da4eeoj39src73cfkk7g` is `live` on this exact SHA. [6] | **Locally dual-gate healthy and live, with a GitHub exact-head gate evidence gap.** Not promotion-complete while staging deployment and divergence blockers remain. |
| `master-staging` | [`9bf783ce411f32cdf328195207cd7af1f6c48eda`][4]; 42 commits ahead of and 91 behind `master`; 411 ahead of and 5 behind `termux-smoke`. | No named exact-head GitHub run was returned. Fresh local repository gate exited 0. | No named exact-head GitHub run was returned. Fresh local Termux smoke exited 0. | All three staging services auto-deployed this exact SHA and are `build_failed`. [7] [24] [25] | **Gates locally healthy but deployment-blocked.** This is a material improvement over the prior gate failure, not promotion readiness. |
| `termux-smoke` | [`d5116612803ab8207f7aa37902a383e269f57926`][5]; 5 commits ahead of and 411 behind `master-staging`. | No named exact-head GitHub repository-gate run was returned. Fresh local repository gate exited 0. | Exact-head GitHub `termux smoke` run [`31895158871`][2] succeeded. | No Render service is configured for this branch. | **Dual-gate evidenced but unsynchronized.** The 411-commit staging gap prevents treating its smoke pass as promotion readiness. |

The prior staging `archwiz/linear_sync.py` syntax blocker is **not present** on the current staging SHA: the fresh local repository gate and Termux smoke both pass. That historical failure must not be carried forward.

## GitHub and Linear reconciliation

The active PR portfolio is not generally merge-ready: 22 of 32 open PRs are `DIRTY`. A clean PR is also not automatically complete. PR [#34][16] is `CLEAN` against `termux-smoke` but has no recorded review decision; PR [#7][17] is `CLEAN` against `master-staging`, but its explicitly linked Linear item `TER-21` remains `Todo`, unassigned, and undelegated. Neither meets the completion standard.

| PR | Current GitHub condition | Verified Linear relationship | Completion finding |
|---|---|---|---|
| [#92][12] | Targets `master`; head `e0d9854`; `DIRTY`; GitLab CI and review check fail. | **Verified:** `TER-120` explicitly attaches PR #92 and is In Progress, assigned to LoggedOut Timer, delegated to Devin. [13] | **Not complete.** Its head is absent from current staging and production; it lacks clean/passing PR evidence. |
| [#48][13] | Targets `master-staging`; head `7839eeb`; `DIRTY`; Aikido, review, and `sync-linear` fail. | **Verified:** `TER-71` explicitly links PR #48, is In Progress, assigned to LoggedOut Timer, delegated to Devin. [15] | **Not complete.** Its head is absent from staging and production; relevant checks fail. |
| [#8][14] | Targets `master-staging`; head `f5d428d`; `DIRTY`; only recorded Devin review passes. | **Verified:** `TER-11` explicitly attaches PR #8, is In Progress, assigned to LoggedOut Timer, delegated to Codex. [14] | **Not complete.** Its head is absent from staging and production, and the staging deployment barrier remains. |
| [#6][18] | Targets `master-staging`; `DIRTY`; its listed hygiene checks pass. | **Candidate only:** `TER-9` refers to PR #6 but the audited metadata contains no explicit GitHub PR URL. | **Not complete.** Do not use the candidate association for a tracker write. |
| [#69][19] | Targets `feature/proposal-vote-promote`; `DIRTY`; GitLab, review, and `sync-linear` fail. | **Candidate only:** `TER-116` is In Progress, but audited metadata supplies no explicit repository PR URL. | **Outside controlled spines.** |

The four open native GitHub issue-closing links are [#143 → #117][20], [#137 → #109][21], [#131 → #129][22], and [#125 → #124][23]. These GitHub links do not establish Linear relationships.

Linear continues to show 11 In Progress items. The following started items have no delegate: `TER-9`, `TER-7`, `TER-116`, `TER-27`, and `TER-14`. Ten active items have neither assignee nor delegate, including `TER-7`, `TER-27`, `TER-21`, `TER-22`, `TER-23`, `TER-24`, `TER-14`, `TER-3`, `TER-1`, and `TER-4`. These are stale or unowned-work findings, not authority to auto-assign. No fresh delegation was applied.

## Current Render deployment matrix

| Service | Branch and configuration | Latest deployment | Current build/start evidence | Verdict |
|---|---|---|---|---|
| [`termux-readme-extractor`][6] | `master`; root directory empty; build `cat README.md`; start `python -m http.server $PORT`. | `dep-da4eeoj39src73cfkk7g` on `0c702995` is `live`. | Current production service is live. | **Live.** |
| [`termux-monorepo_render-webService-v3`][7] | `master-staging`; root empty; build `poetry install`; start `poetry run ./setup.sh`. | `dep-da4c6e3bc2fs73fj6610` on `9bf783ce` is `build_failed`. | Current log: Poetry cannot find `pyproject.toml` in `/opt/render/project/src` or its parents. | **Hard staging deployment blocker.** |
| [`termux-monorepo_render-webService-v2`][24] | `master-staging`; root empty; build `pip install -r requirements.txt`; start `./setup.sh`. | `dep-da4c6e00vjus73ai229g` on `9bf783ce` is `build_failed`. | Current log: `requirements.txt` cannot be opened. | **Hard staging deployment blocker.** |
| [`termux-monorepo_render-webService`][25] | `master-staging`; root empty; build `pip install -r requirements.txt`; start `./setup.sh`. | `dep-da4c6e3bc2fs73fj6630` on `9bf783ce` is `build_failed`. | Current log: `requirements.txt` cannot be opened. | **Hard staging deployment blocker.** |

No service tracks `termux-smoke`. No Render configuration, deployment, suspension, or deletion was requested or performed.

## Verified blockers and ordered follow-up

| Order | Verified blocker | Required evidence before declaring recovery |
|---:|---|---|
| 1 | All three current `master-staging` deployments fail: v3 cannot find `pyproject.toml`; v1/v2 cannot find `requirements.txt`. | Correct root directory or build/start commands in reviewable changes, then successful automatic deployments for the corrected staging SHA. |
| 2 | `termux-smoke` is 411 commits behind staging despite passing current smoke and local repository gate. | A focused reconciliation change, reduced divergence consistent with branch policy, and current gate results on its resulting head. |
| 3 | PRs #92, #48, and #8 are dirty, have failing or incomplete relevant checks, and are absent from staging and production. | Rebase or replace narrowly, with clean state, passing checks, explicit Linear alignment, staging presence, and applicable deployment evidence. |
| 4 | Ten active Linear work items have no assignee or delegate. | Deliberate human-directed triage or explicit valid-specialist delegation; do not infer ownership from candidates. |
| 5 | Exact-head GitHub repository-gate and Termux-smoke runs are absent for `master` and `master-staging`. | A named successful GitHub Actions run, or retain the documented local-worktree evidence as the explicit evidence gap. |

No tracker delegation was applied. No merge, close, retarget, force-push, branch deletion, redeploy, protected-branch change, Render change, credential rotation, or bulk GitHub/Linear update occurred.

## References

[1]: https://github.com/timerloggedout-spec/termux-monorepo/pulls "Current pull-request inventory"
[2]: https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/31895158871 "Exact-head Termux-smoke success"
[3]: https://github.com/timerloggedout-spec/termux-monorepo/commit/0c70299529ecf3e2da0573103f856319e20fa4f4 "Current master commit"
[4]: https://github.com/timerloggedout-spec/termux-monorepo/commit/9bf783ce411f32cdf328195207cd7af1f6c48eda "Current master-staging commit"
[5]: https://github.com/timerloggedout-spec/termux-monorepo/commit/d5116612803ab8207f7aa37902a383e269f57926 "Current termux-smoke commit"
[6]: https://dashboard.render.com/web/srv-d9pq9pajnfac73a73sh0 "Production Render service"
[7]: https://dashboard.render.com/web/srv-d9pphvdbedkc73e2im00 "Staging Render service v3"
[8]: https://github.com/timerloggedout-spec/termux-monorepo/issues/50 "Controlled-spine recovery issue"
[9]: https://github.com/timerloggedout-spec/termux-monorepo/issues/268 "Actions hygiene issue"
[10]: https://github.com/timerloggedout-spec/termux-monorepo/issues/175 "Operator priority matrix"
[11]: https://github.com/timerloggedout-spec/termux-monorepo/issues/192 "Actions refinements proposal"
[12]: https://github.com/timerloggedout-spec/termux-monorepo/pull/92 "Open security PR"
[13]: https://linear.app/termux-monorepo-linear/issue/TER-120/prompt-injection-in-github-workflows-action "TER-120 explicit PR #92 attachment"
[14]: https://linear.app/termux-monorepo-linear/issue/TER-11/integrate-codex-termux-fork-as-submodule-deepcli-bridge-native-codex "TER-11 explicit PR #8 attachment"
[15]: https://linear.app/termux-monorepo-linear/issue/TER-71/ter-llm-api-hub-adekai9000-split-ter-41 "TER-71 explicit PR #48 attachment"
[16]: https://github.com/timerloggedout-spec/termux-monorepo/pull/34 "Open PR targeting termux-smoke"
[17]: https://github.com/timerloggedout-spec/termux-monorepo/pull/7 "Open PR targeting master-staging"
[18]: https://github.com/timerloggedout-spec/termux-monorepo/pull/6 "Open PR targeting master-staging"
[19]: https://github.com/timerloggedout-spec/termux-monorepo/pull/69 "Open feature-targeting PR"
[20]: https://github.com/timerloggedout-spec/termux-monorepo/pull/143 "Native close of issue #117"
[21]: https://github.com/timerloggedout-spec/termux-monorepo/pull/137 "Native close of issue #109"
[22]: https://github.com/timerloggedout-spec/termux-monorepo/pull/131 "Native close of issue #129"
[23]: https://github.com/timerloggedout-spec/termux-monorepo/pull/125 "Native close of issue #124"
[24]: https://dashboard.render.com/web/srv-d9pph1qjobas73etpmrg "Staging Render service v2"
[25]: https://dashboard.render.com/web/srv-d9oeqmvqj5pc738ke09g "Staging Render service v1"
