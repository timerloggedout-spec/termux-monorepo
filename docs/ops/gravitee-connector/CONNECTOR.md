# Gravitee

- `custom.gravitee` — BUILD COMPLETE, mock-verified; NOT registered against a
  live instance (no instance exists). 2026-10-28.
- API: Gravitee APIM **Management API v2** (APIM 4.12 surface). Root base
  `<host>/management/v2`; org base `<host>/management/v2/organizations/{orgId}`
  (spec `servers:` in the official MCP repo's vendored OpenAPI:
  `gravitee-io/gravitee-apim-mcp-server/.speakeasy/openapi-{apis,environments}.yaml`
  = **149 paths / 189 operations**).
- Auth (vendor docs): **service-account Personal Access Token**, Bearer header.
  Mint: Console → Organization → Users → Service Account → roles → Tokens →
  Generate (shown once). Cloud Token (Gravitee Cloud control plane) and the AM
  Management API are different surfaces — not covered, not conflated.

## Helper

`~/workspace/custom-connectors/custom.gravitee/bin/gravitee.py` (in-repo copy:
`docs/ops/gravitee-connector/`). 42 named commands + generic fallback covering
any spec path:

- Reads: `ping envs env apis api api-export plans plan pages page subscriptions
  subscription members analytics health logs audits groups integrations
  integration clusters cluster scoring spg portal-pages`
- Writes (require `--yes`): `api-create api-import api-update api-delete
  api-start api-stop api-deploy plan-create plan-publish plan-close page-create
  page-publish sub-accept sub-reject sub-close sub-pause sub-resume key-renew
  key-revoke spg-deploy`
- Generic: `get|post|put|patch|delete <path> [--file body.json]` (org base)
- Utility: `ops` (coverage), `mcp-config` (official MCP client JSON; token as
  `${APIM_BEARER_TOKEN}` placeholder only)
- Global: `--base-url <root /management/v2 URL>` or `GRAVITEE_BASE_URL`
  (non-secret config), `--org`, `--env` (default `DEFAULT`/`DEFAULT`).

## Verify

- Mock-mAPI integration test (in-repo: `docs/ops/gravitee-connector/test_gravitee.py`):
  local HTTP server serving documented v2 shapes + stubbed credential module
  (test token only). **PASS 2026-10-28**: exact paths, Bearer header, write
  guard (exit 3 without `--yes`), BLOCKED exit 2 without base URL, mcp-config
  contains no token.
- Live verification = first harmless read once an instance exists:
  `gravitee.py --base-url <instance>/management/v2 ping`
  (`GET /management/v2/organizations/{org}`). **Untested live.**

## Remaining blocker (unchanged, external)

No instance/account: no signup/card per owner rule; self-host infeasible on
this VM (no docker; ~0.5G RAM free of 7.7G — APIM stack needs Mongo + search +
gateway + mAPI + consoles). Unblock = instance on owner's host or Cloud org →
register `custom.gravitee` (`api_key`, `bearer_header`, `api_hosts=[<instance
host>]`) → PAT via vault → `ping`.

## Official MCP (maximum-benefit route, ready)

`npx @gravitee/apim-mcp-server start --mode dynamic --bearer-auth <PAT>
--server-url <instance>/management/v2` — official, generated from the same
OpenAPI; dynamic mode = 4 discovery/execution tools instead of 189 tools.
`gravitee.py mcp-config` emits the client JSON. Same PAT/instance blocker.

## Credentials

Credential lives only in the registered connection once created; helpers use
`dynamic_credentials.py` surrogates; redirects refused on authed requests.
Never put a token in docs, helpers, args, env vars, or logs.
