# RFP — Durable Execution Substrate for the Lane Fleet (Temporal × the four planes)

**Lane:** [MUSEai]@{role:{temporal-recon}}
**Status:** Open for Oracle Method generation pass — no substrate selected,
no account authorized, no code vendored by this document.
**Date:** 2026-10-27 · **Evidence base:** `RECON.md` in this folder
(live-derived, 2026-10-27).
**Owner boundaries:** independent of the hackathon Delphi RFPs except that
it *uses* the Oracle Method as its evaluation machinery; Temporal Cloud
signup is owner-gated (card rule) and is **not** requested here;
self-host/remote-first per the B160V heavy-runtime law.

## 1. Executive intent

The fleet loses work when execution surfaces die: VM replacements, killed
workers, expired sessions. Today that risk is carried by chat discipline
and retries-by-hand. This RFP asks for a **durable-execution substrate
design** — built by drafting from the Temporal ecosystem as `{seed}`
models through this repo's own `{starter}` templates — that makes a lane's
work survive the death of the machine running it, with provenance intact.

The question is not "adopt Temporal?" It is: **which pieces of the 17
recon'd repos, composed with Bifrost (request plane), Gravitee
(publication plane) and a to-be-seeded DX measurement plane, beat the
incumbent Actions/chat-driven execution on evidence — and what do we
invent that none of them has?**

## 2. Generation-first contract (Oracle Method, owner law)

Proposals for this RFP are **generated**, not hand-authored by a single
lane:

1. **Generate n** candidate architectures (n configurable; suggested
   n = 5) from the RECON evidence set. Each candidate must declare its
   seed combination explicitly (e.g. pi-temporal core + cookbook HITL +
   worker-versioning actuation) and its `{starter}` form (§5).
2. **Cross-vote round 1** — comparative ballots across all n, source
   classes separate, input vote expectations recorded before any
   implementation evidence exists.
3. **Implementation round** — every candidate gets the same bounded
   build: the §6 MVT kill-and-resume proof on the self-host dev server
   (remote/Codespace), scored by the deterministic harness, not by prose.
4. **Round 2** — second Delphi cycle on an *equalized* evidence base
   (every voter starts from the same per-candidate test results),
   re-vote, and calibration deltas (round-2 vs round-1 expectations)
   written to the weighting/elo ledgers.

No candidate may claim a capability its implementation round did not run.

## 3. Scoring — MoneyBall + DoE/MVT machinery

**MoneyBall composite** (weights to be fixed at intake, recorded in the
pass manifest; starting proposal): fleet-pain relevance 0.30 · evidence
maturity 0.25 · survivability proof (§6) 0.20 · adoption cost (inverse)
0.15 · composability with the four planes 0.10. Scores must be
explainable per candidate (`ml/pipelines/moneyball/explain.py` pattern) —
a bare number is not a result.

**DoE factorial (first slice)** — factors varied while task contract
hash, environment fingerprint, benchmark version and deterministic scorer
stay fixed (per `docs/ops/ATES-ORCHESTRATOR-DOE-MVT.md`):

| Factor | Levels |
|--------|--------|
| execution substrate | Actions/chat incumbent \| Temporal self-host |
| attestation | Witness off \| Witness on (digest referenced from evidence record) |
| worker placement | single remote worker \| two workers, kill-over enabled |
| routing input | static task queue \| MoneyBall/quota-weighted queue choice |

Primary outcomes: deterministic pass rate · duplicate-side-effect count ·
work-loss events per kill · time-to-resume. Secondary: retry/error rate,
human interventions, attribution confidence, ATES/WTCV.
Canonical row identity stays cohort × task × arm × repetition, extended
with workflow/run IDs as the trace identity (§7, N2).

**MVT cohort** — the existing seven hard invariants, plus one new:

8. **Kill-and-resume:** a worker is killed mid-activity; a second worker
   completes the workflow; started-but-unrecorded side effects are
   surfaced as *unknown outcome* (pi-temporal semantics), never silently
   retried; the evidence record closes with zero lost tasks.

## 4. Priorities (from RECON §5 — the pass may overturn them only on evidence)

- **P0:** pi-temporal pattern proof · ai-cookbook recipes as starters
  (agentic loop, HITL approval, deep-research) · ai-integrations plugin
  packaging for the frameworks we already touch (LangSmith bridge exists).
- **P1:** Worker Versioning + auto-scaled-workers WCI as actuation for
  routing decisions · omes load scenarios feeding DoE · nexgen-style
  contract generation for lane/evidence envelopes · skill-temporal-
  serverless mined as a skill-form starter.
- **P2 (watch only):** kube-temporal, cloud-operator, cruise-control-api,
  public-actions, ui patterns.
- **Out of scope:** any K8s adoption decision; any Cloud account; any
  on-device server; replacing OTEL/ATES canonical evidence (Temporal
  history is *referenced from* evidence records, never their successor).

## 5. Drafting method — `{seed}{starter}` templates already in the repo

Every generated candidate must be drafted through existing forms, one per
artifact, no new scaffolding:

| Artifact | Template (precedent) |
|----------|----------------------|
| Upstream model record | `docs/repositories/research-seeds/*.json` (Gravitee — currently the only occupant; this pass adds the Temporal set + a getDX seed marked evidence-pending) |
| Candidate pack | proposal `MANIFEST.md` + `ITEMS.md` (+ `RECON.md` where new recon is done) — Bifrost / Temporal-LangSmith precedents |
| Seed disposition | extract / do-not-extract / evidence / next-gate table — `docs/agentic/decisions/SEED_SELECTION.md` precedent, incl. its global no-go: no seed decides readiness, dispatch, merge, or approval |
| This RFP's own tracking | this folder + a tracking issue, mesh-resiliency RFP precedent |

