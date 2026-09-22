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


## Control-surface topology

The public dashboard is now a provenance-aware projection rather than a static KPI page. The machine snapshot carries a `help-wanted.control-surface.v2` contract with source SHA, registered lane paths, complete commit history for those paths, and deployment topology. The UI exposes this as operator inspection/navigation plus a commit-derived evolution timeline.

### Evidence flow

`GitHub issues/PRs + Actions + evidence JSONL → help_wanted_status.py → versioned status snapshot → Pages/Vercel dashboard`

The dashboard never writes inferred facts back to the repository. Browser controls are navigation into authoritative GitHub surfaces. Reachability of a deployment is not accepted as proof that the intended SHA was deployed; provider/source verification remains part of promotion evidence.

### Additive-feature accounting

A dashboard feature is considered accounted for when its implementation/contract path is covered by the registered lane history and the resulting snapshot records the source SHA. This deliberately includes workflow, skill, generator, contract, and UI changes—not only `index.html`.
