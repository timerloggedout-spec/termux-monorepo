# Help-Wanted Oversight Dashboard — Live Surfaces

**Skill:** `github-pages-operator` (`.agents/skills/github-pages-operator/SKILL.md`)

## Open in browser (rendered HTML)

| Priority | URL | Notes |
|----------|-----|--------|
| **1 GitHack** | https://raw.githack.com/timerloggedout-spec/termux-monorepo/master/apps/help-wanted-dashboard/index.html | Correct HTML MIME |
| **2 User site** | https://timerloggedout-spec.github.io/help-wanted/ | After mirror job (PAT) |
| **3 Project Pages** | https://timerloggedout-spec.github.io/termux-monorepo/ | After enable-pages job succeeds |
| jsDelivr | https://cdn.jsdelivr.net/gh/timerloggedout-spec/termux-monorepo@master/apps/help-wanted-dashboard/index.html | Often **text/plain** → looks like raw source |

Status JSON:
https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/master/docs/ops/generated/help-wanted-status.json

## Operator deploy

Workflow: `.github/workflows/help-wanted-dashboard-deploy.yml`

Jobs:

1. **enable-project-pages** — POST/PUT Pages API (`OPERATOR_GITHUB_TOKEN` / `ARCHWIZ_GITHUB_TOKEN` preferred)
2. **publish-gh-pages** — content on `gh-pages`
3. **mirror-user-github-io** — `timerloggedout-spec.github.io/help-wanted/`
4. **vercel-prod** — optional, `continue-on-error`

```bash
gh workflow run help-wanted-dashboard-deploy.yml -f target=all
```

Credential inventory: issue **#184** (notes only; never paste secrets).

Agent-Identity: Grok (Administrator) · BIUDL
