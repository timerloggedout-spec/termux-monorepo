# Web Design Assessment — Published Surfaces of timerloggedout-spec/termux-monorepo

- **Role:** fleet web-design specialist side chat (seeded from main chat, 2026-10-21)
- **Pass:** read-only inventory + design assessment (2026-10-21). Staged locally first; published to `docs/ops/` on the owner's direct order ("PUSH YOU FILES!", 2026-10-22).
- **Evidence:** every file below was read live through the vault-PAT helper (`github_pat.py get …/contents/…?ref=master` / git trees API) on 2026-10-21 ~21:45 PDT. Master head at read time: `6f4f802e` (2026-10-22T04:45:44Z, "ops(help-wanted): live status refresh"). Full recursive tree: 9,267 entries, not truncated. Counts in this document are counted from those live responses, never copied from dated docs.
- **Correction to standing memory:** the quota panel's `/quota` route is **not** an explicit rewrite in the current `apps/help-wanted-dashboard/vercel.json` — the file now carries only `/matrix` + `/lane-matrix` rewrites; `/quota` works via `cleanUrls: true`. Earlier memory ("a /quota rewrite in vercel.json") is superseded by the current file.

---

## 1. Surface map — what is actually published, and where

The repo does not publish one site. It publishes **one app through three hosts**, plus a thin project-Pages site, plus several in-repo pages that no deploy path touches.

### 1a. The Tribute app (`apps/help-wanted-dashboard/`) — three hosts, three freshness ages

| Host / URL | What it serves | Deploy path | Freshness mechanism |
|---|---|---|---|
| User site: `timerloggedout-spec.github.io/help-wanted/` (+ `/matrix/`) | Full app copy: index, quota, matrix, data/, quota.txt, robots, sitemap | `help-wanted-dashboard-deploy.yml` `user-site` job mirrors the whole app dir to the separate `timerloggedout-spec.github.io` repo (branch `main`, dir `help-wanted/`); matrix mirrored separately to `matrix/`. Verified live: that repo's tree (26 entries) contains `help-wanted/quota.html`, `help-wanted/index.html` (17,043 B, same size as master) | On push to master touching app paths / generated status JSON. Mirror **lags master**: its `help-wanted/data/status.json` is 1,223,676 B vs master's 1,358,494 B at read time |
| Vercel: projects `help-wanted-oversight`, `help-wanted-dash` (`*.vercel.app`) | Same app as site root; `cleanUrls`, `/matrix` rewrite, `/data/*` cache header (60 s), `git.deploymentEnabled: false`, path-gated `ignoreCommand` | `vercel-batch-deploy.yml` (hourly cron :23, quota-reconciled against the 100/day Hobby cap, 6 h per-project cooldown, Tribute first) for both projects; `tribute-vercel-prod.yml` is manual-only since 2026-10-20 and stamps `data/build.json` with the served SHA; the deploy workflow's own Vercel job is dispatch-only | Slowest of the three by design (quota protection). Can be hours behind master while Pages is minutes behind |
| Project Pages: `timerloggedout-spec.github.io/termux-monorepo/` | **Not the app.** Hub `index.html` + `matrix.html` + `data/lane-matrix-status.json` only (gh-pages tree verified: 18 entries) | Same deploy workflow, `pages` job → orphan `gh-pages` branch (Pages API confirms: legacy build, source `gh-pages:/`, status "building" at read time) | On push. **No dashboard index, no quota page on this host** |

Pages inside the app:

