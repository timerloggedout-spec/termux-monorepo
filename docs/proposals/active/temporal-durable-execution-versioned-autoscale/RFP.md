# Proposal — Durable execution substrate for the lane fleet (Temporal four-plane RFP) — Worker Versioning + backlog-driven autoscaling (WCI) as the actuation layer for MoneyBall/quota routing decisions; K8s actuation itself specified_not_run (no cluster), the versioning/autoscale model and omes load evidence are the claims.

- **Proposal ID:** temporal-durable-execution-versioned-autoscale
- **Kind:** rfp
- **Surface:** delphi-oracle-method
- **Deadline:** UNVERIFIED — confirm from the official page
- **Status:** GENERATED — in review; generated proposals carry no ballots
- **Generated:** 2026-10-28T02:09:47Z by scripts/delphi/generate_proposal.py oracle-method-generator/v1

## 1. Executive request

Generate n=5 candidate architectures for a durable-execution substrate that lets lane work survive worker/VM death, drafted from the Temporal ecosystem as seeds through the repo's existing starter templates, and run the full Oracle Method cycle: cross-vote round 1 with the recorded expectations, an implementation round gated on the kill-and-resume proof (RFP §6), a DoE 2^4 factorial slice, and round 2 on an equalized evidence base with calibration deltas to the weighting/outcome ledgers.

## 2. Basis in evidence

- Worker Versioning + backlog-driven autoscaling (WCI) as the actuation layer for MoneyBall/quota routing decisions; K8s actuation itself specified_not_run (no cluster), the versioning/autoscale model and omes load evidence are the claims. (evidence: `docs/rfps/temporal-durable-execution/RFP.md`, `docs/rfps/temporal-durable-execution/RECON.md`)
- Four-plane composition: Bifrost = request plane (proposal + partial slice), Gravitee = publication plane (research seed only), Temporal = time plane, getDX = measurement plane with zero in-repo presence (seed before any claim), Witness attests across planes with the evidence envelope canonical. (evidence: `docs/rfps/temporal-durable-execution/RECON.md`, `docs/proposals/active/bifrost-gateway-integration/RECON.md`, `docs/repositories/GRAVITEE-RESEARCH-SEED.md`, `config/agent_stack_integrations.json`)
- MoneyBall weights fixed at G0 intake: relevance 0.30, evidence maturity 0.25, survivability proof 0.20, adoption cost inverse 0.15, composability 0.10; scores must be explained per candidate. (evidence: `docs/rfps/temporal-durable-execution/INTAKE.md`, `ml/pipelines/moneyball/explain.py`)
- Owner gates: no Temporal Cloud/AWS/GCP account or payment instrument (serverless execution paths specified_not_run), no vendoring, remote-first, credentials names-only. (evidence: `docs/rfps/temporal-durable-execution/RFP.md`)

## 3. Plan

**Steps:**

1. Model Worker Versioning (build-id routing) as the actuation layer for MoneyBall/quota routing decisions (N3)
2. Model backlog-driven autoscaling (WCI) as a deterministic policy over queue metrics — the model is the claim
3. Run the omes load scenario against the self-host dev server with published scenario receipts (declared suite)
4. Record K8s actuation itself as specified_not_run wherever no cluster exists

**Risks:**

- Actuation unproven without a cluster — the variant can win the model and still not move a worker
- omes is a heavy harness; scenario receipts may not be producible in every environment

**Alternatives considered:**

- Static worker pools — no routing actuation at all
- Cloud autoscaling paths — owner-gated, not taken

## Provenance

Generated from 1 evidence set(s), 10 stamped items. Full generation receipt: `PROVENANCE.json` in this directory. Facts not resolved against the evidence at generation time are marked UNVERIFIED above, never asserted.
