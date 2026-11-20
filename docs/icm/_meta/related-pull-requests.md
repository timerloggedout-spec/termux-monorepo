# ICM-Related Pull Requests

This record reconciles GitHub-native searches for `ICM` and `Interpreted` across open, closed, and merged pull-request states. A textual match is **not** automatically an ICM implementation. The classification below separates direct ICM delivery from historical reconnaissance, pending adjacent workspaces, and broader metadata recovery.

| PR | State | Relationship | Decision |
|---|---|---|---|
| [#4](https://github.com/timerloggedout-spec/termux-monorepo/pull/4) | Merged | **Precursor.** It added reconnaissance and root navigation analysis, identified the misspelled `Interpreted-Context-Methdology_fork` as an uncategorized `refTemplates` item, and proposed metadata-only nesting under `07_Prompt_Context`. | Preserve as historical navigation intent. It did not add a Gitlink or full-methodology integration. The current `smods` Gitlink implements the reference dependency without copying its contents. |
| [#47](https://github.com/timerloggedout-spec/termux-monorepo/pull/47) | Open, mergeable/unstable | **Adjacent recovery.** It proposes a large metadata-only `refTemplates` skeleton and its snapshot shows prior `07_Prompt_Context/Interpreted-Context-Methdology*` checkouts. | Do not merge it into the ICM change merely to recover a historical snapshot. If it is promoted later, add a metadata pointer to the current Gitlink instead of restoring a second checkout. |
| [#103](https://github.com/timerloggedout-spec/termux-monorepo/pull/103) | Open, conflicting/dirty | **Pending adjacent workspace.** Its CAVEMAN compression workspace links layered context loading and plain-text handoffs to the prior methodology fork. | Treat as `ghost`/pending, not as a live ICM source, until its broader independent PR is resolved. Do not duplicate or absorb its 15-file scope. |
| [#232](https://github.com/timerloggedout-spec/termux-monorepo/pull/232) | Open, conflicting/dirty | **Direct implementation.** It contains the ICM Architect System map, maintenance Pipeline, full-methodology companion submodule, and workspace-artifact triage. | Preserve as the current P0 review surface. Repair/except baseline gates and reconcile the branch path before promotion. |

## Search interpretation

The GitHub search result for `ICM` returns #4, #103, and #232. The broader `Interpreted` search also returns #47 plus PRs whose match occurs in an old snapshot, an incidental body reference, or wider historical context. They should not be treated as duplicate implementation branches.

> **Canonical decision:** the current custom reference Gitlinks remain at `refTemplates/smods/`. PR #4 and #47 supply historical metadata-placement context; PR #103 supplies a pending CAVEMAN-workspace relationship. No content is copied from, merged with, or assumed from any of those PRs.

## Master path

Keep review capacity focused on one direct ICM delivery path. Validate PR #232’s ICM changes through `master-staging`, resolve or formally except the repository gate failures, then conduct the separate `master`/`master-staging` reconciliation under its own scoped review. Do not reopen #4, force-merge #103, or bulk-merge #47 as a substitute for that path.
