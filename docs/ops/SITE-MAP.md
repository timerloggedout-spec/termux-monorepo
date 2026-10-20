# Site map — timerloggedout-spec web surfaces

**Goal:** Clear roles. No silent twins. Marketing ≠ ops dashboard.

```text
https://timerloggedout-spec.github.io/                 MARKETING / REFERRALS
https://timerloggedout-spec.github.io/help-wanted/     OPS DASHBOARD (canonical UI)
  sitemap → /help-wanted/sitemap.xml
  robots → /help-wanted/robots.txt
https://timerloggedout-spec.github.io/termux-monorepo/  PROJECT HUB (thin)
https://help-wanted-oversight-8w13bl125-timerloggedout-5184s-projects.vercel.app/
  VERIFIED VERCEL DEPLOYMENT (current observed production deployment)
  not canonical: Vercel deployment hostnames are ephemeral
  source SHA: 44626f77baa64d49f452f25f6cf23ef992160ce0
https://termux-monorepo.vercel.app                      PREVIEW PORTAL (WIP)
https://github.com/timerloggedout-spec/termux-monorepo SOURCE
```

## Dashboard URL policy

- **Canonical public dashboard:** `https://timerloggedout-spec.github.io/help-wanted/`.
- **Vercel:** the verified deployment URL above is deployment evidence/navigation only; it is not canonical because Vercel deployment hostnames are ephemeral.
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