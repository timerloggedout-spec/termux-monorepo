# Vercel alternatives and deployment failover plan

**Status:** decision record / evaluation plan. No production migration or provider account activation is implied.

## Executive decision

Do not replace Vercel with one provider across the monorepo. Split the decision by workload:

1. **GitHub Pages — immediate static fallback.** Reuse the existing `gh-pages` publication lane for static dashboards, project hub, documentation and generated reports after verifying the deployed URL and source SHA. It cannot host the dynamic MCP router or persistent application processes.
2. **Cloudflare Pages + Workers — preferred next technical evaluation.** Pages is a static delivery candidate; Workers is the application/API candidate. Keep these as separate deployment products and explicit lanes. Cloudflare's current Pages documentation recommends starting new application projects on Workers; Pages static assets are free/unlimited, while Functions consume Workers request allowance. The current Workers Free limits include 100,000 requests/day and 10 ms CPU/request. This is a candidate, not a verified fleet deployment.
3. **Netlify — viable static/Jamstack alternative, but not the first failover choice.** Current Free pricing is credit-based (300 credits/month, hard limit); production deploys cost 15 credits, bandwidth 20 credits/GB, compute 10 credits/GB-hour, and requests 2 credits per 10,000. At the limit projects pause until the next cycle. That is another quota/capacity risk rather than an obvious cure for the present Vercel build cap.
4. **Render — service/container candidate, not a free production substitute.** The existing repository records a Render image-backed service and a previous build-pipeline spend-limit incident. Render's current docs explicitly say Free instances are for testing/hobby/preview, not production; free web services sleep after 15 minutes idle, wake in about a minute, and have ephemeral filesystems. Use a paid service only after cost approval and build filters are proven.
5. **Keep Vercel selectively during transition.** Retain the live MCP/application lane until a replacement passes API, auth, streaming/transport, cold-start, performance, security and provenance checks. A build-rate-limit check failure is not proof the running production service is down.

## Repository-grounded workload map

| Workload | First fallback / target | What it can replace | Hard boundary |
|---|---|---|---|
| Project hub, static dashboard, matrices, generated reports | GitHub Pages | Static HTML/CSS/JS/JSON artifacts | No dynamic server, persistent process, or MCP API |
| Static frontend with light edge logic | Cloudflare Pages (or Workers static assets) | Static delivery and compatible edge functions | Function limits and bindings must be tested; do not assume Pages and Workers have identical deployment contracts |
| API / webhook / edge receiver | Cloudflare Workers evaluation | Stateless HTTP handlers, webhook receivers, bounded API routes | Validate runtime compatibility, auth, request/body limits, CPU, secrets, storage bindings and observability |
| Persistent MCP router / long-lived service | Keep Vercel until parity; evaluate a paid container/service or redesigned Workers transport | Only after protocol and transport parity | Pages alone is not a replacement; verify streaming/SSE or current MCP transport, auth, submodule build, routing, timeouts and connection behavior |
| Container/image service | Existing Render service or paid container alternative | Container-backed workload | Free Render is not production-grade; filter paths and budget build pipeline before reactivation |
| Documentation site | GitHub Pages first; Netlify/Cloudflare Pages as alternatives | Static docs | Verify custom domain, redirects, headers, search/index generation and artifact provenance |

## Current repository facts and cautions

- `docs/DEPLOYMENT-LANES.md` identifies `mcp-hub` and `demo-portal/public` as the currently documented live Vercel application lanes. It records GitHub Pages as configured but says current publication evidence must be re-verified.
- `.github/workflows/tribute-dashboard-deploy.yml` is the existing Pages publication path; the `gh-pages` branch exists. Do not mark it healthy solely because the branch exists.
- `docs/ops/DEPLOY-FAILURES-2026-10-18.md` records Render build-pipeline spend-limit exhaustion caused by broad auto-deploy on `master`; path filters / CI-gated deploy / disabling auto-deploy were the documented mitigations.
- The same repo's October 21 free-tier recon identifies Cloudflare Workers/Pages as an underbuilt candidate and GitHub Pages as a static failover lane. Its figures are historical research; current provider docs below supersede figures where they differ.
- A prior Cloudflare Tunnel consent block is not evidence that Cloudflare Pages or Workers is unavailable; Tunnel, Pages and Workers are distinct products.
- Do not copy private credentials into repository files, logs, issues or artifacts. Record secret names only.

## Phased execution

### Phase 0 — stabilize current Vercel capacity
- Keep the existing path-scoped ignored-build selector and verify it skips unrelated changes while still building relevant roots.
- Avoid deployment fan-out on generated/status-only commits.
- Keep one Vercel project per independently deployable root.
- Capture provider error, project, branch, source SHA, timestamp and whether the failure was build-rate-limit vs build failure.

### Phase 1 — prove static failover
- Inspect the Pages workflow and current `gh-pages` artifact layout.
- Build from a pinned source SHA and publish only the intended static roots.
- Smoke-test every expected route, assets, redirects, headers and JSON feeds.
- Record public URL, deployment/run ID, source SHA, artifact digest and verification timestamp.
- Do not switch canonical links until the evidence is complete.

### Phase 2 — Cloudflare proof of concept
- First inventory account/site/domain access and current project state; do not assume the connected integration is authorized or an active site exists.
- Select one low-risk static dashboard as a canary. Compare Cloudflare Pages and Workers static assets only if their deployment contracts differ materially.
- If successful, test a small stateless API route in Workers with least-privilege bindings and no production secrets.
- Record free-plan ceilings, runtime compatibility, build behavior, logs, rollback, custom-domain/TLS and source-SHA provenance.
- No MCP production migration in this phase.

### Phase 3 — application/MCP parity gate
A candidate may replace a Vercel application lane only after:
- exact source SHA is traceable from build to deployment;
- auth and bearer-token handling are equivalent or stronger;
- MCP protocol and current transport behavior pass contract tests (including streaming where used);
- routing across submodules/servers and error semantics match;
- request duration, payload limits, concurrency, cold-start and availability are measured;
- secrets are configured through provider secret management, not repository content;
- rollback and independent health checks are demonstrated;
- owner approves domain/DNS cutover and a tested rollback plan exists.

### Phase 4 — remove redundant Vercel spend only after observation
Run both lanes in shadow/preview mode for a defined observation window. Compare correctness, latency, errors, cost/usage, deploy reliability and rollback. Only then decide whether to downgrade/remove a Vercel project. Preserve the previous production lane until the replacement is independently verified.

## Acceptance checklist

- [ ] Every deployable root has an owner, runtime class and explicit fallback.
- [ ] Static fallback is live and its exact source SHA is verified.
- [ ] Dynamic API/MCP parity is demonstrated before cutover.
- [ ] Provider quota and build triggers are measured; no unlimited/free assumptions.
- [ ] No secret values appear in code, logs, PRs or artifacts.
- [ ] Production and preview domains are distinct and rollback-tested.
- [ ] Deployment-lane SSOT and README are updated in the same change as any real deployment.

## Provider documentation checked 2026-11-02

- Cloudflare Pages overview: https://developers.cloudflare.com/pages/
- Cloudflare Pages Functions pricing: https://developers.cloudflare.com/pages/functions/pricing/
- Cloudflare Workers limits: https://developers.cloudflare.com/workers/platform/limits/
- Netlify pricing: https://www.netlify.com/pricing/
- Netlify credit-based plan details: https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/
- Render Free service limits: https://render.com/docs/free

Vendor limits and plans change. Re-check official terms, account entitlements and billing controls before relying on a free allowance or enabling a production lane.
