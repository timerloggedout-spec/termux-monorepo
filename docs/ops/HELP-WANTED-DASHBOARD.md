# Help-Wanted Oversight Dashboard — Live Surfaces

## Canonical public dashboard

**GitHub Pages:** https://timerloggedout-spec.github.io/help-wanted/

Machine-readable discovery:
- `/help-wanted/sitemap.xml`
- `/help-wanted/robots.txt`

## Verified Vercel deployment

https://help-wanted-oversight-git-master-timerloggedout-5184s-projects.vercel.app/

- State: READY
- Source SHA: `44626f77baa64d49f452f25f6cf23ef992160ce0`
- Project: `help-wanted-oversight`
- This hostname is deployment-specific, not canonical. Re-verify before publishing a replacement link.

## Other browser surfaces

| Priority | URL | Notes |
|---|---|---|
| 1 | https://timerloggedout-spec.github.io/help-wanted/ | Canonical public static ops dashboard |
| 2 | https://help-wanted-oversight-git-master-timerloggedout-5184s-projects.vercel.app/ | Vercel master branch alias |
| 3 | https://raw.githack.com/timerloggedout-spec/termux-monorepo/master/apps/help-wanted-dashboard/index.html | HTML fallback |
| 4 | https://timerloggedout-spec.github.io/termux-monorepo/ | Thin project hub, not dashboard twin |

Status JSON: https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/master/docs/ops/generated/help-wanted-status.json

## Operator deploy

Workflow: `.github/workflows/help-wanted-dashboard-deploy.yml`

Jobs: enable project Pages, publish project hub, mirror the user GitHub Pages dashboard, and optionally deploy Vercel production.

## Sitemap boundary

The XML sitemap contains only public dashboard destinations: canonical GitHub Pages plus the Vercel master branch alias. Internal repository paths, Actions URLs, Vercel inspector URLs, and credential-bearing surfaces are deliberately excluded.