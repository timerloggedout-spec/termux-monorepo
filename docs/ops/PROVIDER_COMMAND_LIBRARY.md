# Provider Command Library

**Status:** Implemented under `AR-11` as a declarative, trusted-default-branch command catalog. The library is located at `.github/agentic/provider-command-library.json`; `Provider command dispatch` is the only workflow that executes its entries.

## Purpose

The repository has multiple agent providers with different, evolving pull-request capabilities. Rather than adding ad hoc polling logic or a hard-coded command map to each workflow, the command library records each provider’s known commands, effects, trusted comment authors, and optional interactive-control labels in one reviewable file. The dispatcher accepts only an allowlisted provider/action tuple, reads the library from the repository default branch, verifies the live PR head SHA, and records an attributable receipt.

> A dispatch receipt confirms that the OPERATOR lane made an authorized request. It does **not** claim that the provider has completed a review, generated a fix, or passed validation.

## Command families

| Provider | Supported command family | Delivery behavior | Branch-write confirmation |
|---|---|---|---|
| CodeRabbit | Incremental/full review, AutoFix, Fix CI, merge-conflict resolution | Prefer an exact matching provider checkbox; otherwise post CodeRabbit’s documented command. | Required for AutoFix, Fix CI, stacked PR, and conflict-resolution actions. |
| Qodo | On-demand review | Post the documented `/agentic_review` command. | Not applicable; library has no branch-writing Qodo action. |
| Devin | On-demand review; separately configured Auto-Fix capability | Post the documented `/devin review` command. Auto-Fix requires the organization’s trusted-bot/Auto-Fix configuration. | Not applicable to the available command entry; provider configuration remains external. |

The source evidence and provider prerequisites are recorded in [Provider Command Library — External Evidence](PROVIDER_COMMAND_LIBRARY_EVIDENCE.md).

## Dispatch contract

A dispatch requires the following inputs:

| Input | Rule |
|---|---|
| `pr_number` | Must identify an open pull request. |
| `provider`, `action` | Must be present in both `OPERATOR_COMMAND_ACTIONS` and the trusted command library. |
| `head_sha` | Must equal the PR’s current head SHA; stale requests fail closed. |
| `confirm_branch_write` | Must be `true` for any library action with `requires_confirm_branch_write: true`. |

The dispatcher searches only trusted provider-authored issue comments for an exact unchecked control whose label appears in that action’s library entry. If a control is found, it patches that comment through GitHub’s documented issue-comment update endpoint. If the patch is unavailable or rejected, the dispatcher posts the documented provider command instead. It never invents commands, mutates an undeclared control, edits a non-provider comment, or processes a library from the PR branch.

## Idempotency and evidence

Every execution writes `<!-- operator-provider-command:v1 -->` metadata with the requested provider, action, head SHA, effect, execution route, and control/source identifiers. A matching prior OPERATOR receipt makes a retry a no-op. This prevents duplicate commands during event delivery retries without relying on interval polling or diff scans.

## Configuration

`OPERATOR_COMMAND_ACTIONS` is the runtime allowlist. Its default contains only the command tuples present in the initial library. Removing a tuple disables it even when the command remains documented. Adding a new provider command requires a library update, a focused test, documented capability evidence, and review.

`OPERATOR_EXECUTOR_LOGINS` identifies the token identities that are allowed to create idempotency receipts. The established token priority remains `ARCHWIZ_GITHUB_TOKEN`, then `OPERATOR_GITHUB_TOKEN`, then `OPERATOR_TOKEN`, then the repository workflow token as a least-capable fallback.

## Provider completion boundary

The dispatcher has no merge authority and never bypasses branch protection. Provider output must be verified by the relevant review, check, or workflow before a peer gate treats the action as complete. For example, CodeRabbit AutoFix may commit to the PR branch or create a stacked PR; the resulting revision still has to pass normal review and validation.

## References

[1]: https://docs.coderabbit.ai/reference/review-commands "CodeRabbit code review command reference"
[2]: https://docs.coderabbit.ai/finishing-touches/autofix "CodeRabbit Autofix"
[3]: https://docs.qodo.ai/code-review/use-qodo-in-prs/code-review "Qodo: How to run a code review"
[4]: https://docs.devin.ai/work-with-devin/devin-review "Devin Review"
[5]: https://docs.github.com/rest/issues/comments "GitHub REST API: issue comments"
