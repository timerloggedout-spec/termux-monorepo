# OWNER-REQUESTS — single register ∀ owner-bound items (fleet-wide)

Owner order 2026-10-31 (via main): ONE document ∀ owner-related requests. Lanes add rows HERE instead of piecemeal pings; main reads this file for owner summaries. Row = {item, lane, what's needed, since, blocks}. Resolved rows move to the RESOLVED section with evidence refs — ∅ deletions.

Notation: #320/#1734 — claims carry evidence refs; gaps = NOT_ESTABLISHED.

## OPEN

| # | item | lane | what's needed (owner action) | since | blocks |
|---|------|------|------------------------------|-------|--------|
| 1 | ModelScope ruling | provisioning (a78e43e6) | ruling on ModelScope route | ≤2026-10-31 | ModelScope lane activation |
| 2 | TinyFish key ⇒ Actions secret | scraping-tools (97b21d62) | signup GO + `TINYFISH_API_KEY` provisioned as Actions secret (names-only in chat) | 2026-10-30 | TinyFetch/TinySearch OSINT route (Firecrawl fallback stands) |
| 3 | Meta/WhatsApp number ruling | social-connectors (a78e43e6) | ONE owner number ruling: Meta dev-account SMS verification ∧ WhatsApp dedicated number | 2026-10-31 | Meta app verification; WhatsApp WABA setup |
| 4 | WABA payment (card rule) | social-connectors (a78e43e6) | payment-method decision under card hard-stop | 2026-10-31 | WhatsApp sending |
| 5 | X un-park | social-connectors (628089aa) | owner word to un-park X wiring (parked 2026-10-29) | 2026-10-29 | X posting route |
| 6 | Social others-scan build word | social-connectors (628089aa) | GO/NO-GO on candidates Telegram ≻ Mastodon ≻ Discord-webhook ≻ Bluesky | 2026-10-31 | those connector builds |
| 7 | Pay-first families (Anthropic/Codex) | quota | payment decision for pay-first provider families | ≤2026-10-31 | Anthropic/Codex paid lanes |
| 8 | Cerebras card | provisioning | card for Cerebras | ≤2026-10-31 | Cerebras lane |
| 9 | Omni instance | provisioning | Omni instance decision | ≤2026-10-31 | Omni route |
| 10 | ROCm #13152 | AMD (f92553f1) | direction on ROCm item #13152 | ≤2026-10-31 | ROCm work item |
| 11 | #1861 direction | repo | owner direction on issue #1861 | ≤2026-10-31 | issue #1861 |
| 12 | notebooklm pool-charge | provisioning | pool charge action for notebooklm | ≤2026-10-31 | notebooklm pool |
| 13 | action_required stock (≥2666 parked runs) | swarm (6628d41d) | per-run "Approve and run workflows" in Actions UI ∨ accept stock stays parked — forward inflow FIXED via Termux Fleet Swarm (App 5560920) + F1 adoption wave | 2026-10-31 | nothing forward; stock runs only |

## RESOLVED

| # | item | resolution (evidence) |
|---|------|------------------------|
| R1 | Swarm AppID GO + checks:write | GO 2026-10-31 16:53 PT ⇒ App 5560920 live, installation 177357774, record PR #2761 merged 36c986c39fdb (swarm-token authored+merged); F1 pilot verified PR #2763 / run 41255317900 |
