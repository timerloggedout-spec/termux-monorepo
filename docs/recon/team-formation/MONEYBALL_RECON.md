# MoneyBall Implementation Recon

## Executive Finding

The MoneyBall roster design is **not yet a settled mainline implementation**. The live GitHub record for [PR #131](https://github.com/timerloggedout-spec/termux-monorepo/pull/131) shows an open, non-draft pull request with a dirty mergeable state. GitHub’s compare record reports that its head is 94 commits ahead of the PR base and zero commits behind the base; the PR contains five changed files, 627 additions, and 232 deletions. [1] [2]

This conflicts with the current lane SSOT, which states that the #129/#131 stream is merged. The team charter and score model therefore treat #131 as valuable evidence and a likely implementation source, but not as an unquestioned source of current production behavior. ATF-03 is the required reconciliation item.

## Live PR Evidence

| Field | Captured value | Planning consequence |
|---|---|---|
| Pull request | #131, `feat(multi-agent): implement MoneyBall agent roster & betting arena`. | Primary implementation evidence for roster, role, point, and mutation concepts. |
| State | Open; non-draft; `mergeable_state=dirty`. | Do not represent the change as merged or build dependent work on an assumed clean merge. |
| Base | `master` at `a4d84da2602d` when PR metadata was captured. | Compare against the PR’s recorded base and current default branch separately. |
| Head | `jules-5118449608716874585-f16551c8` at `848056f7e7d3`. | Preserve the commit reference in any code-level analysis or future extraction. |
| Compare | 94 commits ahead, 0 behind, with that base. | The branch contains a substantial, unmerged implementation history. |
| Surface | Five files; 627 additions and 232 deletions. | Require file-by-file review before reuse or refactoring. |
| Checks | Vercel and Vercel Preview Comments succeeded; Peer review orchestrator and GitLab pipeline failed in the captured state. | A clean planning document does not clear the implementation branch’s failed checks. |

## Verified Discrepancies

| Record | Statement | Live evidence | Required disposition |
|---|---|---|---|
| Lane Consolidation SSOT | Identifies #129/#131 as merged work in the multi-agent lane. | GitHub reports #131 open and dirty. | Update the SSOT or document which specific commits are authoritative. |
| Integration policy | `AGENTS.md` requires `master-staging` for integration. | The inspected remote exposed `master`; no `master-staging` reference was present. | ATF-09 must restore or replace the branch policy before presenting implementation work as integration-ready. |
| Required gates | `AGENTS.md` lists `repo_gate.py` and `termux_smoke.py`. | `scripts/ci/repo_gate.py` exists on the inspected branch; no `termux_smoke.py` was found. | ATF-10 must restore or replace the smoke-gate invocation and record a passing run. |

## Consequences for Team Formation

The current work can safely define the role taxonomy, additive registry, player-machine fleet, target register, and score-event contracts. It must not silently rewrite the MoneyBall implementation, assume that global ELO/3L0 is authoritative, or automate cull/clone/routing actions until PR #131’s actual implementation and the branch/gate policies are reconciled.

The recommended sequence is to preserve #131 as a comparison source, extract a file-level behavior map, agree on the target integration branch, then create a small separate change that introduces a versioned score-event schema without changing existing routing. The game-player and wallet research records can be designed in parallel because they define data contracts, not an immediate mutation of the roster.

## Evidence Needed to Close ATF-03, ATF-09, and ATF-10

| Item | Closing evidence |
|---|---|
| ATF-03 — MoneyBall reconciliation | Named authoritative commit(s), selected behavior to retain/replace, a corrected SSOT statement, and a recorded Operator disposition. |
| ATF-09 — Integration base | Restored `master-staging` reference or an approved replacement branch policy reflected in the repository instructions. |
| ATF-10 — Smoke gate | Restored/replaced command, documentation update, and successful validation output attached to the relevant change. |

## References

[1] [PR #131 — MoneyBall agent roster & betting arena](https://github.com/timerloggedout-spec/termux-monorepo/pull/131)

[2] [PR #131 GitHub compare evidence](https://github.com/timerloggedout-spec/termux-monorepo/compare/a4d84da2602d...848056f7e7d3)

[3] [Lane Consolidation SSOT](../../ops/LANE_CONSOLIDATION_SSOT.md)

[4] [Repository agent instructions](../../../AGENTS.md)

[5] [ATF item backlog](../../proposals/active/agent-team-formation/ITEMS.md)
