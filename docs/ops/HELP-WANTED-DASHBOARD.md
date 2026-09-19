# Help-Wanted Oversight Dashboard — Live Surfaces

**Lane:** Oversight / evaluation (not MoneyBall admission)

## LIVE URLs (open in browser — no download)

| Surface | URL |
|---------|-----|
| **jsDelivr (primary interim)** | https://cdn.jsdelivr.net/gh/timerloggedout-spec/termux-monorepo@master/apps/help-wanted-dashboard/index.html |
| **raw.githack** | https://raw.githack.com/timerloggedout-spec/termux-monorepo/master/apps/help-wanted-dashboard/index.html |
| Status JSON | https://cdn.jsdelivr.net/gh/timerloggedout-spec/termux-monorepo@master/docs/ops/generated/help-wanted-status.json |
| GitHub tree | https://github.com/timerloggedout-spec/termux-monorepo/tree/master/apps/help-wanted-dashboard |

CDN serves `index.html` + `data/status.json` with correct MIME so the KPIs load without Xed-Editor.

## Operator deploy paths

Workflow: `.github/workflows/help-wanted-dashboard-deploy.yml` (merged #645)

| Target | Status |
|--------|--------|
| **GitHub Pages job** | **SUCCESS** — published `gh-pages` branch `f6f52e0`. Enable once: Settings → Pages → Deploy from branch **gh-pages** / root → then `https://timerloggedout-spec.github.io/termux-monorepo/` |
| **Vercel job** | Failed first run (token/link). Retry after confirming `VERCEL_TOKEN` on repo; optional `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID_HELP_WANTED=prj_iS20meBbcNw6lsng2GHjO4I9gC78` |

MCP cannot Production-Deploy (403). Actions + token is the Operator path. CDN is live **now** without waiting on Pages settings.

## Keep current

1. Commit evidence JSONL on success (not only Actions artifacts)
2. Regenerate `docs/ops/generated/help-wanted-status.json`
3. Push under watched paths → redeploy workflow

Or `workflow_dispatch` `help-wanted-dashboard-deploy` with `target=both`.

Agent-Identity: Grok (Administrator) · BIUDL
