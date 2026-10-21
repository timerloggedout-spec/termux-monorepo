# Source and Relationship Evidence — Issue #192

## Collection Bounds

This record is metadata-only. GitHub issue, comment, review, and timeline bodies were read only to identify explicit references and were not copied here. Collection was limited to the exact Issue #192 root, its GitHub-native timeline references, the directly cross-referenced Issue #175 and PR #193, the implementation/promotion references PR #261, PR #266, PR #267, and PR #269, Issue #268, and a bounded review of the current `master` status context.

## Verified Relationships

| From | Relationship | To | Evidence |
|---|---|---|---|
| Issue #192 | Native GitHub `cross-referenced` event | PR #193 | [Issue #192 timeline](https://github.com/timerloggedout-spec/termux-monorepo/issues/192) and [PR #193](https://github.com/timerloggedout-spec/termux-monorepo/pull/193). |
| Issue #192 | Native GitHub `cross-referenced` event | Issue #175 | [Issue #192 timeline](https://github.com/timerloggedout-spec/termux-monorepo/issues/192) and [Issue #175](https://github.com/timerloggedout-spec/termux-monorepo/issues/175). |
| PR #193 | Implements/refines action and connector surface | `.github/connectors/integrations.yaml`, `.github/workflows/commit-diff-watcher.yml`, `http-llm-invoke` composite action | [PR #193 files](https://github.com/timerloggedout-spec/termux-monorepo/pull/193/files). PR is merged and therefore cannot be extended. |
| Issue #175 | Names PR #81 as a quota-gate workflow concern | PR #81 | [Issue #175](https://github.com/timerloggedout-spec/termux-monorepo/issues/175) and [PR #81](https://github.com/timerloggedout-spec/termux-monorepo/pull/81). |
| Issue #192 | Native GitHub `cross-referenced` event | PRs #261, #266, #267, and #269; Issue #268 | [Issue #192 timeline](https://github.com/timerloggedout-spec/termux-monorepo/issues/192), [PR #261](https://github.com/timerloggedout-spec/termux-monorepo/pull/261), [PR #266](https://github.com/timerloggedout-spec/termux-monorepo/pull/266), [PR #267](https://github.com/timerloggedout-spec/termux-monorepo/pull/267), [PR #269](https://github.com/timerloggedout-spec/termux-monorepo/pull/269), and [Issue #268](https://github.com/timerloggedout-spec/termux-monorepo/issues/268). |
| Active `rate-limit-rotation` proposal | Lists PRs #72 and #81 | PR #72, PR #81 | `docs/proposals/active/rate-limit-rotation/MANIFEST.md`; `ITEMS.md` entries RL-06 and RL-10. |
| Active ICM proposal | Documents branch #232 as its implementation path | PR #232 | `docs/proposals/registry.yaml`; `docs/proposals/active/icm-architect-integration/ITEMS.md`; [PR #232](https://github.com/timerloggedout-spec/termux-monorepo/pull/232). |

## Candidate Links Requiring Human Review

| Candidate | Why it was considered | Why it is not implementation authority |
|---|---|---|
| PR #81 | Workflow-only quota-gate scope and direct mention in Issue #175. | It targets `master`, is currently conflicting, and has changes requested. |
| PR #92 | Workflow-security hardening and action SHA pinning. | It targets `master`; it is not an accepted carrier for functional workflow additions. |
| PR #143 | GitHub Actions coordination scope. | It targets `master`, is conflicting, and is scoped to MCP Agent Mail. |
| PR #72 | Active rate-limit and workflow branch. | It is broad, conflicting, and has its own P0 proposal scope. |

## Existing Capability Inventory

