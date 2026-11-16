# fb-pages-mvt-1 — VERDICT CHECKLIST

`[MUSEai]@{role:{doe-mgr-marketing-live}}` · campaign `fb-pages-mvt-1` ∈ DoE family
SSOT: `DESIGN.json` (this dir) · `README.md` · `records/snapshot-fb-{a,b}-2026-10-31.json`
Doctrine: live = real responses ∨ ∅ verdict · interim snapshots ≠ winner evidence · DESIGN rule governs.

## 1. Rule-fire test — BOTH checked, EITHER fires

- [ ] `redemptions_total_attributed (started arms only) ≥ 10` — source: `rotation_log` + replenishment ledger, `config/referral_programs.json#ab_test`, attribution `?ch=fb-a|fb-b|fb-c`
- [ ] `date ≥ 2026-11-10` — DESIGN `decision_rule.window_closes`
- Verbatim rule: `winner copy => default for all channels at 10 attributed redemptions or 14d`
- ∄ fire ⇒ ∅ verdict, ∅ winner claim, continue window-1 records only.

## 2. Data assembly (marketing lane `81cbe17c` ⇒ `SUMMARY.json` from `SUMMARY.template.json`)

- [ ] per-arm ∀ started arms: `{views, clicks, redemptions_attributed, window{opened, closes, observed_at}}`
- [ ] primary = redemptions/cell · secondary only: FB insights `apps/help-wanted-dashboard/data/fb-traffic.json` ∘ landing traffic-feed
- [ ] ∀ number traces ↦ evidence_ref (file/post/ledger entry) · ∀ null in template filled ∨ explicitly `NOT_ESTABLISHED`
- [ ] copy/page identity == `DESIGN.instance_stamps` (fb-a page `1403768132822477`, fb-b `1368017223068543`, copy sha256 refs)

## 3. Started-arms-only evaluation

- [ ] window-1 verdict evaluates fb-a + fb-b ONLY (both `live`, started `2026-10-27`)
- [ ] fb-c excluded from window-1 numerator ∧ denominator ∧ ranking

## 4. fb-c late-arm handling

- DESIGN deviation verbatim: design stays 3 arms; late fb-c start = late arm w/ own start stamp; ∅ retro-pool into window 1.
- [ ] if fb-c started: record own `started` stamp + own window in SUMMARY; evaluate in its own late-arm window, ¬ window-1 verdict
- [ ] if still `arm_not_started` @ fire: record as excluded, reason `FB new-Page limit; owner retries`

## 5. Winner determination

- [ ] winner = highest `redemptions_attributed` among started arms @ fire
- [ ] tie ∨ `0` ∀ started arms @ date-close ⇒ winner `NOT_ESTABLISHED` — DESIGN carries ∅ tiebreak ⇒ escalate ↑ `doe-expert (44bb4068)`, ∅ invented tiebreak, ∅ views/clicks substitution (secondary ≠ primary)

## 6. Propagation — winner ↦ default

- [ ] winner copy ⇒ default ∀ channels (marketing lane executes)
- [ ] record propagation as 🍒 cherry-pick design event in campaign records: `{winner cell, copy ref+sha256, fired_by, fired_at, rule text verbatim, SUMMARY ref}`
- [ ] cherry-pick record landed in campaign dir PR (same PR as verdict memo ∨ linked PR# cited in memo)

## 7. Verdict memo (this lane, same-turn on SUMMARY landing)

- [ ] verify SUMMARY vs DESIGN verbatim rule + §§1–5 above, firsthand re-read of evidence refs
- [ ] verdict memo PR in campaign dir: `{fired_by, totals per started arm, winner ∨ NOT_ESTABLISHED, fb-c disposition, propagation record ref}`
- [ ] report ↑ doe-expert same-turn: PR# + merge SHA oracle-verified (master-history scan + landed content), ¬ API merge response alone
