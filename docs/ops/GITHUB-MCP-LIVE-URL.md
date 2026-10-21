# GitHub MCP — LIVE URL (SSOT)

**No desktop. No local process. No npx. No Docker on the phone.**

## Live endpoint (GitHub-hosted)

```text
https://api.githubcopilot.com/mcp/
```

| Fact | Value |
|------|--------|
| Operator | GitHub (not this monorepo, not Vercel mcp-hub) |
| Transport | Streamable HTTP |
| Auth | `Authorization: Bearer <GITHUB_PAT>` or host OAuth when supported |
| Free account | Supported with PAT |
| Probe (2026-09-17) | `POST` without auth → **401** `missing required Authorization header` = **LIVE** |

This is the only correct connection for URL-only agent apps (Android mobile, OAuth-field UIs, any host that cannot spawn a process).

## Phone / URL-only app fields

| Field | Value |
|-------|--------|
| URL / Server URL | `https://api.githubcopilot.com/mcp/` |
| Type | HTTP / SSE / Streamable HTTP (whatever the app labels remote) |
| Authorization / Token / Header | `Bearer ghp_…` or paste PAT if the app adds `Bearer` itself |
| OAuth | Use if the app offers GitHub OAuth and completes browser login; otherwise PAT |

### PAT scopes (classic)

Minimum: `repo`
Add as needed: `read:org`, `gist`, `workflow`, etc.

Create: https://github.com/settings/tokens
Prefer fine-grained tokens limited to required repos when the app accepts them.

## Toolset URLs (optional)

Default (all default tools):

```text
https://api.githubcopilot.com/mcp/
```

Read-only:

```text
https://api.githubcopilot.com/mcp/readonly
```

Single toolset examples:

```text
https://api.githubcopilot.com/mcp/x/repos
https://api.githubcopilot.com/mcp/x/issues
https://api.githubcopilot.com/mcp/x/pull_requests
https://api.githubcopilot.com/mcp/x/actions
```

Full table: upstream `docs/remote-server.md` in `github/github-mcp-server`.

## What NOT to use for URL-only agents

| Bad | Why |
|-----|-----|
| `npx @modelcontextprotocol/server-github` | Archived package; local process |
| `docker run … ghcr.io/github/github-mcp-server` (stdio) | Local process |
| `http://localhost:8082` | Not reachable from phone |
| Vercel mcp-hub `/mcp/termux` or `/mcp/android` | Different servers; not GitHub MCP |

Self-host HTTP behind a public HTTPS URL is optional and **separate** (`mcp-docker/github-mcp/`). Not required when the GitHub-hosted URL works.

## Catalog

`mcp-hub/catalog.json` host id: **`github-remote`** — status `live_verified`.

## Separation

- GitHub-hosted remote ≠ Vercel mcp-hub
- Do not route this through `/mcp/github` on mcp-hub
- termux/android lanes stay on their own endpoints

Agent-Identity: Grok (Administrator)
