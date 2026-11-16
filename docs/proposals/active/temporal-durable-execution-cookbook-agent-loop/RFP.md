# Proposal — Durable execution substrate for the lane fleet (Temporal four-plane RFP) — Cookbook recipes as starters (agentic loop, HITL approval pause, deep-research, durable MCP) with plugin-per-framework packaging; LangSmith bridge already in-repo.

- **Proposal ID:** temporal-durable-execution-cookbook-agent-loop
- **Kind:** rfp
- **Surface:** delphi-oracle-method
- **Deadline:** UNVERIFIED — confirm from the official page
- **Status:** GENERATED — in review; generated proposals carry no ballots
- **Generated:** 2026-10-28T02:09:47Z by scripts/delphi/generate_proposal.py oracle-method-generator/v1

## 1. Executive request

Generate n=5 candidate architectures for a durable-execution substrate that lets lane work survive worker/VM death, drafted from the Temporal ecosystem as seeds through the repo's existing starter templates, and run the full Oracle Method cycle: cross-vote round 1 with the recorded expectations, an implementation round gated on the kill-and-resume proof (RFP §6), a DoE 2^4 factorial slice, and round 2 on an equalized evidence base with calibration deltas to the weighting/outcome ledgers.

## 2. Basis in evidence

- Cookbook recipes as starters (agentic loop, HITL approval pause, deep-research, durable MCP) with plugin-per-framework packaging; LangSmith bridge already in-repo. (evidence: `docs/rfps/temporal-durable-execution/RFP.md`, `docs/rfps/temporal-durable-execution/RECON.md`)
- Four-plane composition: Bifrost = request plane (proposal + partial slice), Gravitee = publication plane (research seed only), Temporal = time plane, getDX = measurement plane with zero in-repo presence (seed before any claim), Witness attests across planes with the evidence envelope canonical. (evidence: `docs/rfps/temporal-durable-execution/RECON.md`, `docs/proposals/active/bifrost-gateway-integration/RECON.md`, `docs/repositories/GRAVITEE-RESEARCH-SEED.md`, `config/agent_stack_integrations.json`)
- MoneyBall weights fixed at G0 intake: relevance 0.30, evidence maturity 0.25, survivability proof 0.20, adoption cost inverse 0.15, composability 0.10; scores must be explained per candidate. (evidence: `docs/rfps/temporal-durable-execution/INTAKE.md`, `ml/pipelines/moneyball/explain.py`)
- Owner gates: no Temporal Cloud/AWS/GCP account or payment instrument (serverless execution paths specified_not_run), no vendoring, remote-first, credentials names-only. (evidence: `docs/rfps/temporal-durable-execution/RFP.md`)

## 3. Plan

**Steps:**

1. Adopt ai-cookbook recipes as starters: agentic loop, HITL approval pause, deep-research, durable MCP
2. Package per framework following ai-integrations patterns; keep the in-repo LangSmith bridge as the observability arm
3. Implement the HITL approval workflow (pause on signal, resume, complete) against the dev server as suite 1
4. Run the shared §6 kill-and-resume harness as suite 2

**Risks:**

- Cookbook breadth over depth: recipes drift against the pinned SDK version
- Per-framework packaging multiplies maintenance surface

**Alternatives considered:**

- Bespoke workflows per recipe — slower, loses upstream maintenance
- pi-core only (V1) — no recipe leverage

## Provenance

Generated from 1 evidence set(s), 10 stamped items. Full generation receipt: `PROVENANCE.json` in this directory. Facts not resolved against the evidence at generation time are marked UNVERIFIED above, never asserted.
