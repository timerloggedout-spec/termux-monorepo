# Deployment Lanes

Single source of truth for every Vercel project deployed from this org's
repos. A "lane" is one Vercel project — each has exactly one Root Directory,
so a monorepo with independent deployables needs one lane per deployable,
not one project reused for everything. Add a row here whenever a new lane
is created; update it whenever a lane's purpose or Root Directory changes.

## Vercel lanes

| Vercel project | Source repo | Root Directory | Purpose | Owning proposal/PR | Status |
|---|---|---|---|---|---|
| mcp-hub | termux-monorepo | `mcp-hub` | Public, bearer-token-gated MCP router serving `termux-mcp` and `android-mcp` as submodules via dynamic `/mcp/:server` routes | PR #442, docs/proposals/active/vercel-lane-topology | live, production branch `master` |
| termux-monorepo | termux-monorepo | `demo-portal/public` | Public showcase lane (Operator concept): sandboxed Termux emulator running `archwiz.py` / `deepcli-tui` examples and more, alongside the persistent MCP endpoints hosted on the `mcp-hub` lane. Currently a placeholder page. | docs/proposals/active/vercel-lane-topology (VLT-001, closed), docs/proposals/active/demo-portal (build plan) | live, production branch `master`; repointed 2026-09-07 from `deepseek-cli` |

## Publication and evidence surface matrix

Vercel is the only currently documented **live application-hosting lane** in
this repository. The other surfaces below are deliberately tracked here so
future publication work does not silently create a second, conflicting
source of truth.

| Surface | Role | Current repository evidence | Status / rule |
|---|---|---|---|
| **Vercel** | Application hosting and persistent MCP/demo deployment | `mcp-hub` and `demo-portal/public` are live lanes above | **LIVE** — keep one Vercel project per independently deployable root |
| **GitHub Pages** | Static publication / optional mobile-facing documentation or review surface | ICM docs explicitly describe Pages as a possible static publication path; the initiated CCTV surface says the Pages site is not enabled | **CANDIDATE / NOT ENABLED** — enable only through a reviewed workflow and record the resulting URL/lane here |
| **Render** | Candidate application/service hosting surface | The current deployment-lane SSOT has no Render project or production lane recorded | **AVAILABLE/CANDIDATE, UNPROVEN HERE** — do not describe a Render deployment as live until its project, root, branch, URL, and verification evidence are recorded |
| **Cloudflare / Cloudflare Pages** | Candidate static/edge publication and front-door/WAF surface | No live Cloudflare project is recorded in the deployment-lane SSOT | **AVAILABLE/CANDIDATE, UNPROVEN HERE** — record the exact product (Pages, Workers, etc.), project, source/root, branch, domain, and verification evidence before promotion |
| **Hex** | Analytics / Moneyball evidence layer, not primary application hosting | `docs/ops/HEX-MONEYBALL-INTEGRATION.md` and `hex-moneyball-evidence.yml` define the evidence contract | **INTEGRATED EVIDENCE SURFACE** — GitHub Actions remains execution/orchestration; durable audit retention remains outside Hex where required |
| **GitHub Wiki / DeepWiki / Devin Wiki** | Documentation and discovery surfaces | Root README and `wiki/` publisher define their distinct trust boundaries | **DOCUMENTATION SURFACES** — generated/discovery content never becomes implementation authority without repository evidence |

### Hosting status vocabulary

Use these states consistently:

- **LIVE** — a concrete deployment is currently documented and independently
  verifiable from repository/provider evidence.
- **CANDIDATE / NOT ENABLED** — the platform is an approved option, but no
  production lane has been established in this repository.
- **AVAILABLE/CANDIDATE, UNPROVEN HERE** — the operator may have access to the
  platform, but this repository does not yet contain enough evidence to call
  a deployment live.
- **INTEGRATED EVIDENCE SURFACE** — the platform participates in analytics,
  evaluation, or evidence handling rather than serving the application.
- **DOCUMENTATION SURFACE** — publishing/discovery only; never an authorization
  boundary for source changes.

## Deployment identity requirements

For every future hosting lane record, at minimum:

1. Provider and exact product (for example Vercel project, Cloudflare Pages
   project, Render service, or GitHub Pages site).
2. Source repository and exact root/directory boundary.
3. Production branch or immutable deployment source.
4. Public URL/domain, when applicable.
5. Owning proposal/PR and the validation evidence proving the deployment.
6. Environment/secrets names only — never secret values.
7. Whether the lane is authoritative production, preview, fallback, or
   experimental.

A provider being connected or available is **not** evidence that a deployment
exists. A deployment being reachable is not, by itself, evidence that the
intended SHA was deployed. Promotion requires source/commit provenance and a
successful verification trail.

## Why lanes, not one project

Vercel's Root Directory is a single value per project. A repo hosting more
than one independently-deployable thing (an MCP router, a docs site, a demo
app, ...) needs one Vercel project per thing, each pointed at its own
subfolder, all against the same GitHub repo. Reusing one project for a new
purpose silently stops serving whatever it served before — that mistake is
exactly what created the ambiguity this file exists to prevent (see
`docs/proposals/active/vercel-lane-topology/DEBATE.md` for the incident).

The same identity rule applies to Render, Cloudflare, GitHub Pages, or any
future hosting provider: one independently deployable artifact gets one
explicitly named lane and one recorded source boundary.

## Adding a new lane

1. Create a new hosting project/site against this repo, set its source/root
   boundary and production branch explicitly.
2. Add or update the corresponding row in this file in the same PR/change that
   establishes the deployment.
3. Record the public URL/domain and immutable source/deployment evidence when
   the lane becomes live.
4. If the lane needs its own environment variables/secrets, document what
   they are (not their values) in the folder's own README.
5. If the lane duplicates an existing surface, document why it is a fallback,
   preview, experiment, or deliberate multi-provider redundancy rather than
   silently becoming another production source.
