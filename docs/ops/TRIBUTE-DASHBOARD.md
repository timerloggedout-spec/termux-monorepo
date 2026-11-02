# Tribute Dashboard — Live Surfaces

## Canonical public dashboard

The former `/help-wanted/` path remains published as a compatibility alias.

**GitHub Pages:** https://timerloggedout-spec.github.io/tribute/

Machine-readable discovery:
- `/help-wanted/sitemap.xml`
- `/help-wanted/robots.txt`

## Verified Vercel deployment

https://help-wanted-oversight-8w13bl125-timerloggedout-5184s-projects.vercel.app/

- State: READY
- Source SHA: `44626f77baa64d49f452f25f6cf23ef992160ce0`
- Project: `help-wanted-oversight`
- This hostname is deployment-specific, not canonical. Re-verify before publishing a replacement link.

## Other browser surfaces

| Priority | URL | Notes |
|---|---|---|
| 1 | https://timerloggedout-spec.github.io/tribute/ | Canonical public static ops dashboard |
| 2 | https://help-wanted-oversight-8w13bl125-timerloggedout-5184s-projects.vercel.app/ | Current READY Vercel deployment |
| 3 | https://raw.githack.com/timerloggedout-spec/termux-monorepo/master/apps/help-wanted-dashboard/index.html | HTML fallback |
| 4 | https://timerloggedout-spec.github.io/termux-monorepo/ | Thin project hub, not dashboard twin |

Status JSON: https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/master/docs/ops/generated/tribute-status.json

## Operator deploy

Workflow: `.github/workflows/help-wanted-dashboard-deploy.yml`

Jobs: enable project Pages, publish project hub, mirror the user GitHub Pages dashboard, and optionally deploy Vercel production.

## Sitemap boundary

The XML sitemap contains only public dashboard destinations. Internal repository paths, Actions URLs, Vercel inspector URLs, and credential-bearing surfaces are deliberately excluded.