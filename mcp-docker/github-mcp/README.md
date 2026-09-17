# GitHub MCP Server — Docker Self-Host Lane

**Separated** from the Vercel `mcp-hub` (termux/android) lane.
This is a self-hosted container of the **official** GitHub MCP Server.

## Official image (what is ghcr.io?)

**ghcr.io** = GitHub Container Registry. It is GitHub’s built-in Docker image host
(same account as your repos). The official image lives at:

```text
ghcr.io/github/github-mcp-server:latest
```

Pull is public. No GHCR login required for this image. If pull fails with an
auth error, run `docker logout ghcr.io` and retry.

**Do not use** the archived community package:

- ❌ `npx -y @modelcontextprotocol/server-github` (unsupported as of 2025)
- ❌ Docker image `mcp/github` (old catalog entry)

Those snippets from older Gemini/search answers are stale.

## “Local” vs GitHub-hosted vs self-host HTTP

| What people say | What it actually means | Works with URL-only phone apps? |
|-----------------|------------------------|---------------------------------|
| **Local / stdio** | Process runs on the *same machine* as the agent client (Claude Desktop, Cursor). Client starts it via `command` + `args`. | **No** — phone UI has no process to spawn |
| **GitHub-hosted remote** | GitHub runs the server for you. You only paste a URL. | **Yes** |
| **Self-host HTTP (this lane)** | You run the official Docker image with `http` transport, then expose it (VPS, tunnel, reverse proxy). You get a URL *you* control. | **Yes**, once publicly reachable over HTTPS |

## URL-only clients (Android phone apps, OAuth fields, etc.)

If the agent app UI only accepts a **URL** (and maybe OAuth / Bearer fields),
use one of these:

### 1. Recommended zero-ops — GitHub-hosted remote

```text
https://api.githubcopilot.com/mcp/
```

- Already in `mcp-hub/catalog.json` as `github-remote`.
- Free-account users can authenticate with a Personal Access Token (Bearer)
  or OAuth where the host supports it.
- No Docker, no VPS, no self-host.

Paste that URL into the app. If the UI has an Authorization / OAuth / token
field, put a classic or fine-grained PAT (scopes: `repo`, and whatever else
you need).

### 2. Self-hosted public URL (this lane)

Run the official image in HTTP mode, then put a public HTTPS front door in
front of it (Caddy / nginx / Cloudflare Tunnel / ngrok / your VPS):

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_…

docker run --rm -p 8082:8082 \
  -e GITHUB_PERSONAL_ACCESS_TOKEN \
  ghcr.io/github/github-mcp-server \
  http
```

Server listens on port **8082**. Point your reverse proxy at it and give the
phone app the public URL, e.g.:

```text
https://mcp.yourdomain.com/
```

Optional upstream flags for production (base URL, OAuth metadata, scope
challenge): see
https://github.com/github/github-mcp-server/blob/main/docs/streamable-http.md

Keep this **separate** from the Vercel `mcp-hub` project.

## Transports (detail)

| Mode | Use when | How |
|------|----------|-----|
| **stdio** | Same-machine desktop agents | `docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server` |
| **Streamable HTTP** | Remote / phone / multi-client | `… github-mcp-server http` on port 8082 |

### stdio client config (desktop only)

```json
{
  "mcpServers": {
    "github-docker": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

### HTTP client config (any host that accepts URL + headers)

```json
{
  "mcpServers": {
    "github-docker-http": {
      "type": "http",
      "url": "https://mcp.yourdomain.com/",
      "headers": {
        "Authorization": "Bearer ghp_…"
      }
    }
  }
}
```

Or, for GitHub-hosted with no self-host:

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ghp_…"
      }
    }
  }
}
```

## docker-compose (persistent self-host)

See `docker-compose.yml` in this folder. Default binds `127.0.0.1:8082`.
Open the port to the world only behind TLS + auth.

```bash
cd mcp-docker/github-mcp
cp .env.example .env   # set PAT
docker compose up -d
```

## Token scopes (classic PAT)

Minimum useful set:

- `repo` — private + public repo operations
- `read:org` / `read:user` as needed
- `gist` only if you want gist tools

Prefer a fine-grained token limited to the repos the agent should touch.

## Relation to existing catalog

| ID | Transport | Notes |
|----|-----------|-------|
| `github-remote` | HTTP (GitHub-hosted) | `https://api.githubcopilot.com/mcp/` — **use this for URL-only phone apps** |
| `github-docker` (this) | stdio or Streamable HTTP (self-host) | Independent of Vercel hub; expose yourself if you need a custom URL |
| `termux` / `android` | Streamable HTTP (Vercel) | Stay on mcp-hub |

Do not fold this into the Vercel router. Keep the separation.

Agent-Identity: Grok (Administrator)
