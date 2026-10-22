# Quota Expansion — Gap Analysis

**Date checked:** 2026-10-20 (America/Los_Angeles) · **Status:** STAGED ONLY — not committed, no GitHub writes made.
**Rule applied throughout:** documented vendor entitlements only, URL cited per limit. Never invent a balance or a limit. Where a vendor does not publish a limit, this file says exactly that.

---

## 0. Firsthand recounts (done by the author of this file, 2026-10-20)

### 0.1 Registry — `quota_registry.json` (schema `3l0.quota-registry.v1`)

**Firsthand count: 26 entries.** Recorded count was 26 — **verified, matches.** Source: direct read of `~/workspace/termux-monorepo/quota_registry.json`, entries counted one by one.

| # | id | provider |
|---|---|---|
| 1 | github.actions.minutes | github |
| 2 | github.actions.cache | github |
| 3 | github.api.github_token | github |
| 4 | github.api.user_token | github |
| 5 | github.artifacts.retention | github |
| 6 | github.copilot.free | github |
| 7 | vercel.deployments | vercel |
| 8 | vercel.build_time | vercel |
| 9 | render.pipeline_minutes | render |
| 10 | render.instance_hours | render |
| 11 | render.bandwidth | render |
| 12 | render.postgres_free | render |
| 13 | render.keyvalue_free | render |
| 14 | neon.compute | neon |
| 15 | neon.storage | neon |
| 16 | neon.egress | neon |
| 17 | neon.realtime | neon |
| 18 | openrouter.free_models | openrouter |
| 19 | gemini.api_free | google |
| 20 | g4f.vendors | gpt4free/CLIProxyAPI/Chapito/ai-manus |
| 21 | grafana.cloud_free | grafana |
| 22 | supabase.free | supabase |
| 23 | turso.free | turso |
| 24 | upstash.free | upstash |
| 25 | cloudflare.d1_queues | cloudflare |
| 26 | partners.credits | CellCog/Polsia/Manus |

Distinct provider strings: 13. Providers in the registry with **no** corresponding connected service in §0.2: render, neon, grafana, supabase, turso, upstash, cloudflare, gpt4free, partners — the registry is weighted toward deploy/data free tiers, not toward the user's actual connected tooling. That inversion is the main finding of this analysis.

### 0.2 Connected / tooling surface

**Firsthand counts (filesystem, 2026-10-20):**
- (a) **System connectors: 63** — `ls /opt/hatch/connectors/` (was recorded as 63 — verified, matches). Catalog existence ≠ connected.
- (b) **Custom connectors: 2** — `ls ~/workspace/custom-connectors/`: `custom.github-pat`, `custom.jules`.
- (c) **Services recorded as connected 2026-10-20: 20** — GitHub, Dropbox, Replit, Tailscale, Notion, Google Drive, Google Calendar, Gmail, Google Sheets, Google Tasks, Google Docs, Todoist, Vercel, Figma, Linear, Canva, Zoom, Meta Business Manager, Lovable, Klaviyo. (The Google bundle is 6 distinct APIs; counted as 6 of the 20.) Plus the 2 custom-connector services as tooling: GitHub (already in the 20) and Jules (not in the 20 — additional).

**Coverage verdict:** Of the 20 connected services, only **GitHub** and **Vercel** have registry entries for the service actually connected, and **Google** has an entry only for Gemini AI (`gemini.api_free`) — none for the 6 Workspace APIs connected. **17 of 20 connected services are entirely absent from the registry; 2 more (Vercel, GitHub) are partially covered; Jules (custom tooling) is absent.** Gap sections below: 19 full gaps + 2 partial-coverage expansions = **21 sections**.

---

## 1. Gap sections — Google Workspace APIs (all ABSENT; `gemini.api_free` does not cover these)

> Model-change warning (official pages, fetched 2026-10-20): current Google quota pages use **per-minute quota units / requests plus a daily billing threshold**. Older circulating figures (Gmail 1B units/day, Drive queries-per-100-seconds, etc.) were **not** found on the current official pages — do not carry them forward.

### 1.1 Gmail API
- **Limits:** 1,200,000 quota units/min/project; 6,000 units/min/user/project; 80,000,000 units/day/project (labelled "Daily billing threshold", cannot be increased). Per-method costs documented (e.g. `messages.send` = 100, `messages.list` = 5).
- **Reset:** per-minute windows; daily threshold over a 24-hour period; no midnight reset stated.
- **Source:** https://developers.google.cn/workspace/gmail/api/reference/quota (developers.google.com mirror)
- **Suggested ids:** `google_gmail.api_quota_units` (limit 1200000, unit quota units, window minute/project), plus per-user and daily-threshold variants.
- **Confidence:** Official docs, checked 2026-10-20.

