# Opportunity Cycle — prep-first self-eval loop (#5096)

Design of record for the repo-internal Opportunities loop. Authority:
issue #5096 (owner order 2026-11-10 04:11 PT) + addendum comment
6767147459 (adaptive submission requirements). Build filing: #5103.
Implementation: `scripts/opportunities/opportunity_cycle.py`, driven by
`.github/workflows/opportunity-cycle.yml`.

## What the loop does

Per run, for ALL live opportunities in `ops/challenge/coordinator.json`
(events whose status is not `closed`; candidates whose status is not
screened-out), the cycle executes the challenge_opportunity_pipeline
shape end-to-end and stamps receipts:

1. **Ingest (Scouts)** — one ingest record per opportunity
   {id · kind · name · state · source: coordinator.json ·
   source_sha256 (of the source record) · ingested_at · slug ·
   osint_snapshot ref · podium_dataset ref}. Absent cross-references are
   stamped `NOT_ESTABLISHED`, never fabricated.
2. **QUE priority stamp** — per opportunity: next_gate (the soonest
   governing instant in the coordinator record: judging_end / winners_at
   / deadline / final_due / preliminary_due / submission_deadline /
   reg_close / build_end / proposal_due), days_to_gate, and a
   deterministic score with its basis spelled out. Rank is ascending
   next_gate; `NOT_ESTABLISHED` gates rank last. The stamp carries a
   `priority_timebox` {wall · landing · cushion · escalation · final} —
   taken verbatim from `ops/challenge/desk-feed.json` where the entry
   carries one, else derived by the stated offsets {landing = wall−24h ·
   cushion = wall−72h · escalation = wall−12h · final = wall−30m}.
   Stamps publish to the QUE feed surface
   `ops/que/feeds/opportunity-priority.json`
   (schema `que.opportunity-priority/v1`). QUE previously prioritized
   Actions runs only; this is the opportunity-level stamp.
3. **Prep gate (Stages 0–4 + census)** — fail-closed; see below.
4. **Delphi selection** — prep-complete entries only; see below.
5. **Stages 5–7** — post-gate only: S5 pins the podium dataset
   {path · version · sha256} and folds the entry's
   `ops/agentic-gambling/book/challenges-book.json` subjects and
   settlements VERBATIM (an INTAKE state stays INTAKE, never 0), citing
   the opportunity-ledger rows; S6 reads the latest Panel Judge Mirror
   forecast naming the entry {file · forecast_id · stamp · headline
   scores}, with any re-run recorded `specified_not_run` (the cycle runs
   no inference); S7 stamps the outcome receipt, or PENDING with the
   blocker named when the outcome is not yet knowable.
6. **Tier actions** — {delphi_selection · stage5_fold · stage6_read ·
   stage7_stamp}, each timestamped. The cycle never executes an external
   submission; it stamps readiness only.

## Prep gate rules (the prep-first invariant)

An entry's prep is verified against its prep manifest,
`entries/<slug>/prep-manifest.json`
{schema `opportunity-prep-manifest/v1` · stages {"0".."4":
{artifact, receipt_ref}}}; slug resolves from the coordinator id
(exact lowercase, else the id-prefixed entries directory, e.g.
D1 → `d1-studysprint`).

- Stages 0–4: each manifest artifact must exist on disk; the cycle
  stamps {path · sha256 · size} as the stage receipt. A missing
  manifest or artifact makes that stage `NOT_ESTABLISHED` with the gap
  named.
- Stage 0 additionally requires a row naming the event in
  `ops/challenge/opportunity_ledger.json` (read-only; its
  opportunity-cost semantics are not repurposed — the cycle keeps its
  own ledger) or coordinator registration with dates+prizes populated,
  and a resolvable priority_timebox.
- Census: `entries/<slug>/submission-requirements.json` must satisfy
  the census rules below.
- `prep_complete` ⇔ all stages receipted ∧ census PASS. Otherwise the
  verdict is `PREP_INCOMPLETE`, stages 5–7 are recorded
  `blocked_prep_incomplete`, and `tier_actions` is empty — fail-closed,
  no exceptions. A tier step on incomplete prep (or incomplete census)
  is a defect by construction: the machinery cannot emit one.

