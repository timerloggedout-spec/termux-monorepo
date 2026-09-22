# Help-Wanted Oversight Dashboard

Static KPI surface for the help-wanted lane.

## Live deploy

See `docs/ops/HELP-WANTED-DASHBOARD.md` and workflow `help-wanted-dashboard-deploy.yml`.

- **Vercel:** Actions job uses `secrets.VERCEL_TOKEN`
- **GitHub Pages:** `gh-pages` branch → `https://timerloggedout-spec.github.io/termux-monorepo/`

## Local

Open `index.html` or serve the folder. Data: `data/status.json` (synced from `docs/ops/generated/help-wanted-status.json` on deploy).


## Control-surface contract (v2)

The dashboard is a projection of the Help-Wanted evidence plane. It must not become a second source of truth or an authorization boundary.

The status generator records:

- the source SHA/ref used to build the snapshot;
- every Git commit touching the registered Help-Wanted lane paths;
- whether that history is complete for those paths;
- the lane-path registry itself;
- publication surfaces and their verification expectations.

The UI renders that information as **Control surface** and **Lane evolution** sections. This makes additive work visible from lane initialization through subsequent commits instead of relying on a manually maintained timeline.

Registered paths are intentionally broad enough to catch implementation, contract, workflow, skill, and status-generator changes:

`apps/help-wanted-dashboard/`, `docs/ops/HELP-WANTED-*`, `.agents/skills/help-wanted-lane/`, `.github/workflows/help-wanted-*`, `scripts/ci/help_wanted_*`.

The surface remains read-only: operator buttons navigate to GitHub Actions/evidence/contracts; they do not embed credentials or mutate repository state from browser JavaScript.

## Verification

Run the status generator after checkout to refresh the machine snapshot, then inspect `control_surface.history_complete`, `control_surface.source_sha`, and `evolution`. Deployment must preserve those fields.
