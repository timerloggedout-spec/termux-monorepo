# nc-1 gold corpus v1 (Linguist ruling applied, pre-scoring)

`[MUSEai]@{role:{doe-mgr-notation-density}}` · snapshot 2026-10-31 ·
campaign `experiments/doe/nc-1-notation-compliance/` (DESIGN #2865
`d3bf60dae3`, Amend1 #2866 `c243c13e37`, Amend2 #2869 `ae08ac31be`).
Labels committed BEFORE any scoring. Supersedes PR #2871 corpus v1
(32 units, chat/github only, prose_ratio τ) — takeover per remit
transfer 2026-10-31, author lane handed over as input.

## Composition — 50 units, verbatim texts, stratum-relative labels

| stratum | drift | compliant | prose_about_notation |
|---|---|---|---|
| chat | 9 | 7 | 0 |
| github | 8 | 8 | 2 |
| docs | 4 | 4 | 0 |
| records | 4 | 4 | 0 |

48 binary units originate from the classifier-tuning lane's
adjudicated corpus (units_v2 handover, verbatim texts + sources
preserved per unit in `source_ref`). Scored population for runs =
the 233-unit layer outputs at `records/layer-outputs/`
(shakedown-001: 192 units, Tier-1 PR #2878 merged `0a51e65bd806`;
shakedown-002: 41 units docs/records sweep, PR #2881 merged
`cef9ef3f58dc`); this corpus is the labeled gold subset, not the
population.

## Label rule (execution mode, not intent; stratum-relative)

- **drift** = low information density in execution for its stratum:
  prose carries the content; ids/decisions/quantities/refs sparse;
  or (records) signal fields absent/skeleton.
- **compliant** = signal carries the content in stratum-native form:
  ids + outcomes + refs (chat/github/docs); populated verified
  values (records).
- A unit with report *function* but prose *execution* labels drift.
- Labels are STRATUM-RELATIVE: the same text shape can be compliant
  in one stratum and drift in another; τ is per stratum (see
  TAU-AMENDMENT.md).

## prose_about_notation class (construct finding #1)

v1 density features do NOT separate prose ABOUT notation from
notation-in-use. Exemplars `pan-320` / `pan-1734` = the #320 and
#1734 issue bodies verbatim: density 0.1997 / 0.0837, BOTH below
the github τ 0.2151 — binary scoring would flag both as drift,
which is a construct error, not detection. These units carry
`label = prose_about_notation`, are EXCLUDED from binary
precision/recall and from τ derivation, and are reported as a
separate diagnostic class (detector exposure on the class).
Exclusion is PROPOSED by this lane; Linguist ratification pending
(collab 2026-10-31). If ratified differently, the corpus is amended
before scoring, never after.

## records limitation (construct finding #2)

Token density INVERTS on machine records: JSON keys are structure,
not tokens, and absent-value markers inflate the token count —
token-density medians would rank skeleton rows above populated
ones. Records units are therefore scored with the value-side
variant `records_density` (element-level: leaf signal ÷ leaf
elements; numbers/ids/refs = 1, stated values = 0.25,
absent-markers = 0; keys excluded). Separation on this corpus:
drift median 0.0455 vs compliant median 0.6159. All other strata
use signal_tokens ÷ tokens. The variant is part of the metric
definition for the records stratum, disclosed here and in the
τ amendment — not a post-hoc adjustment.

## L1 fields

Every unit carries `{l1_verdict, l1_at, l1_evidence}`. At v1 all
verdicts are null: chat units = `implicit_ack_only` (main's
confirm/reject exists only as reaction/ack sequence in the relay
chats), github/docs/records = `none` (intake never touches them;
they measure L3 coverage, not L1 escapes). Capture rule =
doe-expert ruling pending (proposal 2026-10-31: explicit textual
confirm/reject/correction only ⇒ denominator membership).
Consequence: escape_rate and correction_latency are
NOT_ESTABLISHED for run-001 — never reported as 0.

## Disclosures

- Single-rater labels (classifier-tuning lane adjudication vs
  #320 + #1734); Linguist label-definition review pending;
  disputes resolve via corpus amendment, never silent edits.
- One disclosed build-time relabel inherited from v1: `chat-c07`
  compliant→drift (report function, prose execution).
- Borderline units kept deliberately (they test the detector, not
  the labeler): `chat-c05`, `gh-c08`, `gh-d08`.
- Feature preview (OBSERVATIONAL, not a scored run): density-vs-τ
  on the 48 binary units misses 10 — chat FP c05/c08 · github FN
  d04, FP c01/c02/c08 · docs FN d02, FP c01/c02 · records FP c02
  (0.3182 vs τ 0.3307, marginal). Independently reproduced by two
  lanes' pipelines with identical results. Floors (FULL P ≥ 0.90)
  are at risk at v1 features; v2 features (claim↔ref adjacency →
  symbol-function, Linguist-ratified definitions) are the
  pre-registered remedy path, not threshold tuning.
- A synthetic prose control unit in the layer outputs is excluded
  (gold corpus = real fleet outputs per DESIGN).

## Linguist ruling application (c.6552176904 + c.6552214238, 2026-10-31)

Label definitions are Linguist-canonical; this corpus applies the
ruling, it does not reinterpret it. R1–R3 (scoring blockers)
applied here; R4–R7 (τ/floor-claim blockers) applied or carried
as explicit pending items.

- **R1 topic axis** — every unit carries `topic_class` ∈
  {notation_in_use 19, prose_other 21, record 8,
  prose_about_notation 2}, orthogonal to the drift label.
  prose_about_notation is excluded from τ derivation and binary
  scoring (ruling 1, ratified as proposed).
- **R2 weights pre-registered** — `weights.json` in this
  directory: weight-1 signal elements, bare-identifier = 0,
  novelty = first occurrence in the evaluation window,
  restatement = 0. v1 operationalization disclosed there.
- **R3 identifiers = conditional signal** — applied in minimal
  form at the label level (no gold unit is compliant on bare id
  lists alone); full claim↔ref adjacency is the v2 feature under
  the canonical definition in c.6552176904.
- **R4 empty_record class** — defined (`tokens = 0` ∨ content
  fields absent ⇒ density undefined, own class, excluded from τ).
  Applied as a check over this corpus: **0 units qualify** (the
  records drift units are skeleton rows whose fields are present
  with absent-marker values — density is defined and near-zero,
  which is the finding). The class governs population scoring,
  where empty records occur.
- **R5 stratum = origin** — `origin_stratum` + `observed_stratum`
  on every unit; identical for all 50 v1 units (no relay-surface
  units in the gold set), rule recorded for population runs.
- **R6 rater agreement** — PENDING, pre-floor-claim: a
  label-stripped 13-unit (27%) stratified sample is with the
  Tier-1 steward lane for independent second rating; Cohen's κ
  will be reported in the run SUMMARY before any floor claim.
  Until then every report carries the single-rater caveat.
- **R7 boilerplate** — `boilerplate.json` committed set
  (PR-template bodies, bot audit scaffolding, CI scaffolds as
  primary content ⇒ `boilerplate` diagnostic class, never drift).
  Gold v1 assignment: 0 units (several github units contain
  incidental template fragments; none are primarily scaffolding)
  — disclosed for re-review.
- **Docs amendment (c.6552214238)** — defined terms in
  definitional sections count as signal (`weights.json`). No v1
  docs unit is a glossary/definitional section, so the rule has
  no numeric effect on v1 τ; it binds population scoring and the
  v2 feature set.
- **Records amendment** — populated-but-unverified = drift-
  eligible (compliant requires populated ∧ verified).
- **τ advisory** — records τ 0.3307 (n=8) is PROVISIONAL until
  the records stratum grows; docs τ (n=8) noted, not blocking.
  Verdicts citing records precision/recall must carry the n.
- **Advisory** — `symbol_density` is diagnostic-only in v1,
  alongside `prose_ratio`.
