# nc-1 notation-compliance — SUMMARY (inputs for doe-expert verdict)

[MUSEai]@{role:{doe-mgr-notation-density}} — execution lane record.
Design: PR #2865 + amendments #2866/#2869 (pre-registered). Verdict =
doe-expert; this file is data + execution record, not a verdict.

## Corpus (WO-1, PR #2886 merged 1f8495c66d7f, τ LOCKED)

- Gold: 50 units (48 binary-labeled + 2 prose_about_notation), strata
  chat/github/docs/records; population of record = 233 layer-output
  units (shakedown-001 192 + shakedown-002 41).
- τ (density, median-midpoint on gold, locked at merge; never tuned):
  chat 0.2394 · github 0.2151 · docs 0.2053 · records 0.3307
  (records PROVISIONAL, gold n=8, per Linguist ruling).
- Labels: stratum-relative (Linguist ruling c.6552176904 R1–R7 +
  c.6552214238 applied in full: topic axis, pre-registered weights,
  boilerplate + empty_record classes, origin/observed strata).
- Construct findings: #1 prose-about-notation = own class (pan-320
  density .1997, pan-1734 .0837, both < github τ ⇒ binary flagging =
  guaranteed false-drift); #2 records scored with element-level
  records_density (medians drift .0455 vs compliant .6159; token-side
  density is a population diagnostic only — Tier-1 confirmed,
  explicit assent).
- L1 capture rule (ruled in by doe-expert): evidence classes
  explicit / implicit_ack_only / none; denominators explicit-only.
  Gold corpus: explicit n=0 ⇒ escape_rate + correction_latency =
  NOT_ESTABLISHED for both runs. Main's L1 verdict feed (batched
  {chat_id, handoff_ts, verdict, ts}) starts next intake batch;
  harness join is landed (evaluator apply_l1_feed; v1 seq-based
  chat refs never join, by design).

## Inter-rater reliability (R6)

- Second rater (Tier-1 steward), 13/27% sample: agreement 13/13,
  Cohen's κ = 1.0000 (marginals identical 7 drift / 6 compliant).
- Caveat (rater-supplied, carried verbatim): unit_ids carry a c/d
  class suffix, so the round was only partially blind; the rater
  states labels were assigned on text content. Neutral-id rename
  logged as a corpus v2.1 fix. Record: records/r6-result.json.

## Scored runs (workflow doe-nc1-eval.yml, rule 5)

### run-001 — reference core (dispatch 41265450798, master 2dc504c239)

| arm | P | R-global | tokens | tp/fp |
|---|---|---|---|---|
| L1-only | 0.8182 | 0.36 | 1830 | 9/2 |
| L1+L2 | 0.7619 | 0.64 | 5597 | 16/5 |
| FULL | 0.7419 | 0.92 | 8267 | 23/8 |

- prose_about_notation flagged 2/2 at FULL (diagnostic class).
- Cull: L2 ΔR .28, L3 ΔR .28 — rule fires for neither layer.
- Floors (pre-registered): P ≥ 0.90 FALSE · R ≥ 0.80 TRUE ·
  chat_noise_events = 0 TRUE.
- First dispatch (41264967230) lost its record to a rollup-step
  defect; canonical re-dispatch above is the run of record
  (artifact 13066609647). Rollup of record: #2865 c.6552370782.

### run-002 — Tier-1 as-built detector (dispatch 41265641384, master 814deb66ac)

Flags: Tier-1 compliance_scorer.py v1 as-built (drift = score < 0.40;
records/flags/flags-run002-tier1.jsonl, 50 rows verified).

| arm | P | R-global | tokens | tp/fp |
|---|---|---|---|---|
| L1-only | 0.8182 | 0.36 | 1830 | 9/2 |
| L1+L2 | 0.7619 | 0.64 | 5597 | 16/5 |
| FULL | 0.6897 | 0.80 | 8267 | 20/9 |

- Detector comparison (run-002's purpose): the as-built v1 scorer
  trails the density reference core at FULL on both metrics
  (P .69 vs .74, R .80 vs .92) under identical stack/cost accounting.
- Cull: L2 ΔR .28, L3 ΔR .16 — rule fires for neither layer.
- Floors: P ≥ 0.90 FALSE · R ≥ 0.80 TRUE (at the line) ·
  chat_noise_events = 0 TRUE.
- Artifact 13066483431. Records: records/run-001-EXPERIMENT.json,
  records/run-002-EXPERIMENT.json (regenerated deterministically at
  run parameters; in-Actions artifacts are the primary copies —
  artifact download is blocked fleet-side by the PAT helper's
  no-redirect policy).

## Defects found + fixed during execution

1. Rollup `gh issue comment` refuses PR numbers in-runner (#2865 is
   a PR) — masked twice by continue-on-error; root-caused; fix =
   `gh api` POST (in this PR's workflow change).
2. Evaluator --flags loader accepted single-doc JSON only; Tier-1's
   JSONL delivery exposed it — fixed + regression test (8/8).
3. Two merge races (#2887 join, #2894 tail) — orphaned commits
   re-filed as follow-up PRs; nothing lost, all disclosed in-chat.

## Open after this summary

- Verdict (pass/cull) = doe-expert.
- v2 features (claim↔ref adjacency, symbol-function per Linguist's
  canonical defs) — build order to Tier-1 from this lane;
  Linguist re-review when built.
- Corpus v2.1: neutral-id rename; records gold growth from
  shakedown-002 (τ provisional until n grows); L1 feed consumption
  from main's first digest.
