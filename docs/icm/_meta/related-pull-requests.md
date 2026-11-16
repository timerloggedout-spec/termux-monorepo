# ICM-Related Pull Requests

This record reconciles GitHub-native searches for `ICM` and `Interpreted` across open, closed, and merged pull-request states. A textual match is **not** automatically an ICM implementation. The classification below separates direct ICM delivery from historical reconnaissance, pending adjacent workspaces, and broader metadata recovery.

| PR | State | Relationship | Decision |
|---|---|---|---|
| [#4](https://github.com/timerloggedout-spec/termux-monorepo/pull/4) | Merged | **Precursor.** It added reconnaissance and root navigation analysis, identified the misspelled `Interpreted-Context-Methdology_fork` as an uncategorized `refTemplates` item, and proposed metadata-only nesting under `07_Prompt_Context`. | Preserve as historical navigation intent. It did not add a Gitlink or full-methodology integration. The current `smods` Gitlink implements the reference dependency without copying its contents. |
| [#47](https://github.com/timerloggedout-spec/termux-monorepo/pull/47) | Open | **Adjacent recovery.** It proposes a large metadata-only `refTemplates` skeleton and its snapshot shows prior `07_Prompt_Context/Interpreted-Context-Methdology*` checkouts. | Do not merge it into the ICM change merely to recover a historical snapshot. If it is promoted later, add a metadata pointer to the current Gitlink instead of restoring a second checkout. |
| [#103](https://github.com/timerloggedout-spec/termux-monorepo/pull/103) | Open | **Pending adjacent workspace.** Its CAVEMAN compression workspace links layered context loading and plain-text handoffs to the prior methodology fork. | Treat as `ghost`/pending, not as a live ICM source, until its broader independent PR is resolved. Do not duplicate or absorb its 15-file scope. |
| [#232](https://github.com/timerloggedout-spec/termux-monorepo/pull/232) | Merged 2026-08-18 | **Direct implementation.** It contains the ICM Architect System map, maintenance Pipeline, full-methodology companion submodule, and workspace-artifact triage. | Landed on `master` 2026-08-18. Preserve as the historical delivery record for the ICM map and maintenance pipeline; currency of the landed map is maintained through the ICM maintenance factory, not this PR. |

## Search interpretation

The GitHub search result for `ICM` returns #4, #103, and #232. The broader `Interpreted` search also returns #47 plus PRs whose match occurs in an old snapshot, an incidental body reference, or wider historical context. PR #485 is recorded separately as an adjacent merged delivery. These should not be treated as duplicate implementation branches.

Live status recheck on 2026-11-02: #47 and #103 remain open and not mergeable; #232 is merged (2026-08-18); #485 is merged (2026-09-19).

> **Canonical decision:** the current custom reference Gitlinks remain at `refTemplates/smods/`. PR #4 and #47 supply historical metadata-placement context; PR #103 supplies a pending CAVEMAN-workspace relationship. No content is copied from, merged with, or assumed from any of those PRs.

## Master path

PR #232 merged 2026-08-18; the direct ICM delivery path has landed on `master`. Map currency is now maintained through the ICM maintenance factory (`docs/icm/maintenance/`). Do not reopen #4, force-merge #103, or bulk-merge #47 as a substitute for scoped maintenance runs.
