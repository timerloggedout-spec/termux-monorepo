# Gravitee Integration — Recon Record

[MUSEai]@{role:{gravitee-integration}} · 2026-10-28 · Vendor-docs + live-API derived only.

## 1. In-repo state (verified via PAT helper, 2026-10-28)

- `docs/repositories/GRAVITEE-RESEARCH-SEED.md` + `docs/repositories/research-seeds/gravitee-api-management.json`: research-only, `adoption: research-only`, `integration_mode: upstream-comparison`, constraints: do-not-vendor-source, do-not-auto-submodule.
- Upstream: `gravitee-io/gravitee-api-management` (Apache-2.0, default branch `master`); fork: `timerloggedout-spec/gravitee-api-management_fork`.
- Seed-dir correction: gravitee is **no longer sole occupant** of `docs/repositories/research-seeds/` — `getdx.json` + `temporalio-temporal-set.json` also present (seed brief was stale on this point).
- Code search `Gravitee`: 27 hits, all docs/seed/registry class — **zero executable code**.
- Four-plane role (PR #1867, merged 74c5b5d3): **Gravitee = publication plane** (Bifrost = request, Temporal = time, getDX = measurement, Witness attests).

## 2. Surfaces (vendor docs: documentation.gravitee.io)

| Surface | What | Notes |
|---|---|---|
| APIM | Console UI, Portal UI, Gateway, Management API | Core product; lifecycle, policies/flows, plans, analytics, app registration |
| Access Management (AM) | CIAM / OAuth2 / OIDC authorization server | **Separate** Management API (see §3) — not APIM |
| API Designer | Drag-and-drop OAS design + mocked APIs | Enterprise, Gravitee-managed, optional even for self-hosted |
| Gravitee Cloud (ex-Cockpit) | Central multi-org/env management of APIM+AM | Enterprise/Gravitee-managed; own Cloud Token (§3) |

Deployment: **self-hosted** (Docker / Helm-Kubernetes, all components user-hosted), **hybrid** (SaaS control plane + self-hosted gateways), **cloud/SaaS** (signup via cockpit.gravitee.io).

## 3. API + auth model (vendor docs only)

- **APIM Management API v2**: REST, base `<instance>/management/v2`, resource path `/organizations/{orgId}/environments/{envId}/...`; OpenAPI descriptor published.
- **Auth = Personal Access Token, `Authorization: Bearer <PAT>`**. PAT minted on a **service account**: Console → Organization → Users → Add user → Service Account → assign roles (e.g. ADMIN org / API_PUBLISHER env) → Tokens → Generate a personal token. Shown **once**.
- Cloud instance URL shape: `https://<org>.<region>.api.gravitee.io/management/v2`; self-hosted example: `http://localhost:8083/management/v2`.
- **Gravitee Cloud Token** (Cloud Console → Settings → Cloud tokens, Automation scope) is a *different* credential for the Cloud control plane (also used by the Terraform provider) — not an APIM PAT.
- AM Management API (distinct): token endpoint `POST /management/auth/token` exchanges Basic user credentials for a bearer JWT. Not used by this connector.

## 4. Official MCP server — EXISTS (sourced)

- `gravitee-io/gravitee-apim-mcp-server`, introduced with APIM 4.9 (vendor blog + docs page "Expose APIM as an MCP Server", documentation.gravitee.io/apim/4.9).
- Generated from the Management API v2 OpenAPI spec; tools mirror mAPI operations. Transport stdio, Node.js 18+, run: `mcp-server.js start --bearer-auth <PAT> --server-url <instance>/management/v2`.
- Read-strong; write operations supported but may require Console follow-up. Governed by the service account's APIM permissions; does not bypass access controls.
- Distinct, not conflated: the **Gateway MCP entrypoint** exposes v4 proxy APIs *themselves* as MCP tools to consuming agents.

## 5. Connector state

- Scaffolded locally (fleet custom-connector pattern): `custom.gravitee` — CONNECTOR.md + connector.yaml + `bin/gravitee.py` (ping / list-envs / list-apis / get; surrogate credential via dynamic_credentials; redirects refused; compiles).
- **NOT registered, NOT verified.** No credential exists to register.

### Blockers (named; owner ruling required)

1. **Hosting ruling**: self-host vs Gravitee Cloud vs hybrid. No signup, no card, no account creation performed (standing rule).
2. **Instance host + org/env IDs**: Management API host is instance-specific, so `credentials.request_api_access` registration is impossible until an instance exists.
3. **PAT issuance**: service-account PAT must be minted inside that instance by its admin.

Unblock sequence: ruling → instance exists → register `custom.gravitee` (`api_key`, `bearer_header`, `api_hosts=[<instance-host>]`) → owner/instance-admin pastes PAT via vault flow → verify harmless read `GET /management/v2/organizations/{org}`.

## 6. Verdict

Recon complete; auth model proven (PAT/bearer, API-key class — Muse-connectable). Connector scaffold ready. Activation is blocked solely on the hosting/account ruling above — not on any technical unknown.
