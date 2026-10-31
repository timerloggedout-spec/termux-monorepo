# Data Ingestion — brief surface

One source, one purpose, read-only. The brief schema mirrors the Web
Adapter Foundry Target Brief (`.github/ISSUE_TEMPLATE/target-brief.yml`,
SSOT example `ops/web_adapter_foundry/examples/target-brief.example.json`).

- Form: `.github/ISSUE_TEMPLATE/data-ingestion.yml` (label `data-ingestion`)
- SSOT example: `ops/data_ingestion/examples/data-ingestion.example.json`
- Routes: the scraping-tools lane's primary-verified set (2026-10-29/30) —
  firecrawl-keyless, tinyfish-search, tinyfish-fetch, crawl4ai-selfhost,
  twscrape, scrapling, apify, zenrows — or `auto-map`.
- Rules baked into the form: read-only (writes refused); credential routes
  are Actions-secret NAMES only, never values; `large` volume means
  automate-under-slice only (manual-browser route refused); harvests run
  via repo tooling, with the browser as a recon/verify surface; quota
  slice of record `github:scraping-tools`.
- First consumers: challenge OSINT page-watch / coverage refresh,
  field-size scrape, challenge-entry discovery sweeps.
- Intake (leg 2, not yet live): an event-triggered workflow mirroring
  `.github/workflows/target-intake.yml` — validates scope + authorization,
  refuses out-of-scope / write / credential-value briefs, maps
  (source x purpose x volume_class) to a route, and comments the dispatch
  plan on the issue. Until intake lands, briefs are triaged by the
  challenge-entries lane; the form promises no automation before it exists.
