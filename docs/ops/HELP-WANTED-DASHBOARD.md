# Help-Wanted Oversight Dashboard — Live Surfaces

**Lane:** Oversight / evaluation (not MoneyBall admission)

## Sources of truth

| Layer | Path |
|-------|------|
| Evidence receipts | `docs/ops/generated/help-wanted-evidence/*.jsonl` |
| Machine status | `docs/ops/generated/help-wanted-status.json` |
| Static app | `apps/help-wanted-dashboard/` |

## Deploy paths (Operator)

Workflow: `.github/workflows/help-wanted-dashboard-deploy.yml`

| Target | Mechanism | Secrets |
|--------|-----------|---------|
| **Vercel** | `vercel deploy --prod` | `VERCEL_TOKEN` (required). Optional: `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID_HELP_WANTED` |
| **GitHub Pages** | `peaceiris/actions-gh-pages` → `gh-pages` branch | `GITHUB_TOKEN` (default) |

Defaults:

- Team / org: `team_jKHy7m9xZrvrGP5cAlIMPs3S`
- Project id (created): `prj_iS20meBbcNw6lsng2GHjO4I9gC78` (`help-wanted-dash`)

### Expected live URLs

1. **Vercel** — whatever `vercel deploy --prod` prints (artifact `help-wanted-vercel-deploy`). Typically `https://help-wanted-dash.vercel.app` once project is linked.
2. **GitHub Pages** — after Settings → Pages → Source = **Deploy from branch** `gh-pages` / `/ (root)`:
   - `https://timerloggedout-spec.github.io/termux-monorepo/`

MCP cannot create Production Deployments (team role). **Actions + VERCEL_TOKEN** is the Operator bypass.

## Keep it current

1. Execute lane writes receipts → commit JSONL (commit-on-success).
2. `help_wanted_status.py` regenerates `help-wanted-status.json`.
3. Push to `master` under watched paths → this workflow redeploys.

Or `workflow_dispatch` with `target=both`.

Agent-Identity: Grok (Administrator) · BIUDL
