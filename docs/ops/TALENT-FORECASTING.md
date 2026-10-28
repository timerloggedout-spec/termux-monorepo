# Skill Talent Forecasting — design + MOAR metrics spec

Status: DESIGN LANDED 2026-10-28 (owner order: "Skill talent
forecasting … Needs MOAR!!", immediately after parking winprob for
lack of statistically significant data). Machine-readable spec:
`ops/challenge/talent_forecasting.json` (`talent-forecasting/v1`).
This document designs the method and the metrics build-out. **It does
not unpark winprob and changes no winprob method.** Collection ships
now; forecasting activates only when the signal thresholds in §3 are
crossed.

## 1. What a talent forecast is

For one entity (entrant, participant, or collaborator-class entity) in
one event context: a prediction of competitive standing in a future or
in-progress event — placement percentile and P(top-award) — produced
from explained evidence, **always** as estimate + range + confidence
(winprob/v2 discipline; never a silent point), internal-only.

## 2. Method (talent-forecast/v1) — consumes, never forks

- **Latent talent belief.** Each entity carries a Gaussian talent
  belief θ ~ N(μ, σ) (Glicko/TrueSkill family: μ = estimated skill,
  σ = uncertainty that shrinks with observations — the pattern the
  Delphi/3L0 side already uses with Elo k=16 + EWMA α 0.2; consumed by
  reference, not re-implemented here).
- **Prior.** Seeded from the entity's MoneyBall v2 composite
  (moneyball-plane/v2 record: track_record .30 / momentum .25 /
  engagement_surface .20 / composability_fit .15 /
  inverse_engagement_cost .10, weights fixed at event intake) mapped
  onto the field's composite distribution; an entity with no v2 record
  starts at the field prior with σ at maximum (cold start, §4).
- **Updates.** Each recorded outcome (placement, win, finalist,
  published judged score) updates (μ, σ) by an Elo-style step whose
  size shrinks as σ falls; judged scores enter as graded observations,
  placements as ordinal observations vs the scored field.
- **Standing.** Percentile vs the scored-field composite distribution
  (Laplace form) — the same standing block winprob/v2 defines; this
  design consumes it.
- **Forecast.** P(top-award) = prior base rate (award slots / field)
  updated by the entity's standing likelihood ratio and criteria/judge
  fit where judges are known — i.e. exactly winprob/v2's computation,
  with the standing term supplied by the talent belief instead of a
  single composite. Uncertainty: unknowns u (unscored share) and v
  (unverified axis share) → k = clamp(0.6u + 0.4v, 0.05, 0.95) →
  range [est(1−k), est(1+k)] + confidence (k<0.30 high, <0.65 medium,
  else low). Below any-signal thresholds (§3) the forecast is
  **no-signal**: estimate null, confidence none — never a number
  printed on noise.
