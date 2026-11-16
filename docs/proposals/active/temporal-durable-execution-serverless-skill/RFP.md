# Proposal — Durable execution substrate for the lane fleet (Temporal four-plane RFP) — The agent skill as the deployment starter (scope -> access checks -> packaging -> registration -> verification -> rollback); all Cloud execution paths specified_not_run under the card rule.

- **Proposal ID:** temporal-durable-execution-serverless-skill
- **Kind:** rfp
- **Surface:** delphi-oracle-method
- **Deadline:** UNVERIFIED — confirm from the official page
- **Status:** GENERATED — in review; generated proposals carry no ballots
- **Generated:** 2026-10-28T02:09:47Z by scripts/delphi/generate_proposal.py oracle-method-generator/v1

## 1. Executive request

Generate n=5 candidate architectures for a durable-execution substrate that lets lane work survive worker/VM death, drafted from the Temporal ecosystem as seeds through the repo's existing starter templates, and run the full Oracle Method cycle: cross-vote round 1 with the recorded expectations, an implementation round gated on the kill-and-resume proof (RFP §6), a DoE 2^4 factorial slice, and round 2 on an equalized evidence base with calibration deltas to the weighting/outcome ledgers.

## 2. Basis in evidence

- The agent skill as the deployment starter (scope -> access checks -> packaging -> registration -> verification -> rollback); all Cloud execution paths specified_not_run under the card rule. (evidence: `docs/rfps/temporal-durable-execution/RFP.md`, `docs/rfps/temporal-durable-execution/RECON.md`)
- Four-plane composition: Bifrost = request plane (proposal + partial slice), Gravitee = publication plane (research seed only), Temporal = time plane, getDX = measurement plane with zero in-repo presence (seed before any claim), Witness attests across planes with the evidence envelope canonical. (evidence: `docs/rfps/temporal-durable-execution/RECON.md`, `docs/proposals/active/bifrost-gateway-integration/RECON.md`, `docs/repositories/GRAVITEE-RESEARCH-SEED.md`, `config/agent_stack_integrations.json`)
- MoneyBall weights fixed at G0 intake: relevance 0.30, evidence maturity 0.25, survivability proof 0.20, adoption cost inverse 0.15, composability 0.10; scores must be explained per candidate. (evidence: `docs/rfps/temporal-durable-execution/INTAKE.md`, `ml/pipelines/moneyball/explain.py`)
- Owner gates: no Temporal Cloud/AWS/GCP account or payment instrument (serverless execution paths specified_not_run), no vendoring, remote-first, credentials names-only. (evidence: `docs/rfps/temporal-durable-execution/RFP.md`)

## 3. Plan

**Steps:**

1. Execute the skill dry-walk against the self-host dev server only: scope -> access checks -> packaging -> registration -> verification -> rollback (declared suite)
2. Record every Cloud execution step as specified_not_run with the card-rule reason, step by step
3. Score the skill FORM (the starter's shape) — execution paths are not claimed

**Risks:**

- While gated, the claim reduces to form; a high score here must not be read as execution readiness
- Skill surface drift upstream changes the walk

**Alternatives considered:**

- Cookbook packaging (V2) as the starter form
- CLI starters (V1) as the onboarding path

## Provenance

Generated from 1 evidence set(s), 10 stamped items. Full generation receipt: `PROVENANCE.json` in this directory. Facts not resolved against the evidence at generation time are marked UNVERIFIED above, never asserted.