## 6. The bounded build every candidate must survive

Extend `scripts/temporal/hello_workflow.py` (existing smoke) into the
proof harness — self-host dev server, remote or Codespace, never the
device:

1. Start a workflow whose activity performs one idempotent, receipt-
   emitting unit of fleet-shaped work (e.g. fetch_evidence over a fixed
   PR set).
2. Kill the worker mid-activity. Start a second worker.
3. Assert: workflow completes; receipt count = 1 (no duplicate side
   effect); any ambiguous activity outcome is reported as unknown, not
   retried blind; full history is exportable and its digest lands in an
   evidence-envelope record (Witness arm: attestation digest likewise
   referenced, keys names-only).

Pass/fail is the harness's, not the candidate author's.

## 7. Novel inventions this RFP explicitly solicits (none exists upstream)

- **N1 — Witness-attested workflow history.** Every completed workflow
  emits an evidence record referencing both the Temporal history digest
  and a Witness in-toto attestation of the producing command/materials.
  Durable execution × provenance: Temporal proves *what happened in
  order*; Witness proves *how the artifact was produced*; the envelope
  stays canonical (PR #1674 composition).
- **N2 — DoE/MVT as workflows.** Factorial arms as child workflows,
  scorer as a deterministic activity, experiment lineage = workflow
  lineage. A rerun is a replay, not a recollection — this closes the
  "defined-not-run" gap in the current harness with replayable evidence.
- **N3 — MoneyBall-routed task queues.** Queue/worker selection driven by
  `quota_weights`-style scoring, actuated through Worker Versioning so a
  routing change never breaks an in-flight workflow. Gantt/Oracle decide;
  Temporal actuates; MoneyBall prices.
- **N4 — Gantt plan as workflow.** The Camshaft-seed YAML phase plan
  compiles to a workflow: phases = child workflows, human check points =
  signals (ICM gate pattern), the Gantt projection = a *query* over live
  state instead of a generated file that drifts.
- **N5 — Oracle cross-vote as a durable process.** Generation → ballots
  (signals) → implementation round → round-2 on equalized evidence, as
  one long-lived workflow that survives the VM replacements that
  currently interrupt Delphi passes mid-flight.
- **N6 — Four-plane request lifecycle.** One agent request traverses
  Bifrost (request) → Temporal (time) → Gravitee-shaped publication of
  its resulting API/artifact → DX measurement of the human's experience
  of the whole loop, with Witness attesting each hop into one evidence
  record.
- **N7 — Unknown-outcome as a fleet-wide side-effect protocol.**
  Generalize pi-temporal's rule beyond coding agents: any lane activity
  that started without a recorded result resolves as *unknown outcome*
  requiring reconciliation — never auto-retry — encoded in the evidence
  envelope schema.

## 8. getDX / measurement plane — seed before claims

getDX has zero in-repo presence (RECON §2). This RFP therefore asks first
for a **research seed only** (Observatory record + research-seeds JSON,
evidence-pending), scoped to one question: which DX signals (flow,
friction, delivery) can be derived from data the fleet already emits
(Actions telemetry, PR cycle times, lane interventions) before any
external DX platform is evaluated. No DX metric may be reported from a
platform that has not been seeded and evidenced.

## 9. Phases (Gantt — dependencies, not dates promised)

| Phase | Depends on | Gate |
|-------|-----------|------|
| G0 Intake: fix n, weights, tracking issue | this RFP | owner-visible manifest |
| G1 Generation: n candidates through §5 templates | G0 | each candidate's seed combination declared |
| G2 Cross-vote round 1 (expectations recorded) | G1 | ballots + receipts in evidence |
| G3 Implementation round: §6 proof per candidate | G2 | harness output, deterministic |
| G4 DoE slice (16-cell full factorial or fractional, fixed at G0) | G3 | canonical rows published |
| G5 Round 2 on equalized evidence + calibration deltas | G4 | ledger updates |
| G6 Disposition: adopt/pilot/reference-only/reject per candidate + per seed | G5 | SEED_SELECTION-style record landed |

## 10. Non-goals and red lines

- No Temporal Cloud / AWS / GCP account creation or payment instrument —
  owner-gated, untouched by this RFP (serverless-workers skill material
  is mined as *pattern*, its Cloud paths stay specified_not_run).
- No vendoring, submoduling, or executing unreviewed upstream code;
  forks, where wanted, follow the Bifrost/Gravitee precedent (owner
  account fork = comparison surface).
- No ML/HindSight telemetry deletion; no credential values anywhere —
  names only, vault/PAT-helper route for GitHub work.
- No seed, candidate, or workflow decides readiness, dispatch, merge, or
  approval (SEED_SELECTION global no-go carries over unchanged).

## 11. Deliverables

1. `docs/repositories/research-seeds/` records for the Temporal set +
   getDX (evidence-pending).
2. n candidate packs (MANIFEST/ITEMS) under `docs/proposals/active/`.
3. The §6 proof harness + its receipts (PR-linked, history-verified).
4. DoE canonical rows + MoneyBall explained scores per candidate.
5. Round-1/round-2 ballots + calibration deltas to the ledgers.
6. Final disposition record (G6) naming, per repo in RECON §1, the best
   piece taken, what was learned, and what was invented instead (§7).
