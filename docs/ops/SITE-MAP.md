# Site map — timerloggedout-spec web surfaces

**Goal:** Clear roles. No silent twins. Marketing ≠ ops dashboard.

```text
https://timerloggedout-spec.github.io/                 MARKETING / REFERRALS
https://timerloggedout-spec.github.io/help-wanted/     OPS DASHBOARD (canonical UI)
  sitemap → /help-wanted/sitemap.xml
  robots → /help-wanted/robots.txt
https://timerloggedout-spec.github.io/termux-monorepo/  PROJECT HUB (thin)
https://help-wanted-oversight-git-master-timerloggedout-5184s-projects.vercel.app/
  VERCEL MASTER (branch alias; public Vercel lane)
  stable project alias for the master branch; deployment target changes over time
  verify source SHA in Vercel before treating it as current
https://termux-monorepo.vercel.app                      PREVIEW PORTAL (WIP)
https://github.com/timerloggedout-spec/termux-monorepo SOURCE
```

## Dashboard URL policy

- **Canonical public dashboard:** `https://timerloggedout-spec.github.io/help-wanted/`.
- **Vercel:** the master branch alias is the public Vercel navigation target; it resolves to the current deployment assigned to that alias. The GitHub Pages URL remains the canonical dashboard.
- A reachable URL is not proof of source freshness; source SHA and deployment evidence remain authoritative.
- The dashboard sitemap indexes public dashboard destinations only; internal GitHub/Actions/inspector URLs are excluded.

## Navigation intent

| From | To | Why |
|------|----|-----|
| Marketing | `/help-wanted/` | Public ops transparency / operator entry |
| Marketing | Vercel portal | Product demo |
| `/termux-monorepo/` | `/help-wanted/` | Project Pages is hub, not product twin |
| Dashboard | `/help-wanted/sitemap.xml` | Machine-readable public discovery |
| Dashboard | `/help-wanted/robots.txt` | Crawler policy |

## Anti-patterns

- Publishing the same dashboard HTML as both project Pages root and `/help-wanted/`.
- Treating a Vercel deployment hostname as a permanent canonical URL.
- Using jsDelivr as primary HTML host (`text/plain`).

Skill: `github-pages-operator` · Deploy: `help-wanted-dashboard-deploy.yml`