---
name: github-pages-operator
description: Enable and publish GitHub Pages for termux-monorepo help-wanted dashboard and other static ops surfaces. Site map: marketing ≠ ops ≠ project hub. Triggers on GitHub Pages, github.io, dashboard deploy, enable pages, gh-pages.
---

# Skill: github-pages-operator

**Canonical:** `.agents/skills/github-pages-operator/SKILL.md` on master
**Load with:** `evidence-led-monorepo-ops` · `help-wanted-lane`
**Map:** `docs/ops/SITE-MAP.md`

## Site map (navigation goal)

| URL | Role |
|-----|------|
| `https://timerloggedout-spec.github.io/` | **Marketing / referrals** (CellCog invitation) |
| `https://timerloggedout-spec.github.io/help-wanted/` | **Ops dashboard** (canonical KPI UI) |
| `https://timerloggedout-spec.github.io/termux-monorepo/` | **Project hub** (thin links — never dashboard twin) |
| `https://termux-monorepo.vercel.app` | Preview portal WIP |

Cross-nav: Marketing ↔ Ops dashboard ↔ Monorepo ↔ Preview.

**Never** publish the full dashboard as both project Pages root and `/help-wanted/`.

## Deploy

Workflow `help-wanted-dashboard-deploy.yml`:
- `gh-pages` ← `apps/project-pages-hub/` only
- user site `/help-wanted/` ← `apps/help-wanted-dashboard/`

Agent-Identity: Grok (Administrator)
