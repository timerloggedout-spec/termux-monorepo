# Context7 + Mintlify integration reconnaissance

**Status:** Evidence-backed historical and operational reference  
**Scope:** Git history, repository configuration, documentation publication surfaces  
**Last verified:** 2026-10-23  
**Repository:** `timerloggedout-spec/termux-monorepo`

## Executive finding

Context7 and Mintlify were not newly introduced together from scratch. Mintlify configuration, navigation, operator guidance, and interactive diagram documentation were merged earlier. Context7 was already present in the repo-local Codex MCP baseline. PR [#1613](https://github.com/timerloggedout-spec/termux-monorepo/pull/1613) subsequently consolidated the two tools into an explicit operating contract and was merged on 2026-10-24 UTC.

The integration has distinct responsibilities:

- **Context7:** version-aware library/framework research.
- **Mintlify MCP:** deployment-scoped documentation inspection/editing and deployment visibility, only where the connected account exposes those capabilities.
- **Git-tracked Markdown/MDX and `docs.json`:** reviewable publication inputs.
- **GitHub PR/CI:** change review and engineering gates.
- **Mintlify deployment status and public agent exports:** publication/discoverability evidence, not substitutes for code correctness.

## Verified history

| Change | Verified result | Why it matters |
|---|---|---|
| [PR #323](https://github.com/timerloggedout-spec/termux-monorepo/pull/323) / [merge commit `cf9b9c9`](https://github.com/timerloggedout-spec/termux-monorepo/commit/cf9b9c92caa9475ab5fc461352d904e242fc64a7) | Merged 2026-08-23; added root `docs.json` and initial Mintlify metadata/navigation. | Establishes Git-tracked Mintlify configuration. |
| [PR #326](https://github.com/timerloggedout-spec/termux-monorepo/pull/326) / [merge commit `4520c2c`](https://github.com/timerloggedout-spec/termux-monorepo/commit/4520c2c179820221eb5a282374cd43173cd5c211) | Merged 2026-08-23; added the Notation Sets proposal page and navigation. | Demonstrates navigation updates must accompany intended public pages. |
| [PR #327](https://github.com/timerloggedout-spec/termux-monorepo/pull/327) / [merge commit `46766a7`](https://github.com/timerloggedout-spec/termux-monorepo/commit/46766a7157528bf0afa3170ebda1031219dd76af) | Merged 2026-08-23; completed sidebar navigation and added Mintlify operator guidance. | Establishes the deployment and operator runbook. |
| [PR #508](https://github.com/timerloggedout-spec/termux-monorepo/pull/508) / [merge commit `d9e7e63`](https://github.com/timerloggedout-spec/termux-monorepo/commit/d9e7e634dbd9373936c6dc8d15ea45372096256e) | Merged 2026-09-14; added a Mintlify page embedding the Mermaid sources and a Diagrams navigation group. | Extends docs into an interactive architecture surface while retaining source links. |
| [Repo Codex MCP config](../../.codex/config.toml) | The tracked configuration contains `[mcp_servers.context7]` using `npx -y @upstash/context7-mcp@latest`. | Context7 was configured before the combined operating-contract PR. |
| [PR #1613](https://github.com/timerloggedout-spec/termux-monorepo/pull/1613) / [merge commit `2018404`](https://github.com/timerloggedout-spec/termux-monorepo/commit/20184043bfd1fcd0f0df6267c7cf004f85029fd5) | Merged 2026-10-24 UTC; added `docs/ops/CONTEXT7-MINTLIFY-INTEGRATION.md`, updated `.codex/AGENTS.md`, refreshed `docs/ops/MINTLIFY.md`, and updated the agent roster. | Makes research, operator editing, provenance, discoverability, and publication-state rules explicit. |

Commit search and code search are different indexes and have different limits. The above is a verified milestone list, not a claim that every mention of either product has been enumerated.

## Current repository contract

The merged operating guide is [`CONTEXT7-MINTLIFY-INTEGRATION.md`](CONTEXT7-MINTLIFY-INTEGRATION.md). The Mintlify operator runbook is [`MINTLIFY.md`](MINTLIFY.md). Together they require:

1. Resolve a library to a Context7 ID before querying unless a valid ID is already supplied.
2. Prefer official sources and the repo-pinned version; record material version/uncertainty.
3. Treat retrieved snippets as evidence to adapt, not as proof that repository code is correct.
4. Inspect deployment, branch, page path, and permissions before using Mintlify MCP to mutate content.
5. Keep Git-tracked MDX and `docs.json` as the reviewable publication inputs.
6. Verify navigation, links, CI, preview, and production deployment independently.
7. Never infer production publication from an editor save, PR, preview, or queued deployment.
8. Keep secrets and private connector configuration out of the repository.

## Agent discoverability

Mintlify documents `markdown.instructions` as a `docs.json` setting that appends site-wide instructions to Markdown exports, `llms.txt`, and `llms-full.txt`. This branch proposes a short, project-specific instruction set that tells agents to ground claims in repository evidence, distinguish proposed/merged/deployed states, version technical guidance, and protect secrets.

These are separate surfaces and need separate checks:

- `docs.json`: configured navigation and site metadata.
- `/llms.txt`: generated index and descriptions.
- `/llms-full.txt` and `/.well-known/llms-full.txt`: generated full-context exports, if available.
- Hosted `/mcp`: public docs-search surface, if enabled.
- Mintlify remote MCP: authenticated operator surface, subject to connector permissions.
- Mintlify deployment status: confirms whether a particular commit is live.

Do not claim these endpoints are available just because the config contains the relevant feature or the operator MCP is connected.

## Remaining verification checklist

- [ ] Confirm the PR's required repository checks on the actual merge commit; do not treat third-party review bots as the only CI evidence.
- [ ] Validate `docs.json` with the current Mintlify CLI/schema and verify every navigation path exists.
- [ ] Inspect the actual deployed `/llms.txt` and `/llms-full.txt` output for the expected instruction block and correct public content.
- [ ] Check the hosted `/mcp` endpoint only if enabled and documented for the deployment.
- [ ] Record a deployment as live only after Mintlify reports the corresponding commit as live.
- [ ] Recheck whether repo-local agents can launch the configured Context7 MCP in their actual runtime; tracked config alone does not prove runtime availability.

## Sources

- [Mintlify operator guide](MINTLIFY.md)
- [Context7 + Mintlify operating contract](CONTEXT7-MINTLIFY-INTEGRATION.md)
- [Mintlify Markdown export documentation](https://mintlify.com/docs/ai/markdown-export)
- [Context7 repository](https://github.com/upstash/context7)
- Historical PRs and merge commits linked in the timeline above.
