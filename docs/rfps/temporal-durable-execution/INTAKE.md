# G0 INTAKE — Temporal durable-execution RFP (fixed parameters)

**Lane:** [MUSEai]@{role:{temporal-recon}}
**Date:** 2026-10-27 · **RFP:** `RFP.md` (this folder) · **Evidence:** `RECON.md`
**Tracking issue:** #1885 · **RFP landed:** PR #1867, merged `74c5b5d3`
**Status:** G0 complete. Dispatched to the Delphi lane for the generation
pass (GitHub comment on #1885 + lane relay, 2026-10-27). No generation has
run yet; nothing below is a result.

## Fixed parameters

| Parameter | Value |
|-----------|-------|
| Proposals per pass (n) | **5** — variants V1–V5 in `brief.json`, each with a declared seed combination |
| Cross-vote | Oracle Method cycle: round 1 with input expectations recorded (below) → implementation round → round 2 on equalized evidence (sha256-stamped bundle) → calibration deltas to ledgers #1489 / #1487 |
| Source classes | Separate, never merged (LOCAL_BASELINE deterministic; HUMAN_COLLABORATOR / MODEL_PROVIDER only from recorded ballots, else honestly 0) |
| Plan floor | `require_plan: true` in the brief — plan-less generation is refused |
| Implementation gate | RFP §6 kill-and-resume harness; unreceipted test suites score ZERO (phantom-test rule) |
| DoE slice (G4) | 2⁴ full factorial: substrate × attestation × placement × routing (RFP §3); task contract hash, env fingerprint, benchmark version, scorer fixed |

## MoneyBall weights (fixed at intake; explain-per-candidate required)

| Dimension | Weight |
|-----------|--------|
| Fleet-pain relevance | 0.30 |
| Evidence maturity | 0.25 |
| Survivability proof (§6 harness outcome) | 0.20 |
| Adoption cost (inverse) | 0.15 |
| Four-plane composability | 0.10 |

## Variants (seed combinations — full text in `brief.json`)

- **V1 pi-core-resume** — pi-temporal core + temporal + cli.
- **V2 cookbook-agent-loop** — ai-cookbook + ai-integrations + temporal.
- **V3 versioned-autoscale** — temporal-worker-controller +
  temporal-auto-scaled-workers + omes (K8s actuation specified_not_run
  where no cluster exists; the versioning/autoscale *model* is the claim).
- **V4 contract-first** — api + nexgen + ui (history-as-projection).
- **V5 serverless-skill** — skill-temporal-serverless +
  temporal-auto-scaled-workers (all Cloud execution paths
  specified_not_run under the card rule; the skill-form starter is the
  claim).

## Input vote expectations (priors, recorded pre-implementation)

Expected order: **V1 > V2 > V4 > V3 > V5.**
Rationale: V1 is the only variant whose core pattern answers the fleet's
actual loss mode (worker death) and carries a runnable no-key starter;
V2 rides integrations already in-repo; V4 is cheap and composable but
does not itself add durability; V3's actuation is real but K8s-gated;
V5's execution paths are owner-gated, leaving only its form to score.
These priors exist to be calibrated against in round 2 — including if
they are wrong (cf. Strands pass, where the brief priors missed).

## Owner gates carried into the pass (unchanged)

No Temporal Cloud / AWS / GCP account or payment instrument; serverless
execution paths specified_not_run. No vendoring/submoduling. Remote-first
— no Temporal server on-device. Credentials names-only. No variant may
decide readiness, dispatch, merge, or approval.

## Deliverables the pass owes back (RFP §11)

Research-seed records (Temporal set + getDX evidence-pending) ·
5 candidate packs · §6 harness receipts · DoE canonical rows · explained
MoneyBall scores · round-1/round-2 ballots + calibration · G6 disposition
record. Returns land on issue #1885 and in the repo — PR numbers +
verified merge SHAs, never staged summaries.