**Ordering invariant:** every tier action stamps ts > the gate's
`prep_verified_at`. Stamps come from a monotonic clock (each stamp is
strictly later than the previous), the invariant is asserted in code,
and test (a) pins it — this is the prep-before-tier proof
(done-evidence ③ of #5096).

## Submission-requirements census (addendum 6767147459)

Per entry, at prep time, every submission requirement is enumerated in
`entries/<slug>/submission-requirements.json`
{schema `opportunity-submission-requirements/v1` · requirements[]}
with each row:

- `class`: `automatable` | `fleet-executable` | `owner-hand`.
- owner-hand rows require `capacity_verified: true` — capacity is
  verified firsthand BEFORE the item may be stamped owner-gated
  (HITL-false-flag doctrine).
- every non-automatable row requires `route_around.sought: true` with
  an `alternative` (or `none_found` recorded) — alternatives are
  priority.
- every row carries its own `landing_time`, which must fall at or
  before the entry's priority_timebox wall — a gate's landing time is
  set at prep time, never discovered at cushion.
- submit-once rows (`submit_once: true`) are first-send-critical: once
  discharged, the row requires `first_send_verified: true`
  (receipt-verified at first send).

## Census inheritance — Coach check ④

The per-entry census file, `entries/<slug>/submission-requirements.json`,
is the inheritance surface for Coach check ④ (submission-gate
readiness). When the Coach seat is seated, its check ④ reads this
census rather than re-enumerating requirements: the enumeration,
classification, capacity verification, route-around, landing-time, and
first-send-verification state of record are the census rows exactly as
the prep gate validated them. A Coach finding that contradicts a census
row is resolved by correcting the census (a new validated state), never
by maintaining a second enumeration.

## Delphi selection

"Delphi selection" had no pre-existing named surface in this repo; this
loop defines it on the pattern of record — `scripts/delphi/gate.py`'s
transparent rubric panel (no model ballots, no provider calls) plus
`method_cycle.py`'s honesty rule. For each prep-complete entry, the open
completion legs {tournament-update · moneyball-update · osint-refresh}
are scored 1–5 on {evidence_recency · gate_proximity · completeness}
from cycle data by stated arithmetic, and the selection receipt records
{candidates · scores (with completeness inputs) · selected · method:
"rubric-panel (delphi-gate pattern)"}. Every leg's execution is
recorded `specified_not_run` with its reason: the cycle stamps the
selection; execution rides the entry's own lane. Nothing here cites a
phantom Delphi-selection surface.

## Outputs

- `ops/opportunities/cycles/<cycle_id>.json` — schema
  `opportunity-cycle/v1`: {cycle_id · run_id · started_at ·
  finished_at · ingest[] · priority_feed_ref · opportunities[]
  {priority_stamp · prep_gate {evaluated_at · verified_at · stage
  receipts 0–4 · census verdict · gaps} · selection · stages 5–7 ·
  tier_actions[] · verdict: COMPLETE | PREP_INCOMPLETE} · doe_stamp
  {task_class: opportunities-cycle · arm: repo-machinery · provider:
  github-actions · model: null · run_id · outcome · cost_class:
  actions-free}}.
- `ops/opportunities/cycle-ledger.jsonl` — one appended line per cycle.
- `ops/que/feeds/opportunity-priority.json` — the QUE priority feed.

The workflow runs on schedule (daily 13:17 UTC), on workflow_dispatch,
and on pushes touching the coordinator, entries, or the cycle script;
it mints a Swarm App token before checkout (que-feed-collect pattern)
and commits outputs only on change. The cycle window is the Actions
run: no chat-side steering occurs inside it (done-evidence ④).

## Seed data

D1 (StudySprint) is the only entry whose prep is fully receipted today;
its manifest and census ship with this machinery under
`entries/d1-studysprint/`. Expected first-cycle shape on master: D1
COMPLETE (Stage 7 PENDING — the placement outcome is not yet knowable)
and C12/C13/D5 et al. PREP_INCOMPLETE with named gaps. That is the gate
working as designed, not a failure.

## Companion fix

`.github/workflows/project-task-dispatch.yml` — the intake job
condition gains a body-heading match
(`contains(github.event.issue.body, '### Task / spec')`) so exact-form
filings route regardless of label/title keying (the silent-skip defect
class of #5096's own intake). Parser validation and intake-incomplete
stamping remain the fail-soft gate.

## Tests

`tests/test_opportunity_cycle.py` pins: (a) complete prep ⇒ COMPLETE ∧
tier ts ordering · (b) census missing ⇒ PREP_INCOMPLETE ∧ no tier
actions · (c) owner-hand without capacity_verified blocks · (d)
non-automatable without route_around blocks · (e) landing_time after
wall blocks · (f) screened-out/closed excluded from ingest · (g)
priority ascending by next_gate, NOT_ESTABLISHED last · (h) missing
artifact ⇒ NOT_ESTABLISHED named, never fabricated.