| Capability | Existing repository mechanism | Intake conclusion |
|---|---|---|
| Checkout | `actions/checkout` in multiple workflows | Reuse; standardize only in an accepted pinning/security item. |
| Cache | `actions/cache`, including restore/save variants and local composite actions | Do not add a second cache layer without an ownership and key-compatibility review. |
| Artifact upload | `actions/upload-artifact` in `deepseek-ci.yml` | Reuse only for bounded non-secret hand-offs. |
| Artifact download | No direct repository usage was found in the bounded scan. | Candidate for AR-03 where a downstream job actually needs a retained immutable file. |
| Workflow dispatch/status/comments | `actions/github-script` plus existing dispatcher workflows | Prefer existing native API capability before marketplace wrappers. |
| Changed-file filtering | Existing scripted inventory logic in `gemini-dispatch.yml` | Evaluate one filter solution; do not add overlapping third-party actions. |
| Issue-to-PR automation | Repository workflow token has write defaults; CodeRabbit lacks workflow-file write permission. | Separate AR-04 design item; workflow edits remain operator-owned. |

## Baseline Findings

The required integration baseline is `master-staging`. The collected revision contains unresolved conflict markers in `scripts/ci/repo_gate.py`, `.github/workflows/gemini-dispatch.yml`, and `.github/workflows/gemini-review.yml`; the gate script cannot compile, so both required validation commands currently fail before evaluating this documentation-only branch. Additional markers are present in a small number of Markdown and auxiliary files and must be classified separately rather than resolved opportunistically. The dispatch conflict concerns the `issue_number` input passed to the reusable invoke workflow. The invoke workflow declares that input; however, the review workflow’s conflict region leaves its reusable interface structurally incomplete. This is a prerequisite validity problem, not a safe reason to expand workflow scope.

The proposal-lifecycle check on the intake branch also fails before evaluating this proposal because the inherited `docs/proposals/active/manus-critical-eval` directory is not registered in `docs/proposals/registry.yaml`. That orphan is outside the scope of this proposal; it is recorded here so a reviewer can distinguish it from the newly registered `actions-refinements` directory.

The repository-local context-relationship index exists at `workspace/llm_map/context_relationships`, but its manifest was last collected on 2026-08-19, has incomplete pagination, and still identifies `master-staging` as the default branch. Bounded `issue:175` and `issue:192` queries were therefore used only as historical discovery aids. Direct live GitHub timeline collection is the controlling evidence for the Issue #175 relationship and post-promotion links recorded above. No synthetic graph was generated, rebuilt, or manually edited. The PR candidacies remain intentionally separate and non-authoritative.

## External Baseline

GitHub’s artifact guidance documents `upload-artifact` and `download-artifact` for dependent jobs and states that artifacts are immutable in v4, requiring distinct artifact names for successive outputs. This supports the AR-03 bounded hand-off rule, but it does not justify a general artifact addition. [GitHub Docs: Store and share data](https://docs.github.com/en/actions/tutorials/store-and-share-data#passing-data-between-jobs-in-a-workflow)

## AR-01 Repair Evidence — 2026-08-19

The current `master-staging` surface was rechecked before implementation. Syntax-affecting markers remained in `.github/workflows/gemini-dispatch.yml` and `.github/workflows/gemini-review.yml`; `scripts/ci/repo_gate.py` no longer contained a marker and was left unchanged. The dispatcher was structurally malformed above the remaining marker, so AR-01 restored both affected workflows from `a618774^2`, the conflict-free second parent of the repository’s `a618774` infrastructure-stabilization merge. That source preserved the complete reusable-workflow interfaces, explicit top-level `permissions: {}`, declared `issue_number`/`pr_number` handoffs, and the immutable `actions/github-script` SHA.

The repair branch contains no conflict markers in the AR-01 surface. `python3 scripts/ci/repo_gate.py --base origin/master-staging` and `python3 scripts/ci/termux_smoke.py` passed. The proposal registry validator remains blocked by the pre-existing unregistered `docs/proposals/active/manus-critical-eval` directory; no unrelated proposal repair was made.

The implementation branch `fix/ar01-automation-baseline` was pushed. GitHub temporarily rejected pull-request creation first through GraphQL as submitted too quickly and then through REST with a secondary content-creation limit at `2026-08-19 05:18:39 UTC` (request ID `A1BA:3AC918:2402CE4:76F458A:6A853CAF`). No pull request was created in that rate-limited interval.
