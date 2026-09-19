---
name: github-pages-operator
description: Enable and publish GitHub Pages for termux-monorepo help-wanted dashboard and other static ops surfaces. Prefer API enable + gh-pages branch + user-site mirror. Triggers on GitHub Pages, github.io, dashboard deploy, enable pages, gh-pages.
---

# Skill: github-pages-operator

**Owner:** Grok Administrator / Operator lane  
**Canonical:** `.agents/skills/github-pages-operator/SKILL.md` on master  
**Load with:** `evidence-led-monorepo-ops` · `help-wanted-lane`

## INTENT

Ship a **browser-rendered** dashboard without human Xed-Editor downloads.

jsDelivr often serves `text/plain` for `.html` → looks like raw source.  
**Prefer:** GitHack, project Pages (`*.github.io/<repo>/`), or user site mirror.

## Surfaces (priority)

1. **Project Pages** — `https://timerloggedout-spec.github.io/termux-monorepo/`  
   Requires Pages **enabled** (API POST/PUT) + `gh-pages` branch content.
2. **User site mirror** — `https://timerloggedout-spec.github.io/help-wanted/`  
   Publish into `timerloggedout-spec/timerloggedout-spec.github.io` `main` under `help-wanted/`.
3. **GitHack CDN** — always works for HTML MIME:  
   `https://raw.githack.com/timerloggedout-spec/termux-monorepo/master/apps/help-wanted-dashboard/index.html`
4. **Vercel** — optional; needs `VERCEL_TOKEN` + deploy role.

## Operator loop

1. Ensure `apps/help-wanted-dashboard/` + `docs/ops/generated/help-wanted-status.json` on master.
2. Run workflow `help-wanted-dashboard-deploy.yml` (`target=all`).
3. Job `enable-project-pages` → POST/PUT `/repos/.../pages` source=`gh-pages` `/`.
4. Job `publish-gh-pages` → peaceiris → `gh-pages` branch.
5. Job `mirror-user-github-io` → external repo (needs PAT with write on user pages repo).
6. Probe URLs; record in `docs/ops/HELP-WANTED-DASHBOARD.md`.

## Secrets (never paste values in issues)

| Secret | Use |
|--------|-----|
| `GITHUB_TOKEN` | Same-repo `gh-pages` publish; may lack Pages create |
| `OPERATOR_GITHUB_TOKEN` / `ARCHWIZ_GITHUB_TOKEN` / `GH_PAT` | Enable Pages + write `timerloggedout-spec.github.io` |
| `VERCEL_TOKEN` | Optional Vercel prod |

Inventory SSOT: issue **#184** (status notes only — **do not** store token values in issues). Prefer repo secrets + routing docs.

## Enable Pages API

```bash
# Create (404 today)
POST /repos/{owner}/{repo}/pages
{"build_type":"legacy","source":{"branch":"gh-pages","path":"/"}}

# Update source
PUT /repos/{owner}/{repo}/pages
{"build_type":"legacy","source":{"branch":"gh-pages","path":"/"}}
```

## Anti-patterns

- Pointing humans only at jsDelivr for HTML (MIME = text/plain).
- Claiming github.io live when GET `/repos/.../pages` is 404.
- Pasting PAT values into #184 / PR bodies.

Agent-Identity: Grok (Administrator)
