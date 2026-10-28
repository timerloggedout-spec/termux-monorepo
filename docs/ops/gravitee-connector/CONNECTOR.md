# Gravitee

- `custom.gravitee` — SCAFFOLD, NOT REGISTERED, NOT VERIFIED (2026-10-28).
- Target API: Gravitee APIM **Management API v2**, base `<instance>/management/v2`,
  paths `/organizations/{orgId}/environments/{envId}/...`.
- Auth model (vendor docs, proven): **Personal Access Token as Bearer header**.
  PAT is generated on a **service account**: APIM Console → Organization →
  Users → Add user → Service Account → assign roles → Tokens → Generate a
  personal token (shown once). Distinct token: **Gravitee Cloud Token**
  (Cloud Console → Settings → Cloud tokens, Automation scope) serves the
  Gravitee Cloud control plane only — do not conflate.
- Helper: `~/workspace/custom-connectors/custom.gravitee/bin/gravitee.py`
  (ping / list-envs / list-apis / get). Compiles; every call currently exits
  BLOCKED (no base URL / no credential).

## Blockers (owner ruling required)

1. Hosting: self-hosted (Docker/Helm, e.g. `http://localhost:8083/management/v2`)
   vs Gravitee Cloud (`https://<org>.<region>.api.gravitee.io/management/v2`)
   vs hybrid. No signup/account creation done — standing no-card rule.
2. Instance host + org/env IDs. The Management API host is instance-specific,
   so `credentials.request_api_access` cannot be registered until the host
   exists. Registration details once known:
   `{"provider": "gravitee", "auth_scheme": "api_key", "placement": "bearer_header", "api_hosts": ["<instance-host>"]}`
3. Service-account PAT issuance inside that instance (owner/instance admin).

## Verify (once unblocked)

```text
python3 ~/workspace/custom-connectors/custom.gravitee/bin/gravitee.py --base-url <instance>/management/v2 ping
```

Harmless read: `GET /management/v2/organizations/{org}`. Untested until then.

## Credentials

- Credential will live only in the registered `custom.gravitee` connection;
  helpers use `dynamic_credentials.py` surrogates. Never put a token in this
  doc, a helper, a command argument, an environment variable, or a log.
- Keep redirects disabled on authenticated requests (helper enforces).

## Official MCP (alternative/complement)

- Official: `gravitee-io/gravitee-apim-mcp-server` (since APIM 4.9), generated
  from the Management API v2 OpenAPI spec, stdio, Node 18+, launched with
  `--bearer-auth <PAT> --server-url <instance>/management/v2`. Read-strong;
  writes may need Console follow-up. Same PAT + instance blockers apply.
- Distinct feature, not this connector: Gateway MCP entrypoint exposes v4
  proxy APIs themselves as MCP tools to agents.

## Limits

- Covers APIM Management API v2 only. Access Management has a separate
  Management API (token endpoint: `POST /management/auth/token`, Basic →
  bearer JWT) — not covered, not conflated.
- API Designer + Gravitee Cloud/Cockpit are Enterprise/Gravitee-managed
  surfaces with no PAT route established here.
