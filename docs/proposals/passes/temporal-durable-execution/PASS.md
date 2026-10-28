# PASS — temporal-durable-execution (Oracle Method, full cycle)

**Status:** recorded — full cycle ran 2026-10-27. **Brief:** the frozen
G0 intake (`brief.json` here verbatim; RFP + RECON + INTAKE at
`docs/rfps/temporal-durable-execution/`, PR #1867 merged `74c5b5d3`,
intake PR #1886 merged `87208e49`; tracking issue #1885). The
generator-form adaptation used for the run is recorded as
`pass-brief.json` (variants given suffix/concept/plan per the cycle-v2
plan floor; every frozen parameter — n=5, variant ids, seed sets,
declared suites, expectations, MoneyBall weights — carried verbatim).
Candidates registered **#46–#50** (`author: oracle-method`).

**Environment of record:** self-host Temporal dev server (CLI 1.9.1,
Server 1.32.0) on this VM, Python SDK in a venv — remote-first, no
device, no Cloud/AWS/GCP account (card rule), no vendoring, names-only.

## The cycle

| Stage | Outcome |
|---|---|
| Generate | n=5 candidate packs under `docs/proposals/active/` |
| Cross-vote round 1 | LOCAL_BASELINE only (HUMAN_COLLABORATOR 0, MODEL_PROVIDER 0 — no recorded ballots supplied; stated, not filled) |
| Expectations | BRIEF:temporal-recon-lane priors from INTAKE.md (V1>V2>V4>V3>V5), recorded pre-implementation |
| Facilitator feedback | `SYNTHESIS.json` issued from round-1 rationales, dissent preserved |
| DEBATE / revision | `specified_not_run` — no revision ballots supplied; callable, not automatic |
| Implementation | All declared suites run or receipted as attempted (below) |
| Evidence equalization | One bundle, sha256 `8d67dc032692…`, stamped on round 2 |
| Cross-vote round 2 | Ran on the equalized bundle |
| Calibration | Below; appended to ledgers #1487 + #1489 |

## Round 1 — a near-tie on profiles

LOCAL_BASELINE weighted scores: pi-core-resume **23.654**,
contract-first **23.654**, serverless-skill **23.654**,
versioned-autoscale **23.654**, cookbook-agent-loop **23.077**. Four
candidates tie; the recorded order among them is the comparator's
alphabetical tie-break and is not a score difference (the builder
rubric role scored cookbook 15 vs 18 elsewhere — the only round-1
differentiation). Round 1 says: on paper, the five packs are nearly
indistinguishable. That is what the implementation round exists for.

## Implementation round — the §6 gate

Harness: `scripts/temporal/kill_resume_harness.py` (PR-A of this
pass) — the RFP §6 bounded build. Its V1 suite run: worker SIGKILLed
mid-activity (pid 9210), second worker resumed, workflow completed,
**receipt count exactly 1**, the started-but-unrecorded attempt
surfaced as an unknown outcome and reconciled via the idempotency
key, history digest `025f3f9d34076c29…` in the evidence envelope.

| Candidate | Suites | Result |
|---|---|---|
| V1 pi-core-resume | §6 kill-resume harness | **1/1 pass**, receipted |
| V2 cookbook-agent-loop | HITL approval (pause on signal → resume → complete); §6 harness | **2/2 pass**, receipted |
| V3 versioned-autoscale | omes load scenario vs dev server | **0/1** — omes (Go load harness) absent in this environment; the attempt is receipted with its real exit code and the phantom-test rule credits zero. The versioning/autoscale *model* self-check passes (in-flight build pinning + monotone clamped autoscale) and is filed as evidence, not as a suite |
| V4 contract-first | Envelope schema → validators in 2 languages (Python + JS), aggregated violations | **1/1 pass**, receipted — both languages agree on every payload; multi-broken payload yields 6 aggregated violations |
| V5 serverless-skill | Skill dry-walk vs dev server only | **1/1 pass**, receipted — local steps ran (scope, access, packaging, registration, verification, rollback-by-terminate); the 3 cloud steps recorded `specified_not_run` with the card-rule reason, none silently skipped |

**DoE slice (TD-004):** 2⁴ factorial, 20 canonical rows
(`implementation/doe-rows.json`): the 4 runnable arms
(local-dev × remote) × 2 repetitions completed with real workflow/run
IDs, mean deterministic score 1.0; the other 12 cells are published
as `specified_not_run` rows with reasons (cloud = card rule; device =
remote-first). Contract hash, env fingerprint, benchmark version and
the scorer definition are stamped on the rows file.

## Round 2 — one separation, one tie

On the equalized evidence, LOCAL_BASELINE scores: pi-core-resume
**25.0**, cookbook-agent-loop **25.0**, contract-first **25.0**,
serverless-skill **25.0**, versioned-autoscale **11.615**. The
implementation round separated exactly one candidate — V3, whose
only declared suite could not execute here — and left a **four-way
tie at the maximum** among the candidates whose suites all passed.
The recorded ranked order (contract-first, cookbook-agent-loop,
pi-core-resume, serverless-skill, versioned-autoscale) is the
tie-break order among equals, never a score difference. Any reading
of this pass that names a single "winner" from the ballots is wrong;
the differentiation the RFP asks for is the explained MoneyBall
scoring and the G6 disposition below.

## Calibration — the intake priors, graded

BRIEF:temporal-recon-lane priors (V1 22 / V2 19 / V4 16 / V3 13 /
V5 10, ranks 1–5) vs round 2: score deltas V1 +3.0, V2 +6.0, V4 +9.0,
V5 +15.0 — all outside the 2.0 tolerance, because the priors priced a
*separation* the evidence did not produce (four candidates maxed the
rubric once their suites passed). Only V3 landed within tolerance
(13 → 11.615; rank 4 → 5). The priors' qualitative rationale still
tracks the disposition (V1/V2 strongest, V3 gated, V5 form-only) —
what they got wrong is magnitude: they scored *claims*, round 2
scored *proofs*, and four of five claims proved out. LOCAL_BASELINE's
own round-1 → round-2 deltas are within tolerance everywhere except
V3's collapse (23.654 → 11.615), the one evidence-driven move.

## MoneyBall — explained scores (weights fixed at intake)

Dimensions scored 0–10 from the record; weights: relevance 0.30,
evidence maturity 0.25, survivability (§6 outcome) 0.20, adoption
cost inverse 0.15, composability 0.10.

| Candidate | Rel .30 | Mat .25 | Surv .20 | Cost⁻¹ .15 | Comp .10 | **Weighted** |
|---|---|---|---|---|---|---|
| V1 pi-core-resume | 10 — answers the fleet loss mode head-on | 8 — pattern upstream + in-repo smoke, now §6-proven | 10 — §6 PASS is its suite | 8 — one harness, no new platform | 7 — core other planes build on | **8.90** |
| V2 cookbook-agent-loop | 9 — agent loops are the fleet's daily work | 8 — cookbook upstream + LangSmith in-repo | 10 — §6 PASS + HITL proven | 6 — per-framework packaging surface | 9 — integrations are its substance | **8.50** |
| V4 contract-first | 6 — enables durability, adds none itself | 7 — fixture-proven in 2 languages | 3 — validates the envelope the harness emits; no §6 run of its own | 9 — schema + validators, cheapest adoption | 10 — contracts are how planes compose | **6.50** |
| V5 serverless-skill | 5 — form only while execution is gated | 4 — walk proven; nothing executed in cloud | 4 — walk ran the unit workflow; no kill proof | 6 — a skill pack is cheap to carry | 6 — starter shape composes, execution doesn't yet | **4.80** |
| V3 versioned-autoscale | 6 — routing actuation matters at scale | 3 — model only; omes unrun | 0 — no §6 or load proof in this environment | 3 — K8s + omes are the heaviest adoption here | 6 — versioning composes with routing decisions | **3.60** |

## G6 disposition (TD-007)

**Per variant:**
- **V1 pi-core-resume — ADOPT.** The §6 harness and the
  unknown-outcome reconciliation are now the fleet's durability gate
  assets. Best piece taken: started-marker reconciliation (a started
  unit with no receipt resolves as unknown, never blindly retried).
- **V2 cookbook-agent-loop — PILOT.** HITL + §6 both proven; pilot
  the approval-pause recipe on one real lane flow before wider
  adoption. Best piece: the signal-pause approval shape.
- **V3 versioned-autoscale — REFERENCE-ONLY.** The model is sound
  and self-checked; actuation is unproven (omes unrun, K8s gated).
  Best piece: the in-flight build-pinning invariant (N3's
  precondition). Revisit when a cluster or omes run exists.
- **V4 contract-first — ADOPT (as contract discipline).** The
  evidence-envelope schema + dual-language validators become the
  lanes' evidence contract. Best piece: aggregated-violation
  validators generated from one schema. Its mid MoneyBall rank is
  the intake's own caveat: contracts add no durability by themselves.
- **V5 serverless-skill — REFERENCE-ONLY.** The form is proven by
  the dry-walk; every execution path stays owner-gated. Best piece:
  the dry-walk discipline — cloud steps named `specified_not_run`,
  never silently skipped.

**Per seed repo:** adopt — temporalio/pi-temporal (pattern),
temporalio/temporal (substrate), temporalio/cli (dev server),
temporalio/api (contract source). Pilot — temporalio/ai-cookbook,
temporalio/ai-integrations, temporalio/nexgen. Reference-only —
temporalio/temporal-worker-controller,
temporalio/temporal-auto-scaled-workers, temporalio/omes,
temporalio/ui (history-as-projection reading),
temporalio/skill-temporal-serverless (form),
temporalio/awesome-temporal, temporalio/cloud-operator,
temporalio/cruise-control-api, temporalio/kube-temporal,
temporalio/public-actions.

**N1–N7 survival:** N1 **survives, implemented** (harness envelope
carries history digest + attestation reference). N2 **survives** —
the factorial ran and published canonical rows; factorial-arms-as-
workflows is the next build, not this one. N3 **survives as model**
(build-pinning invariant proven by self-check; actuation gated with
V3). N4 **survives untested** — no Gantt compile was attempted in
this pass. N5 **survives** — this pass is the cycle executed end to
end; running it *as* a Temporal workflow is future work, stated as
such. N6 **survives as composition claim** — the four planes are
named and seeded; a full single-request lifecycle across all four
has not yet run. N7 **survives, implemented** — the unknown-outcome
protocol runs in the harness and is encoded in the envelope schema
(`unknown_outcomes` is a required field).

## Gates honored

No Cloud/AWS/GCP account or payment instrument; serverless execution
paths `specified_not_run` step-by-step. No vendoring (SDK + CLI are
environment installs, not repo content). Remote-first (dev server on
this VM; nothing on-device). Credentials names-only — none were
needed. No variant decides readiness, dispatch, merge, or approval:
this record is evidence for the operator, not a decision.
