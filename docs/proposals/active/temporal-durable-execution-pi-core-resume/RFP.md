# Proposal — Durable execution substrate for the lane fleet (Temporal four-plane RFP) — Agent-agnostic durable core: session-file state, worker death mid-turn resumed by another worker, started-but-unrecorded side effects surfaced as unknown outcome and never blindly retried.

- **Proposal ID:** temporal-durable-execution-pi-core-resume
- **Kind:** rfp
- **Surface:** delphi-oracle-method
- **Deadline:** UNVERIFIED — confirm from the official page
- **Status:** GENERATED — in review; generated proposals carry no ballots
- **Generated:** 2026-10-28T02:09:47Z by scripts/delphi/generate_proposal.py oracle-method-generator/v1

## 1. Executive request

Generate n=5 candidate architectures for a durable-execution substrate that lets lane work survive worker/VM death, drafted from the Temporal ecosystem as seeds through the repo's existing starter templates, and run the full Oracle Method cycle: cross-vote round 1 with the recorded expectations, an implementation round gated on the kill-and-resume proof (RFP §6), a DoE 2^4 factorial slice, and round 2 on an equalized evidence base with calibration deltas to the weighting/outcome ledgers.

## 2. Basis in evidence

- Agent-agnostic durable core: session-file state, worker death mid-turn resumed by another worker, started-but-unrecorded side effects surfaced as unknown outcome and never blindly retried. (evidence: `docs/rfps/temporal-durable-execution/RFP.md`, `docs/rfps/temporal-durable-execution/RECON.md`)
- Four-plane composition: Bifrost = request plane (proposal + partial slice), Gravitee = publication plane (research seed only), Temporal = time plane, getDX = measurement plane with zero in-repo presence (seed before any claim), Witness attests across planes with the evidence envelope canonical. (evidence: `docs/rfps/temporal-durable-execution/RECON.md`, `docs/proposals/active/bifrost-gateway-integration/RECON.md`, `docs/repositories/GRAVITEE-RESEARCH-SEED.md`, `config/agent_stack_integrations.json`)
- MoneyBall weights fixed at G0 intake: relevance 0.30, evidence maturity 0.25, survivability proof 0.20, adoption cost inverse 0.15, composability 0.10; scores must be explained per candidate. (evidence: `docs/rfps/temporal-durable-execution/INTAKE.md`, `ml/pipelines/moneyball/explain.py`)
- Owner gates: no Temporal Cloud/AWS/GCP account or payment instrument (serverless execution paths specified_not_run), no vendoring, remote-first, credentials names-only. (evidence: `docs/rfps/temporal-durable-execution/RFP.md`)

## 3. Plan

**Steps:**

1. Extend scripts/temporal/hello_workflow.py into the RFP §6 kill-and-resume harness on the self-host dev server (the pass's shared gate asset)
2. Model the pi-temporal pattern: session-file state, worker death mid-turn resumed by a second worker on the same task queue
3. Surface started-but-unrecorded side effects as unknown outcomes via started-marker reconciliation against the idempotency key — never blindly retried
4. Export the full workflow history and land its digest in the evidence-envelope record (N1 Witness arm, names-only)
5. Run the §6 prove as this variant's suite: exactly one receipt after a mid-activity SIGKILL

**Risks:**

- Dev-server persistence semantics differ from a production cluster; the proof bounds itself to the dev-server claim
- Activity retry windows can mask a missing idempotency key — the receipt count is the assertion, not the retry count

**Alternatives considered:**

- Temporal Cloud execution — owner-gated under the card rule, not taken
- Hand-rolled checkpoint files without Temporal history — no replay or audit surface, rejected at RECON

## Provenance

Generated from 1 evidence set(s), 10 stamped items. Full generation receipt: `PROVENANCE.json` in this directory. Facts not resolved against the evidence at generation time are marked UNVERIFIED above, never asserted.