### 1.2 Google Calendar API
- **Limits:** 10,000 requests/min/project; 600 requests/min/user/project; 1,000,000 requests/day/project (daily billing threshold, cannot be increased).
- **Reset:** per-minute sliding window; exceeding returns 403/429 `usageLimits`.
- **Source:** https://developers.google.cn/workspace/calendar/api/guides/quota?hl=en
- **Suggested id:** `google_calendar.api_requests` (10000 req/min/project).
- **Confidence:** Official docs, 2026-10-20.

### 1.3 Google Drive API
- **Limits:** 1,000,000 quota units/min/project; 325,000 units/min/user/project; 400,000,000 units/day/project daily billing threshold; separately 1 TB/day/project egress threshold on the same page (record both, do not merge). Per-method costs: `files.get` 5, `files.list` 100, download 200.
- **User-side:** upload/copy cap 750 GB/day/user; max file 5 TB; free account storage "up to 15 GB" shared across Drive/Gmail/Photos — https://support.google.com/googleone/answer/9004014?hl=en
- **Reset:** 750 GB cap — no further uploads until 24 hours have passed.
- **Source:** https://developers.google.cn/drive/api/guides/limits?hl=en
- **Suggested ids:** `google_drive.api_quota_units`, `google_drive.upload`, `google_drive.storage_free`.
- **Confidence:** Official docs + official help center, 2026-10-20. Note: **no queries-per-100-seconds limit is published** on the current page.

### 1.4 Google Sheets API
- **Limits:** read 300/min/project and 60/min/user/project; write 300/min/project and 60/min/user/project. No daily limit while within per-minute quotas.
- **Reset:** per-minute, refilled every minute; 429 on exceed.
- **Source:** https://developers.google.com/workspace/sheets/api/limits
- **Suggested id:** `google_sheets.api_read_requests` / `google_sheets.api_write_requests`.
- **Confidence:** Official docs, 2026-10-20.

### 1.5 Google Docs API
- **Limits:** read 3,000/min/project and 300/min/user/project; write 600/min/project and 60/min/user/project. No daily limit published on the page.
- **Source:** https://developers.google.com/workspace/docs/api/limits
- **Suggested id:** `google_docs.api_read_requests` / `google_docs.api_write_requests`.
- **Confidence:** Official docs, 2026-10-20.

### 1.6 Google Tasks API
- **Limit:** 50,000 queries/day — vendor's own wording: "a courtesy limit of 50,000 queries per day." No per-minute/per-user quota is published for this API (do not substitute Cloud Tasks, a different product).
- **Reset:** "per day"; no reset time stated.
- **Source:** https://developers.google.com/tasks/pricing
- **Suggested id:** `google_tasks.api_queries` (50000, queries/day).
- **Confidence:** Official docs, 2026-10-20.

---

## 2. Gap sections — productivity / dev tooling

### 2.1 Notion API — ABSENT
- **Limits:** per-connection 180 requests/min (Free/Plus and all non-Business/Enterprise plans; avg 3/sec) and 600 requests/min (Business & Enterprise; avg 10/sec), per 60-second window. Per-workspace limit exists but **vendor does not publish a numeric value** for it. Free workspaces with >1 member: 1,000 lifetime blocks (paid/single-member Free: unlimited; 3-day grace, then HTTP 403 on block-creating writes).
- **Reset:** window reset ≤60 s via `Retry-After` (per-workspace can be longer).
- **Sources:** https://developers.notion.com/reference/request-limits ; https://developers.notion.com/reference/workspace-block-limits
- **Suggested ids:** `notion.api_rate_per_connection` (180, requests/min), `notion.workspace_blocks_free` (1000 blocks).
- **Confidence:** Official docs, 2026-10-20. Note: supersedes the older flat "3 req/sec" description — it is now plan-tiered.

