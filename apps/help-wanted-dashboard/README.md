# Help-Wanted Oversight Dashboard

The **Help-Wanted · with Tribute** dashboard is the live presentation layer for the contributor lane.

## Canonical surfaces

- **GitHub Pages:** `https://timerloggedout-spec.github.io/help-wanted/`
- **Repository app:** `apps/help-wanted-dashboard/`
- **Source snapshot:** `docs/ops/generated/help-wanted-status.json`
- **Tribute contract:** `docs/ops/HELP-WANTED-TRIBUTE.md`

The deploy workflow mirrors the app and current status snapshot to the user-site and can also publish the static app to Vercel.

## Evolution

The dashboard evolved in four recorded steps:

1. **Oversight origin** — static KPI/status surface (`93a0a78185a1f9450adbd06586dd080110fcc525`).
2. **Live delivery** — GitHub Pages + Vercel deployment automation (`b97bf32b2a264beaac5cc78c5abc39b759af78d8`).
3. **Freshness/backfill** — live foreign PR discovery and external-PR backfill (`bfcda8161b88b2a748774950c560bde676b496d2`).
4. **Tribute ledger** — upstream PRs became explicit contributor tributes with durable evidence (`eb808e2ce44f1ee66903d65fc75715549e2ccda8`).

The current UI makes that evolution visible instead of treating the page as a disposable status table.

## UI contract

The page is deliberately static and data-first:

- fetch the generated JSON snapshot with cache busting;
- show freshness and receipt counts;
- expose open and historical tribute attempts;
- filter tribute records locally without another API call;
- keep foreign PRs directly navigable;
- group evidence receipts by issue/PR;
- show the pipeline and operating contract;
- link the architecture back to its Git history.

Untrusted fields from the JSON snapshot are HTML-escaped before insertion into the DOM.

## Local

Serve this directory with any static HTTP server, or open `index.html` directly. The page first tries `data/status.json`, then falls back to the canonical raw GitHub snapshot.

Regenerate the source status snapshot with:

`python3 scripts/ci/help_wanted_status.py`

See `.github/workflows/help-wanted-dashboard-deploy.yml` for deployment behavior.
