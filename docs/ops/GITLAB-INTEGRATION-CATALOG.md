# GitLab Integration Catalog

**Implements: AR-33.** This is a declarative, repository-local registry—not a setup directive or a record of installed, enabled, authenticated, or connected services. Machine-readable entries live in [`gitlab-integration-catalog.json`](gitlab-integration-catalog.json). No secrets, tokens, credentials, or account-specific identifiers belong here.

## GitLab integration candidates

| Candidate | Purpose | Catalog state | Important boundary |
|---|---|---|---|
| [GitLab MCP server](https://docs.gitlab.com/user/model_context_protocol/mcp_server/) | MCP tools against GitLab | `requires_auth_approval`; not enabled | GitLab.com endpoint: `https://gitlab.com/api/v4/mcp`. OAuth access token must carry `mcp` scope. Legacy personal access tokens, project access tokens, and group access tokens are rejected; do not configure a legacy PAT as MCP auth. OAuth authorization and organizational/account approval are required. |
| [GitLab CLI (`glab`)](https://docs.gitlab.com/cli/) | GitLab issues, merge requests, pipelines, releases and other CLI functions | `requires_auth_approval`; not enabled | Official CLI; supports OAuth and personal access token authentication. Any credential setup requires explicit approval and secure local handling. |
| [GitLab Duo CLI (`duo`)](https://docs.gitlab.com/user/gitlab_duo_cli/) | GitLab Duo Agent Platform from terminal | `requires_entitlement_auth_approval`; not enabled; account entitlement **unknown** | GitLab documents Premium/Ultimate tier and GitLab.com, Self-Managed, and Dedicated offerings. Eligibility, seat/feature access, account entitlement, and cost for this environment have not been verified. Do not infer entitlement or quota. |

A catalog state of `enabled: false` is intentional; this document does not assert that any candidate is installed, enabled, authenticated, connected, or available to this account. Approval/authentication requirements are not satisfied merely by listing an entry. Catalog declarations are not environment-state observations.

## Existing repository authority

The canonical workflow contract is [`GITHUB-GITLAB-GOVERNED-RECONCILIATION.md`](GITHUB-GITLAB-GOVERNED-RECONCILIATION.md). GitHub `master` is the canonical promotion spine; the governed workflow compares GitHub `master` with a selected GitLab branch. Aligned or GitLab-behind states are no-ops; GitLab-ahead or diverged states may produce an ordinary merge on a review branch and a PR against `master`. Conflicts stop. The workflow never writes to GitLab, force-pushes, or auto-merges. A successful run is not sufficient evidence by itself; inspect its source-pair summary and any review PR. Review and promotion remain separate decisions. This catalog does not change reconciliation behavior or authority and does not authorize GitLab writes, mirroring, merge, deployment, schedules, or production changes.

## Existing quota-provider complement surfaces

OpenRouter and Google AI Studio/Gemini are already represented by repository provider surfaces; they are **not new service candidates**. They are listed as existing complements for completeness, not as recommendations, configured providers, or enabled integrations. The catalog makes no claims about actual account limits, eligibility, pricing, or available quota; those remain unknown until independently verified. This catalog does not introduce a provider adapter or routing path.

### Additional capacity options

Cerebras and Cloudflare Workers AI are listed separately as **existing documented candidates without verified accounts**, not as new integrations. Both remain disabled and require account verification and budget approval; actual remaining quota is unknown (`null`) and cost status is `cost_unknown`. Official published limits below are descriptive policy references, not evidence of this account's actual quota. Each provider has an independent budget; do not pool budgets or use either as a quota bypass.

- [Cerebras rate limits](https://inference-docs.cerebras.ai/support/rate-limits): limits are organization/model scoped continuous token buckets with separate uncached-token and total-token limits; account-specific limits appear in Cloud Console Limits. Trial access is time/credit bounded, not a permanently renewing free allowance.
- [Cloudflare Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/): published free allowance is 10,000 neurons/day, resetting at 00:00 UTC; some models are paid-only. This does not establish account access or remaining allowance.

Next steps are **zero-spend validation only**: verify account access, model eligibility and actual limits, seek budget approval, and determine API access requirements. API access is unknown. Do not enable either service, make a purchase or paid enablement, or introduce invocation adapters.

**Budgets are per service and per billing account.** Do not pool quotas or route around a service's cap by switching providers. Apply each service's own limits and billing controls; unknown cost/quota must remain unknown until independently verified. No billing, quota, or account setting is changed by this catalog.

## Sources

- [GitLab MCP server documentation](https://docs.gitlab.com/user/model_context_protocol/mcp_server/) — endpoint, OAuth `mcp` scope, and unsupported legacy token types.
- [GitLab CLI documentation](https://docs.gitlab.com/cli/) — official CLI and supported authentication methods.
- [GitLab Duo CLI documentation](https://docs.gitlab.com/user/gitlab_duo_cli/) — offering/tier and CLI scope.
- [OpenRouter](https://openrouter.ai/) and [Google AI Studio](https://ai.google.dev/) — identity references for existing repository provider surfaces only; no cost or quota claims.

## Offline validation

Run `python3 tests/test_gitlab_integration_catalog.py`. It parses the JSON and checks required fields, disabled/default approval states, MCP endpoint and auth constraints, unknown Duo entitlement/cost, non-pooled budgets, existing provider classification, reconciliation link, and safety language. It performs no network calls and needs no credentials.
