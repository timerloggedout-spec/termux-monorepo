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

## Registry addendum (owner, 2026-11-01) — managers · scouts · wallets · provider wallets

| Component | State (verified 2026-11-01) |
|---|---|
| **Managers** | PARTIAL — lane managing seat = this MoneyBall seat (charter home). MSM program carries provider-family **passive quota manager contracts** (MSM-019 done, 20 canonical provider families, #1448) + Ollama balance service manager (MSM-022). A distinct "Scout Manager" seat is **not** named in `docs/ops/AGENT-MONIKERS.md` (0 hits) |
| **Scouts** | LANDED — selection surface: `docs/ops/SCOUT-ROSTER.md` + `SCOUT-MISSIONS.md`; pipeline provider catalog → normalized evidence → roster → MVT → MoneyBall/3L0 admission (`MONEYBALL_SCORED`) |
| **Wallets (participant-side)** | OPEN — ∅ wallet artifact in market/speculator/ops trees; substrate = stake units on `BetEntry` only. Per-participant internal wallet store = build item |
| **Provider wallets (market side, per provider/model)** | PARTIAL — landed as quota/balance manager contracts + `ops/quota` registry pools; no artifact named/shaped as a per-provider/model market wallet |

**Refinement to the evidence base (same-day, carrier expansion):** the MSM proposal tree (`docs/proposals/active/model-selection-market/`, outside the original hunt's carrier set) carries **Bids at design level** — DESIGN.md §6 "Bets | Wagers | Bids {Itself | Others | Job} (MSM-005)" and `schemas/bet-ledger.schema.json` ("Observational bet/wager/bid entry… Settlement does not bypass dual-gate", status `open|settled|cancelled`). No distinct bid/ask price construct exists — the bid is folded into the bet entry; **Asks remain absent at every level**. Charter component 2 status reads accordingly: Bids = design-level (proposal), not implemented in `market.py`.

## Registry addendum 2 (owner, 2026-11-01) — wallet invariant · residuals/royalties · team structures · pooled buckets

- **Wallet invariant:** every participant in this lane **has a wallet** — universal and required-by-design, not an open question. The participant-wallets component is upgraded from ∅-artifact to required-by-design; the `BetEntry` stake substrate is its seed, and the per-participant wallet store is a build item against this invariant.
- **Residuals & royalties (code → legacy):** percentage residuals/royalties are owed on optimized 'steals' | 'splits' | etc. as code passes through upgrades — cherry-picked slices/splits carry a % back to origin. State today: **OPEN** — no mechanism found (royalty = 1 noise hit; residual hits are unrelated senses). Rule registered; mechanism = build item.
- **Fees · roster · contracts for teams:** team-side structures — fees, team rosters, team contracts. State today: **PARTIAL** — team roster landed (`docs/ops/AGENT-TEAM-ROSTER.md`); team-formation contracts at proposal level (`docs/proposals/active/agent-team-formation/`); fees not found in lane/market context.
- **Pooled 🪣:** pooled buckets fund promotions · incentives · bonuses. State today: **PARTIAL** — pooled quota buckets landed (`ops/quota` allocation-plan pools); promotion/incentive/bonus funding designation not found.

## Addendum 3 — widened prior-art hunt (owner, 2026-11-01)

Carriers widened to `docs/proposals/**`, all local design exports, early MoneyBall/market docs, charter-adjacent trees:

- **Residuals/royalties:** ∅ after widened search — royalty = 0 in `docs/proposals/**`; every residual hit is an unrelated sense (graph blocked-nodes, ANOVA residual variation, residual billable cloud resources). State stays OPEN/absent.
- **Fees:** ∅ after widened search — word-level `fee` = 0 in MSM + team-formation trees; exports carry only unrelated GCP platform-fee lines. Fees stay ABSENT.
- **Team roster/contracts:** refined to **design-level** — `agent-team-formation/TEAM_CHARTER.md` carries a "Role assignment contract" (task-card + `context_manifest` contracts resolving lane/team/role/agent) and the roster model; packet state = draft / awaiting_review. Roster doc `AGENT-TEAM-ROSTER.md` landed separately.
- **Pooled buckets:** nearest prior art = MSM-020 "modern USD pools" (Ollama provider balance pools) + `ops/quota` pooled allocation buckets — both are balance/quota pools, not promotion funding. Promotion/incentive/bonus designation stays ABSENT (bonus hits = Kiroween prize context only).

## Roles (owner addendum 4, 2026-11-01)

Checked against the widened carriers before minting; the known substrate is `ActorClass {itself, others, job}`.

| Role | Definition | State |
|---|---|---|
| **Critic** | evaluates / challenges entries | ABSENT as named lane role (0 hits MSM proposal + market code); nearest substrate = trading-card role `review` |
| **Validator** | verifies settlements / records | Function landed as practice (validate_v2 · dual-gate settlement · this seat's per-record verdicts); named role ABSENT in market tree |
| **11th man** | the audience / reserve participant — crowd-side seat in the bookie/audience structure | ABSENT (owner-defined; build item tied to the open bookie/audience class) |
| Actor classes | itself (own outcome) · others (peer card, trade-only) · job (lane/job class) | LANDED — `market.py` + `bet-ledger.schema.json` |
| Card roles | triage · review · invoke · job:<id> · engine:<id>; trade actions offer/accept/revoke/settle | DESIGN/schema-level — DESIGN §7 + `trading-card.schema.json` |
| Judge | evaluation judging | Design mention only (DSPY-DOE-LANE "solvers/judges"); judging lives in challenge/Delphi contexts, not a defined MSM role |

## Registry note (2026-11-01) — components of record, Swarm seat

Per owner decision via main, recorded by `[MUSEai]@{role:{optimizations-assurance}}` (Swarm oversight seat): **Speculators manager = the optimizations-assurance seat** (multi-lane participant manager; `scripts/speculators/` + `experiments/speculators/token-strategies/`), and the **provider/model market execution side = the Swarm dispatch surface** (provider-invoke rotation + dispatch-stamp fan-out into MoneyBall v2 records; internal mechanics only). Scope guard acknowledged by that seat: no real money, stakes = observational units / soft quota tokens, #407 trading freeze untouched. No build action from that seat beyond this note until the lane tasks it.