| Page | File (size) | Purpose | Data source(s) | Freshness |
|---|---|---|---|---|
| Control surface (Tribute board) | `index.html` (17,043 B, 67 lines — minified single-line style) | KPIs (9 cards), control/operator links, Tribute ledger w/ keyword+state filter, foreign open PRs, tracked evidence, lane evolution timeline, publication lanes, policy, referral credits | `docs/ops/generated/help-wanted-status.json` via raw master first, `./data/status.json` fallback, `cache: no-store` + `?t=` cache-bust | Excellent: snapshot `generated_at` 2026-10-22T04:45:23Z at read time (minutes old), 3,643 receipts; status-refresh bot commits land on master continuously (master head itself is one) |
| Quota panel | `quota.html` (13,591 B) + `quota-evidence.js` (3,023 B) | "Needs attention" alerts, 27-family provider quota-manager coverage table, provider-development note, all-services registry grouped by provider w/ filter | Registry: `ops/quota/registry.json` from raw master (live count at read time: **28 services**, 14 provider groups). Readings: `docs/ops/generated/quota-status.json` → `./data/quota.json` fallback. Coverage: `./data/provider-quota-coverage.json` (local-relative only, 60,049 B, **27 families**) | **Weakest in the app.** Readings file `generated_at` **2026-10-20T23:05:00Z** (~30 h old at read time) with only **3 readings**, none carrying `observed_at` — see Finding P0-1 |
| Lane matrix | `matrix.html` (4,079 B) | Live PR-lane board: open count + EXTRACT / CANDIDATE / NEED_EVIDENCE / SUPERSEDE counts, PR table by lane/age | `docs/ops/generated/lane-matrix-status.json` via raw master, then `./data/…`, then `/matrix/data/…` | Good: `observed_at` 2026-10-22T04:37:09Z, 46 open PRs at read time |
| Redirect stub | `lanes-and-scopes.html` (397 B) | Meta-refresh to `…/matrix/` | — | — |
| ASCII / TUI / eReader lane | `quota.txt` (10,423 B) + `scripts/quota_tui.py` (18,236 B) | Plain-text quota rendering sharing the registry/readings source | Same JSON sources as quota.html | **Stale vs its own source:** header says "**26 services**" and "No services are reporting a problem state", snapshot dated 2026-10-20T23:05:00Z; the live registry it claims to render now has **28** services. Not regenerated when the registry grew |

Supporting files: `vercel.json` (580 B — above), `sitemap.xml` (345 B, **3 URLs only**: `/help-wanted/`, `/matrix/`, and a stale `/termux-monorepo/matrix.html`; quota and hub absent), `robots.txt` (points at `…/help-wanted/sitemap.xml` — correct only on the user-site host, wrong on Vercel root), `data/status.json` (byte-identical copy of the generated status, sha `c282b9ff`), `README.md` (control-surface contract v2: projection, never a second source of truth; read-only UI).

### 1b. In-repo pages with **no deploy path** (not published, not linked from the dashboard)

| Page | File | State |
|---|---|---|
| Historical Corpus Explorer | `apps/historical-corpus-explorer/index.html` (7,280 B) + `explorer.js` (exists) | Expects `data/snapshot.json`, which **does not exist in the repo**. Page honestly renders "UNVERIFIED · awaiting snapshot" and refuses to infer zeroes. Best-behaved unpublished page |
| OPS-EVENT HITL Replay | `apps/ops-hitl-control-surface/index.html` (9,234 B) | Fetches `data/ops-hitl-events.json`, which **does not exist in the repo** — so it silently falls back to 5 hardcoded DEMO events dated 2026-09-22. If this were ever published as-is it would present demo data as a live command surface |
| Project hub | `apps/project-pages-hub/index.html` (2,981 B) | Published, but only as the project-Pages root (see 1a). 8-second meta-refresh auto-redirect to the user-site dashboard; declares itself "not the marketing site and not a second copy of the ops dashboard" |
| Demo portal | `demo-portal/public/index.html` (1,321 B) + own `vercel.json` | Separate Vercel project (`termux-monorepo` in the batch plan). Light-theme placeholder, "under construction", self-describes as a repoint away from a folder that held committed browser-profile data |
| Ecosystem architecture | `termux-ecosystem-architecture.html` at repo root (18,009 B) | Static SVG diagram, no data, no nav, no deploy path found |
| ArchWiz Markov Lab | `experiments/archwiz-markov-lane/index.html` (8,900 B) + `src/markov-engine.mjs` (exists) | Self-contained interactive experiment, no nav back, no deploy path |
| Commingle swarm web | `commingle-swarm/web/public/index.html` (378 B) | Built-app shell (bundle.js) — an application bundle, out of the published-pages scope, noted for completeness |

