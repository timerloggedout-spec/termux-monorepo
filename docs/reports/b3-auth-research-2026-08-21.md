# B3 Authentication Research — 2026-08-21

## Sources reviewed

| Source | Finding relevant to B3 |
|---|---|
| [GitHub Docs: Creating GitHub Agentic Workflows](https://docs.github.com/en/copilot/how-tos/github-agentic-workflows/creating-github-agentic-workflows) | For an organization-owned repository using GitHub Copilot, the recommended built-in token mode requires `copilot-requests: write` in workflow frontmatter. Organization policy must allow Copilot CLI usage billed to the organization. |
| [GitHub Agentic Workflows: Authentication](https://github.github.com/gh-aw/reference/auth/) | `copilot-requests: write` uses the built-in GitHub Actions token and does not require a PAT or repository secret. If organization Copilot access is unavailable, inference fails and a separately configured `COPILOT_GITHUB_TOKEN` is the documented alternative. |

## Observed B3 evidence

The controlled manual run [32528017565](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/32528017565) failed secret verification before agent execution because the B3 source workflow declared only `contents`, `issues`, and `pull-requests` read permissions. It produced no agent output and the generated conclusion path created [Issue #299](https://github.com/timerloggedout-spec/termux-monorepo/issues/299), a workflow-failure artifact.

## Boundaries for remediation

The smallest documented runtime fix is adding `copilot-requests: write` to B3 frontmatter while preserving the existing GitHub read-tool scope, credit caps, safe-output schema, and prohibition on shell, browser, network, MCP, and write-capable GitHub tools. This is a scoped inference permission, not repository-content or issue-write authority. It must be paired with `report-failure-as-issue: false` so expected credential or organization-policy failures remain workflow evidence rather than automatically creating extra failure issues outside the B3 report safe-output contract.

If the organization has not enabled the documented Copilot policy, the workflow should remain a controlled failed-evidence state rather than adding a personal token or widening secrets usage. No repository secret is proposed.

## References

[1]: [GitHub Docs: Creating GitHub Agentic Workflows](https://docs.github.com/en/copilot/how-tos/github-agentic-workflows/creating-github-agentic-workflows)
[2]: [GitHub Agentic Workflows: Authentication](https://github.github.com/gh-aw/reference/auth/)
[3]: [B3 controlled runtime run](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/32528017565)
[4]: [B3 failure artifact](https://github.com/timerloggedout-spec/termux-monorepo/issues/299)
