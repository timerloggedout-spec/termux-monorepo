# Pool-Scope Methods — method citation of record for category % snapshots

Methods source: MVT seat (surface-separation lane), named alongside
DoE for the MoneyBall pool-scope program (owner via main,
2026-11-03). The rule of record: category % splits are **dynamic** —
category-usage-driven, bounded by the methods below. **No fixed %
table exists or may be created.** The program's DESIGN (MoneyBall
seat, `timerloggedout-spec/moneyball` `docs/DESIGN.md`) records the
allocation rule; these methods are its bounds. Method disputes go to
the DoE seat (census test holder).

Method id: **`pool-scope-methods/v1`**. A change to any method or
parameter below is a new method version; the backfill doctrine
applies (historical snapshots re-bounded under the new version,
compared continuously until DoE culling retires a version).

## The estimator

- Usage units are the DESIGN's usage measure of record, counted
  over a **declared window W** (start/end stamped on the snapshot).
- Category share: **ŝ_c = n_c / N**, N = Σ n_c over W (multinomial
  sampling model). A share is a measured quantity with sampling
  error — never a quota, target, or entitlement.

## The bounds (what makes a % stampable)

- Per-category bounds = **Wilson score interval at 95%** (z = 1.96)
  on ŝ_c. A snapshot % may not be presented tighter than its
  bounds; when N is small the bounds are wide, and that width is
  the discipline, not a defect.
- Joint multi-category statements (all shares at once) use the
  Dirichlet–multinomial posterior (uniform prior α = 1); bounds =
  95% credible interval per category. The snapshot's `method` field
  states which bound family was used.
- **Evidence floor:** N < 30 in W ⇒ the share is
  **NOT_ESTABLISHED** — no point % is stamped (bounds-only or
  absent). This is a method parameter of record, amendable only by
  a method version change.
- **Guardrails:** per-category floor/cap % live in the DESIGN's
  allocation rule, not here. If a realized share is clamped to a
  guardrail, the snapshot shows the pre-clamp share and bounds and
  marks the clamp — clamping is disclosed, never silent.

## Change discipline (the MVT leg)

- An allocation change is a **treatment**: it takes effect as a new
  cohort at a window boundary (never mid-window), is stamped with
  its method version, and is evaluated against the prior allocation
  on the DESIGN's outcome measure over the following window —
  sets/stop-when-conclusive per the family desk method, records in
  EXPERIMENT form under the scoring intake
  (`docs/ops/MVT-ATES-SCORING-INTAKE.md`).
- Retuning inside a window destroys the window as a unit of
  comparison; such movement is observational only.

## Snapshot stamp (required shape)

```json
{
  "at": "<ISO timestamp>",
  "window": {"start": "<ISO>", "end": "<ISO>"},
  "method": "pool-scope-methods/v1:wilson95",
  "n": 0,
  "shares": {"<category>": 0.0},
  "bounds": {"<category>": [0.0, 0.0]},
  "clamped": []
}
```

A snapshot missing `method`, `window`, or `bounds` — or stamped
below the evidence floor — is NOT_ESTABLISHED and renders as such.
