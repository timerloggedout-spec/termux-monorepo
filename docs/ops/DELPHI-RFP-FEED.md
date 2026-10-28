# Delphi RFP feed — contract (`delphi-rfp-feed/v1`)

Owner requirement (2026-10-27): the dashboard shows the RFP flood's
**progress & status, the criteria, the questions, the outcomes — and
renders the responses in the page**. This feed is the Delphi lane's
data contract for that page; the Web Design lane renders it. One
feed, one collector — no parallel shapes.

- **Schema:** `delphi-rfp-feed/v1`
- **Canonical file:** `apps/help-wanted-dashboard/data/delphi-rfp-feed.json`
- **Collector:** `scripts/delphi/rfp_flood_feed.py` (pure transform,
  stdlib) over a cache written by `scripts/delphi/rfp_flood_fetch.py`
- **Refresh:** `.github/workflows/delphi-rfp-feed-collect.yml` —
  dispatch + weekly + on `delphi-gate` completion; opens a refresh
  PR, never commits directly.
- **Sources:** open GitHub issues labeled `delphi:rfp` (bodies +
  labels), their gate ledger comments (`<!-- delphi-ledger v1 -->`),
  `ops/delphi/surfaces.json`, `ops/delphi/panel.json`.

## Entry shape (one per open RFP)

| Field | Meaning |
|---|---|
| `number`, `title`, `url`, `created_at` | The issue |
| `surface_id` | From the filing's form field (title fallback) |
| `group` | `surface` (in surfaces.json) · `synthetic` (unknown id) · `research-baseline` · `research-variant` |
| `status` | The gate's **award** — latest ledger decision (`parked` / `shadow` / `promoted`); pre-award, the award label; otherwise `unscored` with the gap named. `converged` is a rounds property and travels as its own boolean — 18 parked RFPs also carry the converged label, so labels alone must never be read as the award |
| `scoring_inputs` | `sourced surface` vs `synthetic unsourced surface — rubric scores from the form only (fit 3, headroom 3, horizon H2)` |
| `questions[]` | The 10 form questions (`.github/ISSUE_TEMPLATE/delphi-rfp.yml`) with the response **as filed**; an absent field is a named gap, never an empty string |
| `outcome` | From the latest ledger comment: award line + award object (decision, why, band, recheck), `effective_score` /25, converged, rounds[] (median / IQR / effective per round), trigger, input hash |
| `responses` | The panel's **signed votes verbatim** (role, score, impact, importance, veto, reason, sign-off) + the oracle line + the HindSight/ForeSight/MoneyBall records block |
| `comparison_axes` | research.* only: the three post-hoc axes, each reading `pending` until a record exists — never zero, never a gate score |
| `progress` | Raw numbers the page's progress display derives from — never a baked percentage: `stage` (`awaiting-gate` / `gate-scored`), `rounds_run` / `rounds_max` (3), `votes_cast` / `votes_expected` (panel size) |
| `parent` | Variants only: the baseline silo RFP (`number` + `surface_id`) |
| `gaps[]` | Every honest absence for this entry, named |

There is no "winning response" in the gate: the award is the outcome
and the signed votes are the responses of record. An RFP with no
ledger comment is undecided and renders as such (`status: unscored`,
`progress.stage: awaiting-gate`).

Feed-level `criteria` states the rubric once: /25 scale, up to 3
median/IQR rounds, shadow bar 15.0, the 5 panel roles (live weights
are the #1489 ledger's; panel.json is cold-start defaults), and the
cost_auditor money veto. `summary` counts are derived from the
entries at generation time.

## Segments block (additive, DoE lane)

When `ops/delphi/rfp-segments.json` is available (the fetch copies
it and `research-silos.json` into the cache), the collector emits a
feed-level `segments` block and a per-entry `segment` field — the
segmentation layer of `docs/ops/DELPHI-RFP-SEGMENTATION.md` riding
inside this one feed (no second feed, no second collector). The
block carries the class definitions (description / criteria /
questions / cycle) and one rollup per segment: member issue
numbers, status counts, gate-scored count, and — research segments
only — comparison-axes recorded/total read from the baseline's
`comparison_axes`. Rollups count members and states only; no score
is computed or averaged. Entries no rule claims land in
`segments.unassigned`, never dropped. Absent config, the block is
omitted and the v1 feed is otherwise unchanged.

## Honesty rules

1. Status comes from the gate's award and labels; an RFP with no
   ledger comment is `unscored` with the gap named — never inferred.
2. Responses are the signed votes verbatim; nothing is paraphrased
   into a new score.
3. A form field absent from a filing is an explicit gap, not "".
4. Research comparison axes read `pending` until a post-hoc record
   exists.
5. The collector REFUSES to emit a partial feed: a cache missing any
   of its four inputs fails the run instead of publishing a subset.
