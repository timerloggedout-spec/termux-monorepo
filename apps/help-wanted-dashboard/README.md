# Help-Wanted Oversight Dashboard

Static KPI surface for the help-wanted lane.

## Live deploy

See `docs/ops/HELP-WANTED-DASHBOARD.md` and workflow `help-wanted-dashboard-deploy.yml`.

- **Vercel:** Actions job uses `secrets.VERCEL_TOKEN`
- **GitHub Pages:** `gh-pages` branch → `https://timerloggedout-spec.github.io/termux-monorepo/`

## Pages

`index.html` (Tribute control surface), `quota.html` (quota & limits),
`matrix.html` (lane matrix), and `admin.html` — the admin control panel over
the whole web inventory: Delphic Oracle Method (live `ops/delphi/panel.json`
config, cycle stages, ledger/dispatch links), systems inventory, privileged
admin surfaces, and a live review queue fetched from the public GitHub API.
The admin panel follows the dashboard contract: read-only projection, no
embedded credentials, actions navigate to the owning admin surface.

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

## Design system

`dashboard.css` is the shared stylesheet of record for every page in this app
(tokens, nav, hero, cards, tables, pills, freshness card — see the token table
in `docs/ops/WEB-DESIGN-ASSESSMENT-2026-10-21.md`). Pages link it and keep only
page-specific rules in a small local `<style>`. Accent rule: blue = links and
navigation, gold = eyebrows / headings / freshness, ok/bad = evidence states
only. All pages carry the same primary nav (brand, Marketing, Ops · Tribute,
Lane matrix, Quota, Vercel deployment, Sitemap, Monorepo); the deploy workflow
copies `dashboard.css` alongside `matrix.html` wherever the matrix page is
published standalone.
