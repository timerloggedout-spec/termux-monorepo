# Deploy failure triage — 2026-10-18

Additive record. Nothing existing was moved or removed.

## Vercel: gh-pages Preview failures (4 projects)

- Projects hit on every `gh-pages` push: `mcp-hub`, `help-wanted-dash`, `help-wanted-oversight`, `termux-monorepo` (team `timerloggedout-5184's projects`).
- `gh-pages` is written by `.github/workflows/help-wanted-dashboard-deploy.yml` (`peaceiris/actions-gh-pages`, `force_orphan: true`) and only holds `index.html`, `matrix.html`, `data/`, `.nojekyll`. None of the lanes' Root Directories (`mcp-hub`, `demo-portal/public`, `apps/help-wanted-dashboard`, ...) exist there, so each Preview build fails.
- Fix (this PR): the publish job now writes a `vercel.json` with `git.deploymentEnabled: false` and a fallback `ignoreCommand: "exit 0"` at the artifact root and at each known lane Root Directory. Vercel reads `vercel.json` from the deployed commit, so the setting has to live on `gh-pages` itself; `force_orphan` would wipe any hand-added file, which is why it is generated in the workflow.
- Belt and braces (dashboard, optional): Project → Settings → Git → Ignored Build Step → "Only build production" or custom `[ "$VERCEL_GIT_COMMIT_REF" != "gh-pages" ]`.

## Render: termux-readme-extractor

- Service: `srv-d9pq9pajnfac73a73sh0`, branch `master`.
- Root cause is **not** a code/build error. Render's account email "[Important] Build failed on your Render account" says the workspace hit its **build pipeline minute spend limit of $0.00**. First hit 2026-09-23 (reset 2026-10-01), hit again 2026-10-08; next reset **2026-11-01**.
- Why minutes ran out: auto-deploy fires on every `master` commit, and most `master` commits are bot status refreshes (lane-matrix sweep, accountability receipts, generated status JSON). ~490 failed deploy notices since 2026-09-20.
- To get green (needs Render dashboard, owner decision):
  1. Either raise the pipeline spend limit (Settings → Spend limit) or wait for the 2026-11-01 reset.
  2. Stop the churn: Service → Settings → Build Filters → include only the paths this service actually builds from, or set Auto-Deploy to "After CI checks pass" / off.
  3. Bot commits can also carry `[skip render]` in the commit message to skip a Render deploy.