### 2.2 Dropbox API — ABSENT
- **API rate limit: vendor does not publish exact rate limits.** Verbatim: "While Dropbox does not publish exact rate limits, these limits are *not* designed to inhibit normal applications." Limits are per-authorization; HTTP 429 `too_many_requests` always carries `Retry-After` (seconds); rate-limited requests themselves count toward the limit. Registry entry must be `unpublished / handle 429 + Retry-After`, not a number.
- **Other documented:** `/files/upload` for files under 150 MB (larger via upload sessions); batches up to 1,000 entries.
- **Storage:** Basic (free) = 2 GB, 1 person, up to 3 devices — the informal "2 GB?" assumption is confirmed.
- **Sources:** https://www.dropbox.com/developers/reference/data-ingress-guide ; https://www.dropbox.com/en_GB/individual
- **Suggested ids:** `dropbox.api_rate` (limit null, unpublished), `dropbox.storage_basic` (2 GB).
- **Confidence:** Official docs/pricing, 2026-10-20. (Dropbox Sign API limits are a different product — excluded.)

### 2.3 Linear API — ABSENT
- **Limits:** API key 2,500 requests/hour/user (all keys for a user share); OAuth app 5,000/hour/user; unauthenticated 600/hour/IP. Complexity budget separate: 3,000,000 points/hour/user (API key), 2,000,000 (OAuth), 100,000/IP (unauth); single query max 10,000 points, hard-rejected.
- **Reset:** leaky bucket, constant refill; `X-RateLimit-Requests-*` headers, reset = UTC epoch ms; exceeding = HTTP 400, GraphQL code `RATELIMITED`.
- **Free plan:** 250 issues, 2 teams, 10 MB file upload, unlimited members.
- **Sources:** https://linear.app/developers/rate-limiting ; https://linear.app/pricing
- **Suggested ids:** `linear.api_requests` (2500 req/hour/user), `linear.api_complexity`, `linear.free_issues` (250).
- **Confidence:** Official docs High; Free-plan figures Medium (pricing table text fetched collapsed, values in Free-column sequence), 2026-10-20.

### 2.4 Todoist API — ABSENT
- **Limits (only Sync limits are published on the current official page):** partial sync max 1,000 requests/user/15 min; full sync max 100/user/15 min; max 100 commands/request (a 100-command batch counts as one request). Also on the page: POST body 1 MiB, headers 65 KiB, processing timeout 15 s.
- **Not published:** no separate REST per-minute limit was found on the official page checked — do **not** import third-party figures (e.g. "450/min") into the registry.
- **Source:** https://developer.todoist.com/rest/v2/
- **Suggested ids:** `todoist.sync_partial_rate` (1000/15 min/user), `todoist.sync_full_rate` (100/15 min/user), `todoist.api_rate_rest` (null, not published).
- **Confidence:** Official docs, 2026-10-20 (High, including for the absence).

### 2.5 Figma API — ABSENT
- **Limits (in effect as of 2025-11-17 per vendor; per-minute, leaky bucket, tier × seat × plan-of-the-resource):** Tier 1 (file/nodes/image GETs) Dev/Full seats: Professional 10/min, Organization 15/min, Enterprise 20/min; View/Collab up to 20/month. Tier 2: 25 / 50 / 100 per min (Prof/Org/Ent), View/Collab up to 5/min. Tier 3: 50 / 100 / 150 per min, View/Collab up to 10/min. Starter-plan resources can be far lower (vendor example: a Starter file limited to 6 requests/month even for a Full-seat holder elsewhere).
- **Reset:** leaky bucket; HTTP 429 with `Retry-After` + `X-Figma-Plan-Tier` / `X-Figma-Rate-Limit-Type` headers.
- **Source:** https://developers.figma.com/docs/rest-api/rate-limits/
- **Suggested ids:** `figma.api_rate_tier1` / `tier2` / `tier3` (plan-parameterised — no single number exists).
- **Confidence:** Official docs High, 2026-10-20. Third-party summaries quoting 15/50/100 for Professional do **not** match the official table as fetched (10/25/50).

---

## 3. Gap sections — comms, marketing, platforms

