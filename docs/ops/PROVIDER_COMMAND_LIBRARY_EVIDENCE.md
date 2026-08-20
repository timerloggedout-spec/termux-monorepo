# Provider Command Library — External Evidence

**Collection date:** 2026-08-20. This record captures provider and GitHub capabilities used to design the command-library lane. It does not contain credentials, browser state, or provider-session data.

| Capability | Verified behavior | Source |
|---|---|---|
| Qodo manual review | Qodo documents `/agentic_review` as a pull-request comment command that requests a review on demand. Its legacy review documentation also documents `/review`. | [Qodo code review][1] [Qodo review tool][2] |
| Qodo automatic review | Qodo can be configured to review pull requests on open/update and to keep review comments synchronized with new commits. | [Qodo trigger a code review][3] [Qodo persistent review comments][4] |
| Devin manual review | Devin documents `/devin review` at the start of a GitHub PR comment as a manual review trigger. The commenter needs write/admin repository access and a GitHub account linked to Devin. | [Devin Review][5] |
| Devin automatic review | Devin Review can trigger on PR open, new commits, and ready-for-review events when configured for repository/user auto-review. | [Devin Review][5] |
| Devin Auto-Fix | Devin Review can push fix commits when Auto-Fix is enabled, using the organization’s pull-request bot-response setting. | [Devin Auto-Fix][6] |
| Devin trusted-bot routing | Devin can respond to comments from an explicit allowlist of trusted bot accounts; Devin recommends adding bots one at a time to prevent loops. | [Devin bot-comment settings][7] |
| CodeRabbit review commands | CodeRabbit documents incremental `@coderabbitai review` and complete `@coderabbitai full review` triggers. | [CodeRabbit command reference][8] |
| CodeRabbit AutoFix | CodeRabbit documents `@coderabbitai autofix` for a direct commit to the current PR branch and `@coderabbitai autofix stacked pr` for a separately reviewable stacked PR. Its GitHub Autofix checkbox offers the same delivery options. | [CodeRabbit AutoFix][9] |
| CodeRabbit Fix CI | CodeRabbit documents `@coderabbitai fix-ci` for a stacked PR and `@coderabbitai fix-ci commit` for a direct PR-branch commit; supported GitHub PRs expose equivalent checkbox choices when CI failures are detected. | [CodeRabbit Fix CI][10] |
| CodeRabbit merge-conflict resolution | CodeRabbit documents `@coderabbitai resolve merge conflict` and a GitHub checkbox for supported conflict flows. | [CodeRabbit Resolve Merge Conflicts][11] |
| GitHub issue-comment update | GitHub documents `PATCH /repos/{owner}/{repo}/issues/comments/{comment_id}`. Fine-grained tokens require Issues or Pull requests write permission. | [GitHub issue comments][12] |
| GitHub review-comment update | GitHub documents `PATCH /repos/{owner}/{repo}/pulls/comments/{comment_id}`. Fine-grained tokens require Pull requests write permission. | [GitHub pull request review comments][13] |

## Design implications

The command library should prefer a provider’s documented command first, because it is explicit, attributable, and provider-supported. A provider control such as a checkbox may be used only through a declared `comment_patch` capability that verifies the exact provider, target comment ID, live SHA/cycle, and expected control payload before an OPERATOR-token patch is attempted. A failed or unsupported patch must fall back to the documented provider command and preserve a non-secret execution result for the current cycle.

[1]: https://docs.qodo.ai/code-review/use-qodo-in-prs/code-review "Qodo: How to run a code review"
[2]: https://docs.qodo.ai/v1/tools/tools-list/review "Qodo review tool"
[3]: https://docs.qodo.ai/code-review/use-qodo-in-prs "Qodo: Trigger a code review"
[4]: https://docs.qodo.ai/code-review/persistent-review-comments "Qodo persistent review comments"
[5]: https://docs.devin.ai/work-with-devin/devin-review "Devin Review"
[6]: https://docs.devin.ai/use-cases/gallery/devin-review-autofix "Devin Review Auto-Fix"
[7]: https://docs.devin.ai/product-guides/bot-comment-settings "Devin bot-comment settings"
[8]: https://docs.coderabbit.ai/reference/review-commands "CodeRabbit code review command reference"
[9]: https://docs.coderabbit.ai/finishing-touches/autofix "CodeRabbit Autofix"
[10]: https://docs.coderabbit.ai/finishing-touches/fix-ci "CodeRabbit Fix CI failures"
[11]: https://docs.coderabbit.ai/finishing-touches/resolve-merge-conflict "CodeRabbit Resolve Merge Conflicts"
[12]: https://docs.github.com/rest/issues/comments "GitHub REST API: issue comments"
[13]: https://docs.github.com/rest/pulls/comments "GitHub REST API: pull request review comments"
