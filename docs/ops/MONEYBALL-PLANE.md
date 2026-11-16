# MoneyBall Functional Plane — Charter

**Seat:** `[MUSEai]@{role:{moneyball-plane}}` (owner dispatch, 2026-10-28; seat created 2026-10-28, did not exist before).
**Records home:** `ops/moneyball/plane.json` (this plane's only record file).
**Scope:** explained scoring / valuation over the fleet's proposals, lanes, and passes.

## 1. What MoneyBall is

MoneyBall = a composite score that is **explainable per candidate**: per-axis values, the weights actually used, and the composite, recorded together. A bare number is not a result (`docs/rfps/temporal-durable-execution/RFP.md` §3; code pattern `ml/pipelines/moneyball/explain.py`).

Canonical axes (Oracle-pass MoneyBall), verified firsthand 2026-10-28 in `docs/rfps/temporal-durable-execution/RFP.md` §3:

| axis | starting weight |
|---|---|
| fleet-pain relevance | 0.30 |
| evidence maturity | 0.25 |
| survivability | 0.20 |
| adoption cost (inverse) | 0.15 |
| composability | 0.10 |

**Weight law:** the table above is a *starting proposal*, not a global constant. Weights are fixed **per pass at intake** and recorded in that pass's manifest (RFP §3). Any record citing MoneyBall weights must name the pass/intake they were fixed at.

**Aggregation law:** MoneyBall is reported **beside** the ballot aggregate, never merged into it (Delphi method-self-application brief, issue #1963). It separates tied candidates only where axis profiles actually differ; identical profiles stay tied — claimed separation there is invented signal.

## 2. Separation from 3L0 (hard boundary)

MoneyBall and 3L0 are **separate functional planes**: separate seats, separate records. This is not a merge.

- 3L0 plane seat: chat `c96257e5`. Its scores (Elo × role) are its own records.
- Cross-access is by **in-repo artifacts only**, never chat relays.
- Existing seam, preserved as-is: `ml/pipelines/moneyball/quota_weights.py` — quota multipliers (contract `3l0.moneyball.v1`, `docs/ops/HEX-MONEYBALL-INTEGRATION.md`) multiply a candidate's 3L0 Elo × role score; missing evidence → neutral 1.0. MoneyBall consumes 3L0 scores as *inputs*; neither plane writes the other's records.

## 3. Relation to Delphi / Oracle

MoneyBall historically lived inside Delphi/Oracle passes (Delphi lane = reference implementation). This plane **extracts the pattern**; it does not fork Delphi's ledgers.

- Delphi ledgers (`ops/delphi/ledgers.json`, issues #1487 / #1489) are read-only references from this plane.
- New passes keep their `moneyball_weighted` block in their own `pass.json`; this plane's `plane.json` indexes them and owns the axis/weight discipline.
- Telemetry-comparison lane is a consumer of the pattern, not its owner.

Pass index (verified firsthand 2026-10-28; full data in `ops/moneyball/plane.json`):

| pass | state | MoneyBall outcome |
|---|---|---|
| `temporal-durable-execution` | recorded | separated the 4-way ballot tie at 25.0: pi-core-resume 8.9 / cookbook-agent-loop 8.5 / contract-first 6.5 / serverless-skill 4.8 / versioned-autoscale 3.6 |
| `strands-rfp-response` | recorded | identical candidate profiles → stayed tied; no separation claimed |
| `delphi-method-self-application-1` | RFP #1963, not yet run | `method-v2-moneyball-required` arm makes the explained score a required second aggregation in `cross_vote` |

## 4. Not this plane's scoring

`ml/pipelines/moneyball/` (PR-triage scorer: `weights.py` — dual_gate_green 40, on_master_base 20, …; `scorer.py`; `explain.py`) is a **separate domain** that shares the name and the explainability pattern. This plane references its `explain.py` pattern; it does not own, re-weight, or re-interpret the PR-triage weights.

## 5. Consumer: challenge participant tracking

`docs/ops/CHALLENGE-SCHEMA.md` (judges/signals section, owner 2026-10-28) already declares participant tracking a **MoneyBall lane for competitions**: sourced-entity + time-series-signal + joined-view discipline applied to participants and judges.

Division of ownership:

- **Challenge-entries lane owns the records**: `ops/challenge/coordinator.json` `participants[]` / `judges[]`, append-only `signals.snapshots[]`, and the DB mirror in `ops/challenge-participants/`.
- **This plane supplies the valuation pattern**: any per-entity score over participants/judges must be explained (per-axis values + weights), with weights fixed at event intake and recorded beside the score; sourced-or-`NOT_ESTABLISHED` and append-only discipline from the schema are unchanged.
- Coordination happens on GitHub (issues/PR comments under the seat moniker), not chat relays.

Population state at charter landing (per CHALLENGE-SCHEMA.md, 2026-10-28): participants 0, judges 0, candidates 0 — no gallery has opened; entities populate on the schema's schedule.

## 6. Rules of the seat

- All work in `timerloggedout-spec/termux-monorepo`: branch → PR → merge, verified by master-history scan + landed content.
- VM is a sandbox for authoring/pushing only; no local daemons, crons, or monitors.
- GitHub access via the vault-backed PAT helper only; credentials names-only.
- Counts and scores are derived from live repo state at report time, never copied forward from dated snapshots.

**Consumer addendum (2026-10-28, coordination issue #2204):** the pattern supplied is `moneyball-plane/v2` (`docs/schemas/moneyball-score.schema.json`, validator `scripts/moneyball/moneyball_v2.py`) — NOT the `ml/pipelines/moneyball/` PR-triage scorer, whose weights are PR-domain constants (verbatim reuse refused: domain mismatch). Participant-axis starting proposal (mirrors canonical weights; fixed at **event** intake, recorded before any score): track_record .30 (signals past_wins/placements) · momentum .25 (append-only snapshot deltas) · engagement_surface .20 · composability_fit .15 · inverse_engagement_cost .10. Standout/recruitment flag requires composite ≥ the intake-fixed threshold **and** no `unverified` axis. Full mapping in `ops/moneyball/plane.json` → `consumers[0].pattern_for_consumer`. Population 2026-10-28: D1 × 1 participant (`ladder-practice-sets`), judges 0, candidates 1.

**Internal metric — win_probability (owner ruling, 2026-10-28, via challenge-entries-manager):** a MoneyBall-side metric living ONLY at `coordinator.json events[].metrics_internal.win_probability` — separate column, ADAPTIVE (recomputed in the same PR as any input change: field/score/submission), SILENT + HIDDEN (never rendered on feeds/pages/briefs/ledger; the ledger carries 1st-place gross only, no EV). Method `winprob/v1`: base = 1/field_size, lifted by our composite vs the scored field's mean (clamp 0.25–4) when both exist, else base-rate only; `field_size` NOT_ESTABLISHED → estimate null. Full spec: `ops/moneyball/plane.json` → `consumers[0].internal_metric`.

**winprob/v2 (owner critique, 2026-10-28 — supersedes v1):** v1 read as lottery probability (slots ÷ field). v2 is talent-based: the base rate is demoted to a **prior only**; the estimate is driven by **our standing** (our v2 composite percentile vs the scored-field distribution, odds-form LR), **criteria/judge fit**, and **evidence strength**. Unknowns are explicit — unscored field share + unverified-axis weight share widen an **uncertainty interval** (`estimate + range + confidence`), never silently collapsed to a point. Closed events with a recorded outcome carry the realized value (D0/Decider = 0, not_submitted — v1's 0.025 for a settled event was the clearest defect). No sourced denominator → no estimate (confidence `none`). Full spec + worked values: `ops/moneyball/plane.json` → `consumers[0].internal_metric`.
