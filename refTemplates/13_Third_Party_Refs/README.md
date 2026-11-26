# 13_Third_Party_Refs

Metadata-first registry of third-party tools, protocols, and reusable engineering patterns. These references are discovery inputs, not automatic dependencies.

## Current research intake

| Reference | Primary role | Disposition |
|---|---|---|
| [Alibaba Open Code Review](open-source-radar-2026-11-15/README.md#alibaba-open-code-review) | Deterministic + agent-assisted code review | Research only |
| [Chrome DevTools MCP](open-source-radar-2026-11-15/README.md#chrome-devtools-mcp) | Browser inspection, debugging, performance evidence | Research only |
| [AG-UI](open-source-radar-2026-11-15/README.md#ag-ui) | Agent ↔ user application event protocol | Research only |
| [Univer](open-source-radar-2026-11-15/README.md#univer-office-sdk) | Office SDK and headless document processing | Research only |

Discovery notes and primary sources: open-source-radar-2026-11-15/.

## Intake and sMods policy

Upstream references are not automatic dependencies. A package/API integration without local source changes does not need a submodule. Create a custom fork only when repository-owned modifications or a maintained adaptation are justified.

The companion smods-disposition.json records the current research-only state and the required promotion path. When a project is actually selected for repository integration, update the canonical refTemplates/smods/INTEGRATIONS.json registry. A fork-required record is not a gitlink; promote to pinned only after the actual fork, license review, immutable SHA, exact .gitmodules URL, 160000 gitlink, and dual-gate evidence are verified.

Recheck volatile versions, stars, compatibility, pricing, and commercial scope at implementation time.