### 1c. The other half of the IA lives in another repo

The primary nav on index/quota points at `timerloggedout-spec.github.io/` ("Autonomous AI Employees" brand + "Marketing") — the marketing/user-site root, whose source is the separate `timerloggedout-spec.github.io` repo (root `index.html` 7,076 B + `js/content.js`). The Tribute design system therefore governs the ops subtree only; the brand-level entry point is a different codebase with its own (unreviewed in this pass) design.

---

## 2. Design coherence assessment

### What is genuinely coherent (the Tribute core)

`index.html` and `quota.html` are near-siblings, clearly one design system — "the Tribute view's" system of record:

- **Shared tokens (verbatim in both):** `--bg:#080b10; --panel:#10161f; --panel2:#0c1219; --line:#243140; --text:#edf3f8; --muted:#93a4b8; --blue:#65c7ff; --gold:#e9c779; --ok:#63d69b; --bad:#ff7b83`; radial-gradient backdrop, sticky blurred nav, 1,180 px content column, 12 px-radius gradient cards, uppercase micro-labels (0.68 rem, 0.08 em tracking), gold eyebrow (0.72 rem, 0.12 em), `clamp(1.8rem,4vw,2.8rem)` H1, pill components, `.fresh` freshness card with `aria-live`.
- **Typography:** `15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif` in both. No webfont, no external requests — fast and offline-tolerant on the user's phone.
- **Semantics:** `<nav aria-label>`, header/main/section with `aria-labelledby`, labelled filter inputs, `target=_blank rel="noopener noreferrer"` discipline, HTML-escaping in every render function. This is careful work.

### Where coherence breaks

