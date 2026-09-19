# Grafana MCP Integration

## Purpose

This document defines the production boundary between interactive Grafana Cloud MCP access and GitHub Actions automation.

The integration has two deliberately separate authentication paths:

1. **Interactive ChatGPT / MCP path** — `https://mcp.grafana.com/mcp` using Grafana Cloud OAuth 2.1. Authorization happens in Grafana's browser consent flow and is user-scoped.
2. **GitHub automation path** — a Grafana service-account token supplied only to GitHub Actions as a secret. The token is never committed, emitted into evidence, or copied into chat.

Grafana Cloud's hosted MCP server is OAuth-based; the service-account token is for the automated/local Grafana API/MCP path rather than for the hosted OAuth endpoint.

## Required GitHub configuration

For repository automation, configure:

- `GRAFANA_SERVICE_ACCOUNT_TOKEN` — Grafana service-account token with the minimum RBAC/scopes required by the workflow.
- `GRAFANA_URL` — Grafana stack URL, preferably as a repository/environment variable because it is normally not a credential.

The smoke workflow also accepts the legacy aliases `GRAFANA_TOKEN` and `GRAFANA_API_KEY` for migration. `GRAFANA_API_KEY` is deprecated by Grafana in favor of `GRAFANA_SERVICE_ACCOUNT_TOKEN`.

Do not put either credential in source control, workflow YAML, generated evidence, artifacts, comments, or issue bodies.

## Interactive ChatGPT connection

When ChatGPT custom MCP apps are available for the workspace, configure a custom remote MCP app with:

- endpoint: `https://mcp.grafana.com/mcp`
- transport: Streamable HTTP
- optional header: `X-Grafana-URL: https://<your-stack>.grafana.net`
- authentication: OAuth 2.1 / PKCE as provided by Grafana Cloud

The user completes Grafana's browser authorization. ChatGPT then receives the authorized MCP connection; no GitHub secret needs to be exposed to ChatGPT.

If the current ChatGPT workspace does not expose custom MCP app creation, the repository integration remains usable independently and the interactive connection must be enabled by a workspace administrator through ChatGPT's supported custom-app/developer-mode surface.

## GitHub automation path

`.github/workflows/grafana-mcp-smoke.yml` performs a non-destructive connectivity check. It:

1. requires `GRAFANA_URL` and a service-account token;
2. calls Grafana's `/api/user` endpoint with the token;
3. records only safe identity metadata and HTTP status;
4. never prints the authorization header or token;
5. fails closed when credentials are absent or invalid.

The workflow is manual/reusable rather than a mandatory CI dependency. Grafana availability must not determine repository correctness.

## Security boundary

The existing observability architecture requires capability-gated telemetry: local structured evidence first; external telemetry only when explicitly configured; authorization material is never persisted; telemetry availability is infrastructure evidence rather than a task-quality score.

The same rule applies here. A successful Grafana connection proves connectivity/authorization only. It does not prove an agent task was correct.

## Verification loop

Use the repository's reconciliation cadence:

`WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT`

For Grafana integration:

- **WAIT:** allow the workflow or OAuth connection to settle.
- **WATCH:** observe the workflow run and Grafana connection state.
- **VALIDATE:** verify HTTP identity/health without exposing credentials.
- **RE-FETCH:** retrieve current workflow/run state rather than relying on cached status.
- **COMPARE:** compare expected configuration against observed state.
- **CLASSIFY:** distinguish missing secret, invalid token, insufficient RBAC, network failure, and successful authentication.
- **RECORD:** retain safe evidence only.
- **REPEAT:** retry only after the failure class is understood.

## Current limitation

The GitHub connector can modify repository contents and workflows but does not expose the GitHub Secrets API. Therefore this change intentionally does **not** attempt to create, copy, read, or rotate the secret. The operator must add the secret through GitHub's repository/environment secret UI.

Likewise, this repository change cannot itself grant ChatGPT access to the hosted Grafana MCP endpoint. That requires the supported ChatGPT custom MCP app/OAuth connection.

## References

- Grafana Cloud MCP: https://grafana.com/docs/grafana-cloud/ai-tools/mcp-servers/cloud-mcp/
- Grafana MCP RBAC/tool reference: https://grafana.com/docs/grafana/latest/developer-resources/mcp/reference/mcp-tools-table/
- ChatGPT developer mode and MCP apps: https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps
- Repository observability boundary: `docs/ops/ACTIONS-RUN-OBSERVABILITY.md`
