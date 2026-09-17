# GitHub MCP Server — Docker Self-Host Lane

**Separated** from the Vercel `mcp-hub` (termux/android) lane.
This is a self-hosted container of the **official** GitHub MCP Server.

Official image: `ghcr.io/github/github-mcp-server`  
(Do **not** use the archived `@modelcontextprotocol/server-github` npm package.)

## Why this lane exists

- Vercel hub already exposes `termux` + `android` + points at GitHub’s hosted remote (`api.githubcopilot.com/mcp/`).
- This lane gives a **self-hosted** Docker option (local stdio **or** remote Streamable HTTP) under operator control.
- No Vercel project, no shared auth token with the hub. Fully independent.

## Transports

| Mode | Use when | Command / config |
|------|----------|------------------|
| **stdio** | Local agent / Claude Desktop / same-machine client | `docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN …` |
| **Streamable HTTP** | Remote agents, reverse proxy, multi-client | `docker run … github-mcp-server http` (port 8082) |

## Quick start — stdio (local)

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_…

docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN \
  ghcr.io/github/github-mcp-server
```

Client config example (Cursor / Claude Desktop):

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

## Quick start — Streamable HTTP (remote)

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_…

docker run --rm -p 8082:8082 \
  -e GITHUB_PERSONAL_ACCESS_TOKEN \
  ghcr.io/github/github-mcp-server \
  http
```

Server listens on `http://0.0.0.0:8082`.

Client:

```json
{
  "mcpServers": {
    "github-docker-http": {
      "type": "http",
      "url": "http://localhost:8082",
      "headers": {
        "Authorization": "Bearer ghp_…"
      }
    }
  }
}
```

Production: put a reverse proxy (Caddy/nginx/Traefik) in front, set `--base-url` / `--base-path` if needed, and never expose the PAT in the clear.

See upstream docs:  
https://github.com/github/github-mcp-server/blob/main/docs/streamable-http.md

## docker-compose (persistent)

```yaml
# mcp-docker/github-mcp/docker-compose.yml
version: "3.8"
services:
  github-mcp:
    image: ghcr.io/github/github-mcp-server:latest
    container_name: github-mcp-server
    restart: unless-stopped
    ports:
      - "8082:8082"
    environment:
      GITHUB_PERSONAL_ACCESS_TOKEN: ${GITHUB_PERSONAL_ACCESS_TOKEN}
      # Optional: GITHUB_HOST for GHES / ghe.com
    command: ["http"]
    # For pure stdio omit ports + command and use stdin_open/tty
```

```bash
cd mcp-docker/github-mcp
cp .env.example .env   # put your PAT
docker compose up -d
```

## Security notes

- Prefer least-privilege classic PAT or fine-grained token.
- Never commit tokens. Use env / secret store.
- HTTP mode: bind to loopback or protect with reverse-proxy + TLS + auth.
- Official image is public; `docker logout ghcr.io` if you hit auth errors on pull.

## Relation to existing catalog

| ID | Transport | Notes |
|----|-----------|-------|
| `github-remote` | HTTP (GitHub-hosted) | `https://api.githubcopilot.com/mcp/` — already in mcp-hub/catalog.json |
| `github-docker` (this) | stdio or Streamable HTTP (self-host) | Independent of Vercel hub |
| `termux` / `android` | Streamable HTTP (Vercel) | Stay on mcp-hub |

Do not fold this into the Vercel router. Keep the separation.

Agent-Identity: Grok (Administrator)
