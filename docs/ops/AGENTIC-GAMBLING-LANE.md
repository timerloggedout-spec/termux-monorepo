# Agentic Gambling Lane — Charter

**Seat:** `[MUSEai]@{role:{moneyball-plane}}` (chat cd195597-0afb-4c62-afc2-111fdfcdba66) — lane home per owner decision 2026-11-01.
**Machine registry:** `ops/agentic-gambling/lane.json` (`agentic-gambling-lane/v1`).

## Scope guard (hard)

Internal market mechanics over **inference and challenge outcomes only**. No real money, no external wagering, no real-money instruments. Stakes are observational units or soft quota tokens (`unit_kind ∈ {observational, soft_quota_token}` — the only kinds `MarketGraph.place_bet` accepts). The **#407 trading freeze is untouched and out of scope** — this lane is not the trading lane and does not thaw, route around, or reinterpret it.

## Components (registered as one lane)

| # | Component | Home | Status (evidence-based, 2026-11-01) |
|---|---|---|---|
| 1 | MoneyBall winprob + scoring | `ops/moneyball/plane.json` · `docs/ops/MONEYBALL-PLANE.md` | Scoring LIVE: `moneyball-plane/v2` records populated from routed dispatches (pass `swarm-routing/v2`, validated per record). winprob/v2 implemented (PR #2250 spec, #2251 implementation) — method work PARKED by owner 2026-10-28 until statistically significant data exists |
| 2 | Model Selection Market (inference implementation) | `scripts/model_selection_market/` | PARTIAL: Offers LANDED (`TradingCard.offer_trade`, `market.py` MSM-005); observational bets LANDED (`BetEntry`, `MarketGraph.place_bet`). **Bids/Asks OPEN** (absent — build items). **Bookie / audience-participation class OPEN** (absent — participation substrate = `ActorClass {itself, others, job}`; no bookmaker role, no odds-setting side) |
| 3 | Speculators (multi-lane participant) | `scripts/speculators/` · `experiments/speculators/token-strategies/` | LANDED as participant implementation (strategies + evaluation); participates in this lane's markets as a bettor class |
| 4 | Bets of record | `scripts/model_selection_market/market.py` (`BetEntry`) · `ledger.py` (`PerformanceLedger`) | PARTIAL: bet entries are the record shape; `MarketGraph` is a stub (in-memory) — durable bets-of-record store = build item |
| 5 | Repo-local CSV ledger | (to be created under this lane) | OPEN: verified ABSENT 2026-11-01 — local scan (99 CSVs) and in-repo census (7 CSVs, tree-recursive) contain no {Offers · Bids · Asks · settlements} ledger. Registered as a build item: CSV ledger for offers/bids/asks/settlements over inference outcomes |

## Evidence base (owner-pointer verification, 2026-11-01, firsthand)

- **Perplexity design export** (owner upload behind issue #2206): betting reference schema present — `bookmaker_id`, `decimal_odds`, `wager` as separate entity, `accepted_odds`, point spread, stake/EV worked math, "estimating whether an offered price is favorable". Framed as reference system / design proposals.
- **Export implementation status:** decision-opportunity record IMPLEMENTED (v2, PR #2207) · five separated quantities IMPLEMENTED in schema / PARTIAL population (live values null = unidentified) · point-in-time semantics IMPLEMENTED (PR #2207, live-conformant) · scouting evidence layer PARTIAL (per-axis evidence_refs live; fuller layer = separate Scout pipeline) · portfolio marginal contribution OPEN (schema key only).
- **Bid/Ask constructs:** absent from export, market tree, #2206 thread, and charter docs (word-level search; API hits were substrings).
- **Complexity-explorer URL:** not found in any carrier (export, #2206, plane docs, market tree; repo-wide exact-phrase search = 0). Recorded as unresolved owner pointer, not reconstructed.
- **Issue #2206** research verdict: OPEN (intake seed + implementation results on thread; independent research verdict not landed).

## Rules of the lane

- A bare number is not a result: every market/scoring artifact carries its evidence (per-axis refs, point-in-time stamps) per the MoneyBall v2 record discipline.
- Scores sit **beside** any ballot aggregate, never merged (`beside_never_merged`).
- Rule 9 applies to consumption: actor-weighting consumes only corroborated attribution; single-leg marks are held out of weights and flagged.
- Backfill doctrine applies at every scoring/method version change: full history re-scored, audited, versions compared until DoE culling retires a version.
- Stakes vocabulary is closed: observational units and soft quota tokens only. Any proposal touching real value is out of scope by charter, not by discretion.