1. **The system is copy-pasted, not shared.** Index CSS is 3,829 chars, quota's 3,221, matrix's 1,335 — the same token block and components re-typed per page, already drifting: KPI value is 1.5 rem on index vs 1.3 rem on quota; index `.grid` is `repeat(5,1fr)`, quota's `repeat(3,1fr)`; quota defines `.pill.bad/.gold/.ok` variants index doesn't have (index colours pills via separate classes); matrix drops the gradient panel, sticky nav, hero, and freshness card entirely and redefines `.card` flat.
2. **Three competing "close but not the same" palettes** sit one click apart: Tribute (above), hub (`--bg:#0b0d10`, teal accent `#4fd1c5`, Inter, 14 px radius), Historical (`--bg:#0b1118`, teal accent `#7dd3c7`, 1 rem radius, 16 px base). HITL uses a fourth abbreviation of the same idea (`--p/--p2/--l/--t/--a`, gold `#e8c56b` vs Tribute `#e9c779`). A user moving hub → dashboard → explorer crosses three accent colours (teal → blue/gold → teal) with no rule for what teal vs blue means.
3. **Typography forks:** 15 px (Tribute), 14 px (HITL), 16 px (Historical), 13 px ui-monospace (ArchWiz), all-monospace JetBrains Mono via Google Fonts (architecture page — the only external font dependency in the estate, and it renders a 1,200 px-minimum SVG). Hub names Inter but never loads it (falls back to system-ui — harmless, but the declaration is fiction).
4. **Navigation is three different navs.** Index nav: brand, Marketing, Ops·Tribute, Lane matrix, Vercel deployment, Sitemap, Monorepo — **no Quota link in the primary nav** (quota survives only as one "Quota panel" button deep in Operator links — the exact spot whose earlier loss caused the #1396 regression). Quota nav adds a Quota self-link the other pages don't reciprocate. Matrix nav has only 3 links, a non-link brand span, and no Quota/Marketing/Sitemap. Both index and quota link "Vercel deployment" to a **deployment-hash URL** (`help-wanted-oversight-8w13bl125-…vercel.app`) — a per-deploy address embedded as if it were the stable alias, while `tribute-vercel-prod.yml` itself verifies against the stable `https://<project>.vercel.app`. The root-relative `/sitemap.xml` nav link resolves to the *marketing site's* sitemap on the GitHub host and to the app's on Vercel — same link, two targets.
5. **Responsive / phone behaviour is uneven, and the primary device is a phone.**
   - Index: breakpoints at 850 px (5-col KPI grid → 2, hero/controls stack) and 520 px (nav un-sticks and wraps). Tables carry `min-width:720px` inside `overflow:auto` — scrollable, workable.
   - Quota: at 850 px its alert grid collapses 3 → **1** column (index keeps 2 at the same width — inconsistent), and its tables are the widest in the app: `min-width:820px`, including the **8-column coverage table** — on a phone that's a long horizontal pan across the densest data the user checks most. `setInterval(render, 60000)` re-renders every minute **without refetching** — the relative-time labels tick, the data doesn't; a freshness illusion.
   - Matrix: one breakpoint (800 px), no small-phone nav rule.
   - Historical is the responsive exemplar: `auto-fit minmax(190px,1fr)` grids, no fixed table minimums, `:focus-visible` outlines (the **only** page with explicit focus styling; Tribute pages rely on browser defaults).
   - Architecture page: no responsive behaviour at all — SVG `min-width:1200px` inside horizontal scroll, 2 rem padding.
6. **Information density & weight.** Index renders 9 KPI cards + 7 sections on one page and parses a **1.36 MB JSON** (`no-store`, cache-busted) on every load — on an Android phone over mobile data this is the app's dominant cost, paid before any content paints. Quota is light to load (14 KB registry + 1.5 KB readings + 60 KB coverage) but extremely long: 28 services grouped in tables **plus** a 27-row × 8-column coverage table on the same page. Density is honest (everything in scope is listed, per directive) but there's no progressive disclosure — no collapsed groups, no sticky sub-nav.
7. **Freshness UX diverges per page.** Index: relative "Xm ago" + generated timestamp + receipt count (good). Quota: "Snapshot Xm ago" (honest wording). Matrix: observed timestamp + master SHA (good). Three hosts serve three different snapshot ages for the same pages (§1a), and only the Vercel lane stamps a served-SHA (`data/build.json`); the Pages mirrors give the user no way to tell which snapshot they're looking at beyond the data's own timestamp.

### Directive compliance check (standing user directives)

| Directive | Verdict |
|---|---|
| Pages are LIVE and data-fed, never static snapshots | **Mostly met** — index/matrix fetch generated JSON from raw master with local fallback, no-store. **Exceptions:** quota readings are a 2026-10-20 historical file (self-labelled "not a live quota feed"); quota.txt is a static rendering of that same stale snapshot; HITL page is demo data by fallback |
| List everything in scope | **Met** — quota renders all 28 registry services grouped by provider + all 27 coverage families; index renders full ledger with filters. (quota.txt's "26" header breaks this in the text lane) |
| Every page linked from the published dashboard | **Partially broken** — quota is linked only via an Operator-links button, absent from primary nav; matrix is in nav; Historical, HITL, ArchWiz, architecture, demo portal are not linked from anywhere in the dashboard (and mostly not published) |
| Phone layout matters | **Partially met** — viewport + breakpoints everywhere in the app, but quota's 820 px tables and index's 1.36 MB payload work against the phone-first reality |
| Quota ASCII/TUI/eReader lanes share one data source (`data/quota.json`) | **Formally met, materially stale** — quota.txt and quota.html read the same sources, but the .txt was not regenerated when the registry went 26 → 28, so the lanes currently disagree with the registry |

---

## 3. Findings in priority order

**P0-1 — Quota "Needs attention" is dead by construction.** `quota-evidence.js` only surfaces a live state when a reading has a valid `observed_at` ≤ 15 min old, `horizon: "H0"` and `evidence_status: "confirmed"`. The published readings have **no `observed_at` field at all**, `horizon: "H1"`, `evidence_status: "attributed_claim"` — so `readingView()` returns `unknown`/`reported` for every service, the alert filter (`cap_tripped|exhausted|watch|stale|reported` — note: `reported` can appear, `unknown` cannot alert) shows essentially nothing, and the seeded `vercel.deployments = cap_tripped` — the single most operationally important state on the page — is invisible as an alert. The gate's fail-closed honesty is right; the data contract feeding it was never upgraded to match. Fix the *feed* (poller-artifact promotion publishing `observed_at`-bearing readings), or explicitly re-scope the section to "Reported evidence" with `reported` pills — do not silently weaken the gate.

**P0-2 — Extract the shared design system before adding any new page.** One `dashboard.css` (tokens + nav + hero + card + table + pill + fresh) linked by index/quota/matrix, replacing three hand-copied `<style>` blocks. Every new page (briefing included) currently means a fourth copy to drift. Static hosting makes this trivial: the deploy workflows already copy the whole app dir / serve it as root on Vercel.

**P0-3 — Unify navigation + fix the link rot.** One nav component (same links, same order, `aria-current` per page) on all three app pages, **with Quota in the primary nav**; replace the deployment-hash Vercel URL with the stable `help-wanted-oversight.vercel.app` alias; make the sitemap link host-correct; regenerate `sitemap.xml` to list `/help-wanted/`, `/help-wanted/quota.html` (or `/quota`), `/matrix/` and drop the stale `/termux-monorepo/matrix.html` entry; align `robots.txt` per host or point it at the user-site URL deliberately.

**P1-4 — Phone-first tables for quota.** Adopt Historical's patterns on the quota page: below ~640 px render coverage/services as stacked cards or priority-column tables (Service, Limit, State visible; method/reset behind the row), drop the 820 px minimum, and let the alert grid go 2-up at 850 px like index. Add `:focus-visible` outlines app-wide (lift Historical's rule verbatim).

**P1-5 — Stamp every host like Vercel does.** Emit `data/build.json` (served SHA + generated_at) in the `pages` and `user-site` deploy jobs too, and render "serving <short-sha> · snapshot <age>" in the freshness card on all three pages. Today a user comparing phone (Pages) vs desktop (Vercel) sees two different boards with no explanation.

**P1-6 — Shrink the index payload.** Split `help-wanted-status.json` into a small summary document (KPIs, counts, policy, deployments — what the first paint needs) + on-demand ledger/evidence files, or at minimum drop the redundant `?t=` cache-bust (already `cache:'no-store'`) and serve the fallback copy with the existing 60 s `/data/*` cache header behaviour in mind. 1.36 MB no-store on every phone load is the app's biggest UX cost.

**P1-7 — Regenerate quota.txt in the same job that changes the registry/readings**, and add a count check (header count must equal registry length — the 26-vs-28 drift is exactly the user's "off by one means keep checking" failure mode). Same for the TUI sample (`scripts/quota_tui.sample.txt`).

**P2-8 — Decide the orphans' fate explicitly.** Historical explorer: publish + link once a snapshot pipeline exists (its UNVERIFIED state is the honesty model to copy). HITL surface: either wire `data/ops-hitl-events.json` or add a visible DEMO banner in-page — never let the silent fallback ship. ArchWiz + architecture diagram: mark as experiments (link from a single "Labs" entry) or leave unpublished deliberately; don't let them be discovered as if they were product surfaces. Hub: adopt Tribute tokens (kill the third palette) and reconsider the 8 s auto-redirect, which rushes a phone user reading the site map.

**P2-9 — Remove quota's fake-live interval** (refetch on the 60 s tick, or delete the interval). Re-rendering stale data with fresh relative timestamps reads as liveness it doesn't have.

**P2-10 — One accent rule.** Blue = navigation/links, gold = headings/eyebrows/freshness, teal = *nothing* in the Tribute app (retire it there) or formally assign teal = evidence/provenance if Historical/HITL are adopted into the family. Write the token table into `apps/help-wanted-dashboard/README.md` next to the v2 contract so the system of record is documented, not just embodied.

---

## 4. Where a programmatic morning-briefing page would live (scope NOT confirmed — design note only)

Per main chat's note, no briefing page is to be built until scope is confirmed. When/if it is, the surface map says exactly where it belongs:

- **File:** `apps/help-wanted-dashboard/briefing.html` — inside the existing app, inheriting P0-2's shared stylesheet, the unified nav (P0-3, with Briefing added once, in the primary nav), the `.fresh` freshness card, eyebrow/hero, and pill semantics. Do **not** create a new app folder: a new folder gets no deploy path, no nav, and repeats the orphan pattern of §1b.
- **Routes it inherits for free:** user-site `…/help-wanted/briefing.html` (the `user-site` job copies the whole app dir), Vercel root + `cleanUrls` (`/briefing`) via the existing batch-deploy plan paths, sitemap addition per P0-3. **Gap to decide explicitly:** like quota today, it would **not** appear on project Pages (`/termux-monorepo/`), whose job copies only hub + matrix — either extend that job or accept user-site/Vercel-only, but decide it in the open.
- **Data contract (follow the status/lane-matrix pattern, not the quota-readings pattern):** a generator writes `docs/ops/generated/briefing.json` with `generated_at` + `source_sha`; the page fetches raw-master first with `./data/briefing.json` fallback, `no-store`, and renders age in the freshness card. Generated-content commits are the established freshness engine of this app (status refresh proves it works at minute cadence). Every claim on the page should carry its evidence state the way `quota-evidence.js` forces — briefing copy must never present an attributed report as a confirmed reading.
- **Phone contract:** single column, `auto-fit minmax` card grids (Historical pattern), no table wider than the viewport without a stacked-card fallback, first paint must not depend on a status.json-sized payload — briefing should consume the P1-6 summary document, not the 1.36 MB file.
- **Text lane:** if the briefing is programmatic, generate `briefing.txt` from the same JSON in the same job (the quota.txt lesson, P1-7: same source, same commit, count-checked), so the eReader/TUI lane can carry it without a second pipeline.

---

## Appendix — evidence index (all read live via PAT helper, 2026-10-21 PDT)

- Repo: `timerloggedout-spec/termux-monorepo`, master head `6f4f802e` (2026-10-22T04:45:44Z); recursive tree 9,267 entries; Pages API: legacy, `gh-pages:/`, html_url `…/termux-monorepo/`.
- App files: `index.html` 17,043 B · `quota.html` 13,591 B · `matrix.html` 4,079 B · `quota-evidence.js` 3,023 B · `quota.txt` 10,423 B · `vercel.json` 580 B · `sitemap.xml` 345 B · `robots.txt` 95 B · `data/quota.json` = `docs/ops/generated/quota-status.json` 1,502 B (generated 2026-10-20T23:05:00Z, 3 readings) · `data/provider-quota-coverage.json` 60,049 B (27 families) · `data/status.json` 1,358,494 B (generated 2026-10-22T04:45:23Z, 3,643 receipts).
- Registry: `ops/quota/registry.json` schema `3l0.quota-registry.v1`, **28 services** counted live.
- Lane matrix: `docs/ops/generated/lane-matrix-status.json` 34,648 B, observed 2026-10-22T04:37:09Z, 46 open PRs.
- Workflows read in full: `help-wanted-dashboard-deploy.yml` (11,523 B), `tribute-vercel-prod.yml` (4,317 B), `vercel-batch-deploy.yml` (plan + quota logic).
- Mirrors verified: `gh-pages` branch tree (18 entries); `timerloggedout-spec.github.io` main tree (26 entries; mirrored status.json 1,223,676 B — lags master).
- Other pages read in full: `apps/project-pages-hub/index.html`, `apps/historical-corpus-explorer/index.html`, `apps/ops-hitl-control-surface/index.html`, `demo-portal/public/index.html` + `vercel.json`, `termux-ecosystem-architecture.html`, `experiments/archwiz-markov-lane/index.html`, `apps/help-wanted-dashboard/README.md`, `lanes-and-scopes.html`.
