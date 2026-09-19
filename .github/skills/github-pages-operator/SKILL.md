---
name: github-pages-operator
description: Enable and publish GitHub Pages for termux-monorepo help-wanted dashboard and other static ops surfaces. Prefer API enable + gh-pages branch + user-site mirror. Triggers on GitHub Pages, github.io, dashboard deploy, enable pages, gh-pages.
---

# Skill: github-pages-operator

**Canonical:** `.agents/skills/github-pages-operator/SKILL.md` on master (this path is CI/collaborator mirror).

See full skill body under `.agents/skills/github-pages-operator/SKILL.md`.

**Quick:**
1. Workflow `help-wanted-dashboard-deploy.yml` target=`all`
2. Enable Pages API → `gh-pages`
3. Mirror → `https://timerloggedout-spec.github.io/help-wanted/`
4. Fallback CDN → raw.githack (not jsDelivr for HTML)

Agent-Identity: Grok (Administrator)