- **3L0 consumption.** For collaborator-class entities (scouts,
  orchestrators, players), 3L0 Elo/gate-pass data is an additional
  outcome stream into the same belief, read from repo artifacts
  (weights ledger #1489, panel) per the 3L0 charter's cross-access
  rule. MoneyBall and 3L0 patterns are consumed; neither is forked.

## 3. Signal vs noise — "to be any signal" (owner addendum)

Every metric below carries `min_any_signal`: the minimum volume /
coverage at which it constitutes ANY signal at all. Below it, the
metric is recorded as **no-signal** (present in the record, value
null, never estimated). One level up, `min_usable` marks where the
metric may move a forecast. Thresholds are design constants of this
spec (set from standard practice: rating systems need repeated
outcomes before σ contracts meaningfully; a proportion at n=30 still
carries a ±~18pt 95% CI; detecting even a strong r≈0.5 correlation at
80% power needs n≈29) — they are stated so they can be argued with,
not hidden.

| Metric class | Any signal | Usable | Today (2026-10-28) |
|---|---|---|---|
| Outcomes per entity | ≥3 recorded outcomes | ≥10 | 0 — NO SIGNAL |
| Scored field per event | ≥10 v2-scored entrants | ≥30 | 1 (D1) — NO SIGNAL |
| Axis evidence coverage | ≥50% of axes verified | ≥80% | 1 record, partial — NO SIGNAL |
| Momentum snapshot series | ≥3 snapshots over ≥7 days | ≥6 | 1 per entity — NO SIGNAL |
| Engagement observations | ≥5 touchpoints/observations | ≥15 | ~0 — NO SIGNAL |
| Judge scorecards | ≥1 full panel scorecard or ≥3 judge scores | ≥3 events' panels | 0 — NOT ESTABLISHED |
| Labeled outcomes (all events) | ≥20 placements recorded | ≥50 | 0 — NO SIGNAL |
| Cross-event entities | ≥15 entities in ≥2 events | ≥40 | 0 — NO SIGNAL |

**Forecast activation (all required):** entity outcomes ≥3 AND event
scored field ≥10 AND axis coverage ≥50% for that entity. **winprob
standing feed-in (Phase 2, §5):** ≥30 scored records in an event AND
≥20 labeled outcomes in total AND ≥15 cross-event entities — then,
and only then, does an owner decision unpark winprob with talent
standing as its standing input. Until then forecasts run shadow-only.

## 4. Cold start

New entity: μ = field composite mean (or global prior when no field),
σ = σ_max; track_record axis unverified → v = 1; forecast = no-signal
until §3 thresholds cross. Returning entity: belief carries across
events (that is what the cross-event metric builds); per-event fit is
re-derived, talent is not reset.

## 5. Phasing

- **Phase 0 — NOW: collection only.** The MOAR metrics spec (§6) is
  collected by the existing surfaces (OSINT watch + scraper weekly,
  participant mirror, event-close appends). No forecasts published
  anywhere, not even Admin.
- **Phase 1 — shadow forecasts.** When per-entity/per-event §3
  any-signal thresholds cross, forecasts are computed and stored
  internal-only (Admin panel feed extension), labeled SHADOW, and
  scored against realized outcomes at each event close (calibration
  record appended — a forecast that is never graded is not a signal).
- **Phase 2 — activation.** When the Phase-2 thresholds cross AND
  shadow calibration shows ranges covering realized outcomes at their
  stated confidence, the owner decides whether winprob unparks with
  talent standing as input. Not automatic; this design does not do it.

## 6. MOAR metrics — collection spec (summary; full spec in JSON)

Per participant/entrant: `outcome_record`, `judged_score`,
`moneyball_v2_score_record`, `snapshot_series`, `engagement_observation_count`,
`project_repo_activity`, `demo_engagement`. Per event: `field_size_participants`,
`field_size_projects`, `field_scored_count`, `field_score_distribution`,
`podium_record`, `judges_named`, `judging_criteria_published`. Per
judge: `judge_identity`, `judge_affiliation`, `judge_past_panels`,
`judge_criteria_fit_axes`. Our entrant: `our_v2_score_record`,
`our_outcome_record`, `our_submission_timestamp`,
`our_qualifier_completion`. Stored in coordinator
participants[]/judges[]/podium + `ops/challenge-participants/scores/`
+ the existing Neon participant tables; snapshots append-only; every
value sourced + fetched_at; unsourced = NOT_ESTABLISHED / no-signal,
never filled in.

## 7. Visibility

Forecast outputs, when they exist (Phase 1+), are **Admin-panel-only**
via the challenge-admin-metrics feed family — never public feeds,
pages, briefs, or the opportunity ledger (which stays 1st-place gross
only, no forecast-derived EV anywhere).

— Design by the challenge-entries-manager assistant seat, 2026-10-28.
Consumes: MoneyBall plane (moneyball-plane/v2, winprob/v2 spec
PR #2250), 3L0 plane charter, challenge OSINT/scraper collection
(PRs #2234/#2244/#2248). Coordination: issue #2204.
