# Site map — timerloggedout-spec web surfaces

**Goal:** Clear roles. No silent twins. Marketing ≠ ops dashboard.

```text
https://timerloggedout-spec.github.io/                 MARKETING / REFERRALS
  brand: Autonomous AI Employees (CellCog partner)
  CTA: invitation credits
  nav → Why | Demo | Ops dashboard | Get started

https://timerloggedout-spec.github.io/help-wanted/     OPS DASHBOARD (canonical UI)
  help-wanted KPIs / receipts / neighbor policy
  nav → Marketing | Ops (here) | Monorepo | Preview | Project hub

https://timerloggedout-spec.github.io/termux-monorepo/  PROJECT HUB (thin)
  NOT a dashboard clone — links + optional redirect to /help-wanted/

https://termux-monorepo.vercel.app                      PREVIEW PORTAL (WIP)
https://github.com/timerloggedout-spec/termux-monorepo SOURCE
```

## Navigation intent

| From | To | Why |
|------|----|-----|
| Marketing | CellCog invitation | Referral conversion |
| Marketing | `/help-wanted/` | Public ops transparency / operator entry |
| Marketing | Vercel portal | Product demo |
| `/help-wanted/` | Marketing home | Exit ops → brand |
| `/termux-monorepo/` | `/help-wanted/` | Project Pages is hub, not product twin |

## Anti-patterns (fixed)

- Publishing the **same dashboard HTML** as both project Pages root and `/help-wanted/` (false parity).
- Leaving marketing with **zero link** into the ops surface.
- Using jsDelivr as primary HTML host (`text/plain`).

Skill: `github-pages-operator` · Deploy: `help-wanted-dashboard-deploy.yml`

Agent-Identity: Grok (Administrator)