### 3.1 Zoom API — ABSENT
- **Limits (account-level, shared across the account's apps, by plan):** Light APIs Free 4/sec + 6,000/day; Pro 30/sec; Business+ 80/sec. Medium Free 2/sec + 2,000/day; Pro 20/sec; Business+ 60/sec. Heavy Free 1/sec + 1,000/day; Pro 10/sec; Business+ 40/sec (Pro/Business+ heavy + resource-intensive share a combined daily cap: 30,000 / 60,000 per day). Resource-intensive Free 10/min + 30,000/day. Meeting/webinar create/update: 100 requests/day/user, resets 00:00 UTC.
- **Source:** https://developers.zoom.us/docs/api/rate-limits/
- **Suggested ids:** `zoom.api_light`, `zoom.api_medium`, `zoom.api_heavy`, `zoom.meeting_create_update` (100/day/user).
- **Confidence:** Official docs High, 2026-10-20.

### 3.2 Canva (Connect APIs) — ABSENT
- **Limits:** no single global Connect API limit is published; limits are per-operation, per user of the app, per minute — Get design 100/min, Get design export job 120/min, Get asset upload job 180/min, Create design autofill job 60/min.
- **Free plan: not verified** — the official pricing page could not be read in this run (returned an unsupported-client page); no Free-plan figure is entered. Do not import third-party Canva Free figures without a successful official fetch.
- **Sources:** https://www.canva.dev/docs/apps/rest-apis/reference/designs/get-design/ ; https://www.canva.dev/docs/apps/rest-apis/reference/exports/get-design-export-job/ (plus canva.dev reference pages for the other two)
- **Suggested ids:** `canva.connect_get_design` (100 req/min/user), etc.; `canva.free_plan` (null, not verified 2026-10-20).
- **Confidence:** Official docs High for the two opened pages, Medium for snippet-only pages, 2026-10-20.

### 3.3 Klaviyo API — ABSENT
- **Limits (per account, fixed windows — burst = 1 s, steady = 1 min; tier assigned per endpoint):** XS 1/s + 15/min; S 3/s + 60/min; M 10/s + 150/min; L 75/s + 700/min; XL 350/s + 3,500/min. Endpoint overrides exist (e.g. Create/Update Profile steady is 750/min, not 700). Global payload limit 5 MB.
- **Reset:** `RateLimit-Reset` header (seconds to window reset); 429 carries `Retry-After`. OAuth apps get a separate quota per installed app instance; private-key integrations share the account quota.
- **Source:** https://developers.klaviyo.com/en/v2024-10-15/docs/rate_limits_and_error_handling
- **Suggested id:** `klaviyo.api_rate` (tier-parameterised, e.g. tier_m = 10/s burst, 150/min steady).
- **Confidence:** Official docs High, 2026-10-20.

### 3.4 Meta Business Manager / Graph API — ABSENT
- **No fixed universal calls-per-hour number exists by design** — limits are formula-based over rolling windows, throttled on `call_count` / `total_cputime` / `total_time` percentages via `X-App-Usage` / `X-Business-Use-Case-Usage` headers. Documented formulas: Platform (app token) 200 × Number of Users per rolling hour; Pages BUC 4,800 × Engaged Users per rolling 24 h; Ads Insights Standard 600 + 400×Active ads − 0.001×User Errors per hour, Advanced 190,000 + 400×Active ads − …; Ads Management Standard 300 + 40×Active ads/hour, Advanced 100,000 + 40×Active ads/hour; Instagram BUC 4,800 × Impressions/24 h; WhatsApp Business Management 200/hour/app/WABA default, 5,000/hour with ≥1 registered number. User-token call value is explicitly not revealed (privacy).
- **Reset:** rolling windows, no calendar reset; BUC header gives `estimated_time_to_regain_access` in minutes.
- **Source:** https://developers.facebook.com/docs/graph-api/overview/rate-limiting/
- **Suggested id:** `meta.graph_api_platform` (limit null — formula `200 * users`/hour; record the formula, not a number).
- **Confidence:** Official docs High, 2026-10-20.

### 3.5 Lovable — ABSENT
- **Limits:** Free — 5 build credits/day (daily grants cap at 30/month) + 20 Cloud credits/month + 4 AI-feature credits. Pro ($25/mo, $21 annual) — 100 base credits/month + 5 daily. Business (from $50/mo) — 100 base credits/month. Enterprise — custom, no fixed number published.
- **Reset/expiry:** daily build credits expire end of day, no rollover; monthly plan credits expire 2 months after issue; top-ups last 12 months. Plan Mode = 1 credit/message; Default Mode varies by task complexity.
- **Sources:** https://lovable.dev/pricing ; https://lovable.dev/guides/lovable-vs-vercel-platform-comparison-guide
- **Suggested ids:** `lovable.free_build_credits` (5/day, 30/month cap), `lovable.pro_credits` (100/month).
- **Confidence:** Official vendor pages High (plan amounts via Lovable's own guide page — the pricing page's plan-card table did not extract), 2026-10-20.

### 3.6 Replit — ABSENT
- **Starter (free):** 1 free published app (link goes down after 30 days); daily Agent credits up to a monthly cap — **vendor does not publish the numeric credit amounts** on the pages checked; production database storage 1 GiB. Current pricing page shows no Starter card (Core/Pro/Enterprise only).
- **Paid reference:** Core $20/mo — $20 toward models, up to 30 chat hours and 60 projects on Free Mode; Pro $100/mo — $100 toward models, 10 parallel agents.
- **Sources:** https://replit.com/pricing ; https://docs.replit.com/billing/plans/starter-plan
- **Suggested ids:** `replit.starter_published_apps` (1), `replit.starter_prod_db_storage` (1 GiB), `replit.starter_agent_credits` (null — amount unpublished).
- **Confidence:** Official pricing/docs High, 2026-10-20.

### 3.7 Tailscale — ABSENT, NOT VERIFIED
- **API rate limit: none found in official docs** in this run — treat as not published on the pages found.
- **Personal (free) plan device/user limits: NOT VERIFIED 2026-10-20.** The official pricing page fetch failed, and third-party citations of it conflict (older: 3 users / 100 devices; newer: 6 users / unlimited user devices / 50 tagged resources). **No value is entered** — this needs a successful official-page fetch before any registry value is set.
- **Attempted source:** https://tailscale.com/pricing
- **Suggested ids (unpopulated):** `tailscale.personal_users`, `tailscale.personal_devices`, `tailscale.api_rate` — all null / not verified.
- **Confidence:** None claimed — explicit gap, 2026-10-20.

### 3.8 Jules API (custom connector `custom.jules`) — ABSENT
- **API rate limit: no API-specific quota is published** on the Jules API documentation (the only numeric limit there is max 3 API keys at a time) — https://developers.google.com/jules/api
- **Plan task limits ARE published (product limits, not an API rate limit — do not re-label):** Free 15 tasks/rolling 24 h, 3 concurrent; Google AI Pro 100/day, 15 concurrent; Google AI Ultra 300/day, 60 concurrent. At the limit, new tasks block until the rolling window frees; limits are not pooled across family plans.
- **Source:** https://jules.google/docs/usage-limits
- **Suggested id:** `jules.tasks_free` (15 tasks/rolling 24 h, 3 concurrent).
- **Confidence:** Official vendor page High, 2026-10-20. **Trap flagged:** a stale beta-era mirror (`jules-documentation.web.app`, 5 tasks/day, 2 concurrent) contradicts the official page — do not use it.

---

## 4. Partial-coverage expansions (service present, quota surface incomplete)

### 4.1 Vercel — present (`vercel.deployments`, `vercel.build_time`), expansion sourced
Documented Hobby values **not** in the registry: Fast Data Transfer first 100 GB/month; Fast Origin Transfer first 10 GB/month; CDN Requests first 1,000,000/month; Function Invocations first 1,000,000/month; Active CPU 4 CPU-hrs/month; Provisioned Memory 360 GB-hrs/month; Projects max 200; Concurrent deployments 1. Hobby overage rule (documented): no billing cycle — exceed a cap and the feature pauses until 30 days have passed (Web Analytics resumes after 7 days); Hobby cannot buy additional usage.
- **Sources:** https://vercel.com/docs/limits ; https://vercel.com/docs/plans/hobby ; https://vercel.com/pricing
- **Suggested ids:** `vercel.fast_data_transfer` (100 GB/month), `vercel.function_invocations` (1000000/month), `vercel.cdn_requests`, `vercel.projects` (200).
- **Confidence:** Official docs High, 2026-10-20.

### 4.2 GitHub — present (6 entries), expansion sourced
Documented **secondary rate limits not in the registry**: max 100 concurrent requests (REST + GraphQL shared); 900 points/min REST, 2,000 points/min GraphQL (GET/HEAD/OPTIONS = 1 pt, writes = 5 pts); 90 s CPU per 60 s real time; content creation generally ≤80/min and ≤500/hour. Vendor caveat: secondary limits are "subject to change without notice" and there is no way to check their status.
- **Source:** https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
- **Suggested id:** `github.api.secondary_limits` (limit null — composite; record components in the note).
- **Confidence:** Official docs High, 2026-10-20.

---

## 5. Staleness flags — **7 flags**

**Verified NOT stale first (so they are not re-litigated):** GitHub REST 5,000/hr user token and 1,000/hr `GITHUB_TOKEN` per repo — MATCHES (docs.github.com, 2026-10-20). GitHub Actions cache 10 GB/repo — MATCHES as the default/included value (configurable upward, chargeable beyond 10 GB — not a hard cap). Render 500 pipeline min/mo, 750 instance hrs/month, 5 GB bandwidth — MATCHES all three (render.com/docs/free + render.com pricing/article, 2026-10-20). Vercel deployments 100/day and build time 45 min/deployment — MATCHES (vercel.com/docs/limits, page updated 2026-09-16). OpenRouter free-model tiers 50/day (< $10 lifetime credits) and 1,000/day (≥ $10) — MATCHES (openrouter.ai/docs, updated 2026-10-10).

| Flag | Entry | Issue | Current documented value + source |
|---|---|---|---|
| F1 | `openrouter.free_models` | **Incomplete:** registry `limit` is null with no numeric tiers, and the documented per-minute cap is missing entirely | 50/day (<$10) / 1,000/day (≥$10), **plus 20 requests/min in both tiers** — https://openrouter.ai/docs/api_reference/limits |
| F2 | `github.artifacts.retention`, `neon.realtime`, `supabase.free`, `turso.free`, `upstash.free`, `cloudflare.d1_queues` | **Unverified sourcing (6 entries):** each entry's own `source` field says "reported by Platform201 Planning Queue 2026-10-19 (not re-fetched)" — none was re-verified against vendor docs in this run either | Unchecked 2026-10-20 — schedule a vendor-doc re-fetch per entry before relying on any number in them |
| F3 | `github.copilot.free` | **Unverified:** registry itself records limit null / reset "unverified" / "numeric caps not stated on the fetched page" | Still unresolved 2026-10-20 — no numeric Copilot Free cap sourced in this run |
| F4 | `gemini.api_free` | **Null limit:** per-model RPM/TPM/RPD recorded as null with no values; not re-fetched in this run | Unchecked 2026-10-20 — vendor page: https://ai.google.dev/gemini-api/docs/rate-limits |
| F5 | `g4f.vendors` | **Unmetered/unknown by construction:** no vendor documentation exists for the wrapped endpoints; 429 observation is the only signal | No documented value exists to check against — flag is permanent until a vendor publishes terms |
| F6 | `grafana.cloud_free` | **Partially verified:** registry itself notes the free-tier monthly series/log/trace allowances were "not verified on a fetched page"; only the 10,000 samples/s ingestion rate is sourced | Unresolved 2026-10-20 — vendor page: https://grafana.com/docs/grafana-cloud/cost-management-and-billing/understand-your-invoice/usage-limits/ |
| F7 | External trap (not a registry entry) | **Stale Jules mirror:** `jules-documentation.web.app/usage-limits` still shows beta limits (5 tasks/day, 2 concurrent) that contradict the official page | Official current: 15 / 100 / 300 tasks per rolling 24 h — https://jules.google/docs/usage-limits — never source Jules limits from the mirror |

---

## 6. Second tier — catalog-available, not connected (no sections researched)

The remaining 43 system-connector catalog entries (63 total − 20 connected) — e.g. Slack, Spotify, Stripe, Shopify, Plaid, Asana, Calendly, OpenTable, Duffel, Ticketmaster, Zapier — are **not** gaps against connected usage. Per the brief, they are a second tier: add registry entries only when a service is actually connected, using the same vendor-doc-only rule. Three catalog entries map to Google APIs already covered above (gmail, google_calendar etc. are separate connector dirs for the same 6 Workspace APIs in §1).

## 7. Recommended registry additions, in priority order

1. `jules.tasks_free` — the steering lane actually consumes this daily; currently invisible to the panel.
2. `vercel.fast_data_transfer` + `vercel.function_invocations` — the deploy cap already bit once; bandwidth/invocations are the next caps to trip silently.
3. `google_gmail.api_quota_units`, `google_drive.api_quota_units`, `google_sheets.api_write_requests` — the Workspace APIs the connectors exercise most.
4. `notion.api_rate_per_connection`, `linear.api_requests`, `todoist.sync_partial_rate`, `figma.api_rate_tier1` — dev-lane APIs with hard 429 behaviour.
5. `openrouter.free_models` fix (F1): set the tiered daily limits and add the 20/min cap.
6. `dropbox.storage_basic`, `klaviyo.api_rate`, `zoom.api_heavy`, `meta.graph_api_platform` (formula), `lovable.free_build_credits`, `replit.starter_published_apps`.
7. Re-fetch queue (F2): the 6 "not re-fetched" entries, one vendor page each.
8. Tailscale: retry the official pricing fetch before entering anything.
