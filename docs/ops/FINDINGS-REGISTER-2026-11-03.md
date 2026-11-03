# Findings Register — first mining pass (2026-11-03)

One pass through the challenge-opportunity pipeline over
every current holding: the D0/D1 spec atom maps (research
cycle, PR #4549) · the NOT_ESTABLISHED register · the podium
corpus + dataset v2 (pin `2026-11-03.v2`, sha256
`3f5eedf757cce138f36b68944b082c7c8bd30ec5f79b4e07abbad7876e0b31e3`)
· the D1 field import (PR #4581, merged `acc6838dd1c1`) ·
D2 OSINT (PR #4526 + mirror spec) · quota readings + the PAT
tick ledger (cadence escalation, closed 2026-11-03) ·
lane-events/provenance corpora · the mirror baseline
(`experiments/doe/panel-judge-mirror/forecasts/
2026-11-03-d1-studysprint.json`).

Rails: nothing invented; a finding without a cited receipt
is struck, not softened. Severity is stated for the LIVE
entries (D1 freeze = Nov 4 23:59 PT; C12 round 1 = Nov 15;
D2 window to Nov 8). Routing per finding: entry-impacting →
Desk + the entry seat · system → the owning lane ·
predictive → recorded forecast, never asserted. The
register stays OPEN under the continuous-improvement
mandate; this is the first pass, not the last.

## ① GAPS

**F-G1 — D1 placements + field identities: PENDING-JUDGING.**
Evidence: D1 spec Outcomes (PR #4545) · field import (PR
#4581). Species: UNPUBLISHED-on-venue (judging Nov 5–18).
Severity (D1): LOW for the freeze itself, HIGH for
everything downstream — the dataset D1 row, mirror scoring,
and the Outcomes fill all wait on it. Route: capture leg at
the Desk; re-check on the venue's publication signal.

**F-G2 — D0 winners: NOT_ESTABLISHED.** Evidence: cycle
record D0-8 · competition import (PR #4550, merged
`2a91b916230a`) — 30 projects enumerated firsthand, ZERO
winner badges on any official surface. Species:
UNPUBLISHED-on-venue. Severity: none for live entries;
blocks dataset completeness + mirror LOEO growth. Route:
capture issue #4547 (Desk/D0 seat).

**F-G3 — GAP-J1: the D2 panel is publicly unnamed.** Evidence:
`docs/ops/PANEL-JUDGE-MIRROR.md` (PR #4584). State: mirror
for D2 is capped at VENUE-ARCHETYPE grade; no person-grade
panel can be built. Severity (D2): MEDIUM — the pre-pick
mirror read stays descriptive, never an effect estimate.
Route: DoE (mirror leg) + Recruitment (identity watch).

**F-G4 — Judge pool mostly POOL_UNRESOLVED.** Evidence:
mirror spec Inputs (RAISE pool ≈ 40 rows; Debnath · Cochrane
named). State: person-grade mirrors are buildable for a
minority of the pool; the rest cannot carry cited signals
yet. Severity: MEDIUM (systemic — caps test-③ effect
estimates fleet-wide). Route: Recruitment/OSINT (dataset
identity-gaps record, PR #4497 merged `94ef71d9`).

**F-G5 — D0 field denominator drift: 40 vs 30.** Evidence:
dataset v2 reads[] — 40 (as_of 2026-10-28, coordinator
exhaustion) ∧ 30 (as_of 2026-11-03, firsthand Load-more
enumeration), status DRIFT, cause NOT_ESTABLISHED, D0
control-set usability downgraded to PARTIAL. Severity: LOW
(closed event) but the species is live — see F-N5. Route:
Recruitment (dataset owner).

**F-G6 — Learnova-slot question: NOT_ESTABLISHED.** Evidence:
field import resolution section (PR #4581 @ `bedef6dd8a3f`)
— the bulk pass crossed our row with a same-named project;
whether that project holds a separate roster slot (field 55
vs 56) is unresolved. Severity (D1): LOW. Route: this seat,
freeze-day re-check if the Desk calls it.

**F-G7 — Strands model-access proof still OPEN (atom D1-4).**
Evidence: issue #4534 — run 1 receipt = model 404 (cured by
PR #4555's swap to gemini-3.8-flash) · run 2 receipt = 503
provider capacity on the correct model (stamped inline,
`6613255734`) · run 3 `41702122859` queued at pass time.
Severity (D1): **HIGH** — this is the live-leg proof the
mirror's platform seat prices (baseline strands_aws 7–9 of
15) and mirror re-run trigger 1. Route: this seat (runs) +
D1 seat (verdict).

**F-G8 — Provider completion routes: free-tier only.**
Evidence: issue #3141 ledger + fleet rule (MEMORY, owner
fact 2026-11-01) — funded-out permanent {huggingface ·
deepinfra · novita · friendli · zai · llm7 · routeway ·
siliconflow · deepseek(balance)} ∧ no-credential {cerebras ·
kilo · modelscope · ovhcloud · requesty · typhoon · xfyun}.
Proven live: cohere · sealion · baseten · mistral. Severity:
MEDIUM (systemic — swarm diversity is narrower than the
170-service registry suggests; §25 selection must price
this, not the catalog). Route: this seat (Swarm) + DoE.

**F-G9 — Dispatch-tree realized wake ≈ 5/day vs 144 designed.**
Evidence: cadence escalation D3 (closed 2026-11-03) — the
tree's own queue throttles its cron. Severity: MEDIUM
(systemic cadence). State: event-wake fix routed to Swarm.
Route: this seat.

**F-G10 — PAT capacity idles while work queues.** Evidence:
cadence D1 — 38.8k counted ticks; 80/151 windows at
maxused <1500 (event-shaped demand, not phase-aligned);
the 5000-wall itself is cured (QAC-007) and the per-session
blind spot is FIXED (flow governor landed in the helper,
cadence D2). Severity: MEDIUM — see F-O5. Route: quota lane
+ this seat.

**F-G11 — Release machinery ran ahead of its dependency.**
Evidence: ss runs `41699805302`/`41699815962` logs +
fix `21320fc9de0e` — the release-cut EPUB leg shipped
(17:46Z) before `export_epub` existed in any cuttable tree
(the eReader build is still PR #4521). Species:
dependency-ordering. State: FIXED (leg conditional; D1
seat PASS). Severity: was HIGH (freeze path), now LOW —
the class, not the instance, is the finding: machinery
extensions need a tree-content precondition check. Route:
this seat (release machinery).

**F-G12 — Field-recon link extraction incomplete.** Evidence:
field import rows (PR #4581) — ≈15 rows carry "link
present, URL not extracted" (sidebar links not in page
text). Severity: LOW (evidence quality; no decision rode
on an unextracted URL). Route: this seat (pipeline Stage-2
refinement, recorded in PR #4573's acceptance).

**F-G13 — D0 per-entry AppID unprovisioned; leg PAUSED at
the owner sudo gate.** Evidence: D0 sub-manager stamps
2026-11-03 (manifest POST fired; GitHub "Confirm access"
interposed; ∅ created). Severity: LOW for entries (D0 is
in upgrade maintenance), MEDIUM for the AppID family's
completeness. Route: AppID lane + owner session.

**F-G14 — CodeRoad credited runs blocked on a token.**
Evidence: certifications record (umbrella #506) —
`CODEROAD_WEBHOOK_TOKEN` placement is Provisioning's,
blocked on owner entry; both run modes are proven
(P pilot run `41512639662` · W pilot `41574262388`, both
SUCCESS). Severity: MEDIUM (64/64-by-Dec-5 trajectory
waits on it). Route: Provisioning + owner.

## ② OPPORTUNITIES

**F-O1 — The scheduling ground is empty (D1).** Evidence:
field import TAK tracks — of 15 education entries, the
only spaced-repetition algorithm named anywhere in the
field besides ours is Ladder's SM-2; the head-to-head
(SyllabusSync AI) has ZERO SR (repo code search: FSRS 0
files, "spaced" 0 files; calendar plans only). Unoccupied
ground: FSRS-grade scheduling as the named, demonstrated
core. Serves: D1 (freeze narrative + v1.0.0 update block).

**F-O2 — Deployed-on-AWS is unoccupied ground (D1).**
Evidence: field import — ≈13/55 projects name any public
endpoint; 6 run no Bedrock at all (Gemini/Ollama); the
head-to-head's "live" is Vercel + Supabase. Our webapp
release line + seam-① publish + receipted releases occupy
ground most of the field never entered. Serves: D1.

**F-O3 — Evidence discipline is the field's scarcest
feature (D1 + C12).** Evidence: field import caveats —
results across the field are pervasively self-labeled
simulated/synthetic/mocked; exactly ONE other project
(Ladder) runs a deterministic verbatim-quote gate. The
mirror baseline prices this from the other side: our
receipts are the panel's enthusiasm ("gate + release
receipts are checkable"). Serves: D1 now; C12 Receipts
Vault (Nov 15) — the same thesis as a NAS skill, already
staged (PR #4273 merged).

**F-O4 — The mirror names D1's three movable caps.**
Evidence: baseline forecast `pjm-2026-11-03-d1-studysprint`
— mean 61.7 (seats 67/57/61, spread 10, DISCRIMINATES);
caps named verbatim: "single sample course caps the
functionality demonstration" · "AWS/Strands depth reads
thinner than the criteria line rewards" (strands_aws
7–9/15) · category crowding (innovation seat 57).
Unoccupied ground BEFORE the freeze: a second demonstrable
course + the #4534 proof receipt + the #4537 schema span
are precisely the counters, and all three are in flight.
Serves: D1 (v1.0.0 content choice + mirror layers 1–3).

**F-O5 — Idle quota windows are harvestable capacity.**
Evidence: F-G10's ledger — 80/151 windows under 1500/5000
used while the dispatch tree starves (F-G9). Unoccupied
ground: phase-aligning backlog work (census · backfill ·
mirror layers) into measured idle windows needs no new
quota. Serves: the whole fleet. Route: quota lane + this
seat (pair with F-N4).

**F-O6 — Thin clusters mark future venue ground.** Evidence:
field import cluster tally — devops 1 (CloudOps Swarm) ·
climate-heat 5 with two same-name Madurai entries ·
education 15. An agent-infra/ops entry faces a field of
one in this venue family; heat is saturated and
name-collided. Serves: D2 slate picks + later entries
(archetype-grade read; advisory beside the charter).

**F-O7 — A two-venue corpus now exists.** Evidence: D0
field 30 (PR #4550) + D1 field 55 (PR #4581) + dataset v2 —
cross-venue pattern mining (template-style bodies ·
simulated-results prevalence · live-endpoint rates) is
possible for the first time. Serves: venue selection,
D2 observatory, and F-N1. Route: Recruitment + this seat.

## ③ NOVEL IMPROVEMENTS (cross-source seams only)

**F-N1 — Feature×outcome matrix: podium patterns × our
execution data.** The seam: the two-venue corpus codes
field features (live endpoint · named algorithm · tests
claimed · evidence gate · AWS-native deploy) for 85
projects; our lane-events + provenance corpora code what
each feature COSTS us to manufacture (runs, receipts,
landed PRs). The instrument: a feature×{field-rarity ×
our-cost} matrix, refreshed per import. What it would
prove: which judge-visible features are simultaneously
rare in-field and cheap for us — positioning by
construction rather than by intuition, per entry, before
its window opens.

**F-N2 — Mirror calibration as a fleet self-model test.**
The seam: the mirror baseline's probabilities (podium
0.20 · finalist/honorable 0.35 · no-recognition 0.45)
score by Brier when D1 judging closes (Nov 18), and the
layer curve (triggers: proof close · 0.2.0 green · v1.0.0)
records whether our improvements moved the modeled panel.
The instrument: the test-⑥ scoring pass, run jointly on
the mirror AND on the alignment synthesis's standing
claims about our execution. What it would prove: whether
the fleet's model of its judges — and of itself — is
calibrated, with a number, not a vibe. Predictive content
files as recorded forecasts only (DoE leg).

**F-N3 — Field-simulation ABM, assessed on the merits.**
The candidate: simulate the 55-project D1 field as agents
carrying their receipted features under the published
Rules weights (Functionality 35 · Innovation 25 ·
Strands/AWS 15 · Originality 25) to map placement
SENSITIVITY to our remaining levers (second course · proof
receipt · v1.0.0 surface state). Merits FOR: every input
is receipted (PR #4581 rows); the rubric is published;
n=55 admits near-exhaustive parameterization rather than
sampling theater. Merits AGAINST: judge behavior is the
unmodeled term — the panel is unpublished, so any judge
model is venue-archetype grade, and an ABM output dressed
as a placement prediction would violate the mirror rails.
Verdict: VIABLE as a sensitivity instrument (which lever
moves the modeled outcome most, per rubric point spent) ·
NOT viable as a predictor. Any run files as a recorded
forecast under archetype labeling. Route: DoE (forecast
leg) + this seat (feature coding from the import).

**F-N4 — Phase-aligned cadence: tick ledger × dispatch
tree.** The seam: the quota ledger's idle windows (F-G10)
and the dispatch tree's wake deficit (F-G9) are the same
hours seen from two instruments. The instrument:
event-wake routing that fires designed tranches INTO
measured idle windows, scored by realized-vs-designed
wake before/after. What it would prove: whether designed
cadence (≈144/day) is reachable with existing quota —
turning two gap findings into one closed system result.

**F-N5 — Enumeration-integrity machinery: drift × crossed
reads.** The seam: F-G5 (D0's 40-vs-30 denominator drift)
and F-G6 (the crossed StudySprint row) are one species —
two reads of one quantity disagreeing silently. The
instrument: generalize the skill's own-entry cross-check
(landed today, Stage 1) into a dataset-level dual-read
differ — every quantity entering the dataset from ≥2 reads
carries both, and a mismatch flags itself mechanically.
What it would prove: enumeration integrity stops depending
on a human noticing — the failure mode both instances
shared. Route: this seat + Recruitment.

---

*Register state: FIRST PASS, 2026-11-03. Counts: 14 gaps ·
7 opportunities · 5 novel improvements. D1-serving items
(F-G7 · F-O1 · F-O2 · F-O4 · F-N3) are routed to the Desk +
D1 seat ahead of the Nov 4 23:59 PT freeze. The register
re-opens on every material landing (mirror layers · 0.2.0
read-backs · judging outcomes) under the
continuous-improvement mandate.*

## Addendum — DoE legs (filed 2026-11-03, same pass)

Source: DoE expert seat, companion brief to this pass.
These entries extend §③; nothing above is edited.

**Alignment wire — LANDED.** PR #4588 merged `a4b4d85d0801`:
per-venue alignment layers hook at placements publication
{D0 capture #4547 · D1 judging close}; the mirror consumes
criteria-fidelity from those layers; tests ①/⑤ consume the
evidence. F-N2's instrument is therefore BUILT, not
proposed — what remains is the outcomes landing.

**F-N2 sharpened — the calibration datum.** Scored-forecast
n across the fleet today ≈ **0**: the wagering book's 23
expectation records sit INTAKE (null priors/posteriors at
open, ∅ positions); the D1 mirror baseline is the fleet's
first fully-stamped, pre-outcome, probability-bearing
forecast of record (scorable Nov 18). The novel improvement
is therefore wider than the mirror: route ALL
expectation-bearing artifacts through the recorded-forecast
machinery (filed pre-outcome · Brier/hit-rate at outcome) —
calibration becomes a measured fleet quantity within 2–3
outcome cycles instead of a rhetorical one.

**Mirror-delta reads (extends F-N2).** As each D1 layer
files (triggers ①②③ to the freeze) and the Nov 18 outcome
lands, the seam yields two reads no other instrument
produces: the IMPROVEMENT CURVE (panel-score Δ attributed
per basis term {Strands depth · sample content · surfaces}
— which improvements actually move a panel read, measured)
∧ the venue's CRITERIA FIDELITY (from the D1 alignment
layer: whether the real picks track the stated rubric or
the taste terms — feeding every future archetype panel).
Entry effort allocatable by measured panel-response per
basis term instead of by intuition.

**F-N7 — ABM equivalency rehearsal (a second ABM; do not
confuse with F-N3's field simulation).** Assessed by DoE
under equivalence-proof v0 (PR #4342): the SFI ABM
open-equivalency claim today = CLAIM-grade, honestly short
of PROVEN — leg (a) syllabus-of-record decomposition NOT
yet executed · leg (b) open-materials index partially built
(Certifications PR #4343: 5 firsthand-verified entries incl.
archived materials + Mesa/NetLogo corpora) · leg (c)
executed verification = ∅ receipts · the credential itself
GATED (tuition-card ∨ discretionary scholarship; session
archived, next run unannounced). Verdict: the LEARNING path
is walkable today at zero cost; the CREDENTIAL path is
closed until a non-card route or a live session opens. The
seam: legs (a)+(c) executed on the archived-session
materials would produce the fleet's first PROVEN-grade
equivalency at ~zero marginal cost — the equivalence
standard's cheapest full-dress rehearsal. Route:
Certifications lane + DoE.

## Pin supersession (2026-11-03)

The dataset pin cited in this register's header (v2) is
superseded: **dataset `2026-11-03.v3` · PR #4592 merged
`c95f37703568` · sha256
`f317dbf47a3636fea02e8acc1feddac41674a0c9596ddd5f632bf1b4030805fc`**
carries this register's rows (F-G6 → D1 ENUMERATED 55 with
the slot caveat in-row · F-G2 re-stamped NOT_ESTABLISHED,
superseding v2's UNPUBLISHED-on-venue wording · F-G1
confirmed · F-O7 + F-N5 in program_notes). Cite v3.
