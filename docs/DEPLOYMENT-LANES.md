# Deployment Lanes

> **Scope note:** this file is the SSOT for Vercel deployment lanes. The
> similarly named [docs/ops/DEPLOYMENT-LANES.md](ops/DEPLOYMENT-LANES.md) is a
> distinct record (n8n / SHE deployment + visual-composition architecture and
> admission rule) — a distinct architecture record.

Single source of truth for every Vercel project deployed from this org's
repos. A "lane" is one Vercel project with exactly one Root Directory. A
monorepo with independent deployables uses one project per deployable. Add a
row here whenever a new lane is created; update it whenever a lane's purpose
or Root Directory changes.

## Vercel lanes

| Vercel project | Source repo | Root Directory | Purpose | Owning proposal/PR | Status |
|---|---|---|---|---|---|
| mcp-hub | termux-monorepo | `mcp-hub` | Public, bearer-token-gated MCP router serving `termux-mcp` and `android-mcp` as submodules via dynamic `/mcp/:server` routes | PR #442, docs/proposals/active/vercel-lane-topology | live, production branch `master` |
| termux-monorepo | termux-monorepo | `demo-portal/public` | Public showcase lane (Operator concept): sandboxed Termux emulator running `archwiz.py` / `deepcli-tui` examples and more, alongside the persistent MCP endpoints hosted on the `mcp-hub` lane. Currently a placeholder page. | docs/proposals/active/vercel-lane-topology (VLT-001, closed), docs/proposals/active/demo-portal (build plan) | live, production branch `master`; repointed 2026-09-07 from `deepseek-cli` |

## Publication and evidence surface matrix

Vercel remains the primary interactive application-hosting lane for the
MCP/demo projects. Cloudflare Workers/D1 provide separate edge/data-plane
services, and Render carries a narrow image-backed README utility service.
GitHub Pages remains a distinct static-publication lane. These surfaces are
tracked here to preserve one source of truth and clear deployment boundaries.

| Surface | Role | Current repository evidence | Status / rule |
|---|---|---|---|
| **Vercel** | Application hosting and persistent MCP/demo deployment | `mcp-hub` and `demo-portal/public` are live lanes above; provider currently reports `build-rate-limit` on some Git-connected project checks. PR #1310 merged the path selector and the connected Vercel project settings for `mcp-hub`, `tribute-dash`, `tribute-oversight`, and `termux-monorepo` were updated to invoke it. | **LIVE, CAPACITY CONSTRAINED / SELECTOR CONFIGURED, EFFECT PENDING VERIFICATION** — keep one Vercel project per independently deployable root; next provider-eligible Git event must prove unrelated changes are skipped and relevant changes build. |
| **GitHub Pages** | Static publication for the project hub, matrix, and Help-Wanted dashboard | `.github/workflows/tribute-dashboard-deploy.yml` configures `gh-pages` and mirrors static routes into `timerloggedout-spec.github.io`; the `gh-pages` branch exists. The latest run/deployment evidence remains unobserved in the current RECON pass. | **CONFIGURED / PUBLICATION UNVERIFIED** — workflow and branch exist; verify the published URLs and source SHA before declaring LIVE. Static-only fallback; MCP/application services require a different hosting class. |
| **Render** | Image-backed README utility service | `ops/render-image/README.md`, `ops/render-image/Dockerfile`, `.github/workflows/readme-extractor-image.yml`, and `scripts/quota_poll.py` define the image build, GHCR publication, image-backed service, and optional quota reader | **REPO-WIRED / PROVIDER HEALTH PENDING** — confirm workspace, service identity, URL, latest deploy, source digest, and usage before declaring provider health LIVE |
| **Cloudflare Workers + D1** | Existing edge API and durable data-plane services | Connected-account inventory on 2026-11-23 returned 2 deployed Workers and 3 D1 databases; GraphQL Analytics confirms Worker and D1 activity; private usage counts remain in oversight; `tmx-device-queue` is the repo-backed pull-queue rendezvous. Queues inventory returned 0; R2 activation remains pending; Billing Read scope is required for financial usage | **WORKERS/D1 DEPLOYED / USAGE PARTIAL** — capture Billing Read metrics and keep D1, Queues, R2, and Pages as distinct products; Cloudflare Pages publication remains unverified |
| **Hex** | Analytics / Moneyball evidence layer, separate from primary application hosting | `docs/ops/HEX-MONEYBALL-INTEGRATION.md` and `hex-moneyball-evidence.yml` define the evidence contract | **INTEGRATED EVIDENCE SURFACE** — GitHub Actions remains execution/orchestration; durable audit retention remains outside Hex where required |
| **GitHub Wiki / DeepWiki / Devin Wiki** | Documentation and discovery surfaces | Root README and `wiki/` publisher define their distinct trust boundaries | **DOCUMENTATION SURFACES** — generated/discovery content remains separate from implementation authority without repository evidence |

### Hosting status vocabulary

Use these states consistently:

- **LIVE** — a concrete deployment is currently documented and independently
  verifiable from repository/provider evidence.
- **CANDIDATE / PENDING ACTIVATION** — the platform is an approved option, while the production lane remains unestablished in this repository.
- **AVAILABLE/CANDIDATE, UNPROVEN HERE** — the operator may have access to the
  platform, while this repository contains insufficient evidence to call a deployment live.
- **INTEGRATED EVIDENCE SURFACE** — the platform participates in analytics,
  evaluation, or evidence handling rather than serving the application.
- **DOCUMENTATION SURFACE** — publishing/discovery only; separate from source-change authorization.

## Deployment identity requirements

For every future hosting lane record, at minimum:

1. Provider and exact product (for example Vercel project, Cloudflare Pages
   project, Render service, or GitHub Pages site).
2. Source repository and exact root/directory boundary.
3. Production branch or immutable deployment source.
4. Public URL/domain, when applicable.
5. Owning proposal/PR and the validation evidence proving the deployment.
6. Environment/secrets names only; secret values remain private.
7. Whether the lane is authoritative production, preview, fallback, or
   experimental.

A provider connection alone establishes neither deployment existence nor source provenance. Reachability alone establishes neither the intended SHA nor deployment provenance. Promotion requires source/commit provenance and a
successful verification trail.

## Why separate lanes

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

The Render README utility is separate from the Render/n8n reference lane in
`docs/ops/DEPLOYMENT-LANES.md`; each record owns its stated scope.

## Adding a new lane

1. Create a new hosting project/site against this repo, set its source/root
   boundary and production branch explicitly.
2. Add or update the corresponding row in this file in the same PR/change that
   establishes the deployment.
3. Record the public URL/domain and immutable source/deployment evidence when
   the lane becomes live.
4. If the lane needs its own environment variables/secrets, document what
   names only; values remain private in the folder's own README.
5. If the lane duplicates an existing surface, document why it is a fallback,
   preview, experiment, or deliberate multi-provider redundancy rather than
   silently becoming another production source.
