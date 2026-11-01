# live-4-dispatch-framing — dispatch framing × Nov wave (LIVE design)

`[MUSEai]@{role:{doe-mgr-live-builds}}` ⊂ doe-expert oversight

**Factor = dispatch framing** (DO-pattern levels, `docs/ops/DO-PHRASING-FRAMING-FRAMEWORK.md` §4):

- `framing-a` — pattern **A** (Implement/repair) only: `templates/framing-a.md`
- `framing-ba` — patterns **B≫A**: recon phase (B) lands before implementation (A): `templates/framing-ba.md`

Levels differ **only** in the B phase. Skeleton, acceptance-evidence
demand, stop/escalation = identical ∀ levels.

**Ride = Nov wave, zero extra quota** (recon PR #2784 concl. 2; arm
correction PR #2787): campaign creates ∅ dispatch. Blocks = projects,
arm ∀ = Jules label route:

| Block | Opens | Sequence (slots 1–8) |
|---|---|---|
| D2 | 2026-11-03 | ba a a ba · ba a a ba |
| D4 | >2026-11-08 | a ba ba a · a ba ba a |
| M2 | gated (M4) | ba a a ba · ba a a ba |
| M3 | gated (M4) | a ba ba a · a ba ba a |

Assignment binding @ issue creation; seat records size stratum
(S|M|L) **before** seeing slot; ∅ swap/re-draw; off-sequence issues =
OBSERVATIONAL, never re-labelled. Exclusions (urgent/security/
template-incompatible) logged ∧ counted.

**Stamps mandatory** ∀ dispatch ⇒ 1 EXPERIMENT record
(`records/<block>-<issue>.json`, schema `docs/ops/corpus/EXPERIMENT.schema.json`):
`treatment.arm` = level; `system_prompt_ref = prompt:<moniker>:<slug>#sha256[:12]`
(exact title+body); model/tools/phrases = `NOT ESTABLISHED` (Jules
exposes ∅; phrases SSOT = {deepseek} only) ⇒ `instance = null`,
`instance_key` ∅ fabricated.

**Primary response** = rework-free first-pass merge (merged ∧ gate
green ∧ 0 corrective re-dispatch ∧ acceptance evidence present).
Secondary: sessions-to-merge, review rounds, elapsed, scope
excursions, stalls.

**Rule (pre-registered):** ≥12 designed dispatches (≥6/level, ≥2
blocks) ∨ wave closes 2026-12-04 ⇒ adopt winner iff Δprimary ≥0.20
∧ ∅ block reversal >0.20; else `no_selection`, framing-a stays
default. Winner 🍒⛏️ cherry-picked ⇒ dispatch docs; loser culled,
records retained.

## Competing-build #1 — ChronoMancer record emission (gated)

Task: emitter `run_history` SQLite ⇒ fork + continuation as 2
schema-valid EXPERIMENT records, byte-stable re-run, source ∅ mutated.
Arms: **A = Jules** (label) × **B = Gemini** (crafted issue, #2732
route) — framing held = `framing-a` ∀ (arm = factor). DeepSeek-CI +
command-dispatch = review arms only.
Gate: arm-B shaping checklist (DESIGN.json) ✓ ∧ D2 underway.
Verdict: acceptance-pass ∧ fewer steering interventions wins;
loser culled w/ record, winner = emitter-class template.
