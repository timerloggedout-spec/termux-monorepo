# Help-Wanted Oversight Dashboard

Static KPI surface for the help-wanted lane.

## Live deploy

See `docs/ops/HELP-WANTED-DASHBOARD.md` and workflow `help-wanted-dashboard-deploy.yml`.

- **Vercel:** Actions job uses `secrets.VERCEL_TOKEN`
- **GitHub Pages:** `gh-pages` branch → `https://timerloggedout-spec.github.io/termux-monorepo/`

## Local

Open `index.html` or serve the folder. Data: `data/status.json` (synced from `docs/ops/generated/help-wanted-status.json` on deploy).
