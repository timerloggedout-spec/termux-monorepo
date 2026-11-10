# RFP — GitHub Command & Workflow Security Gate

- **RFP ID:** `security.command_workflow_gate`
- **Status:** Submitted to Delphi RFP gate; implementation not yet awarded or started.
- **Filed lane:** `ops / security`
- **Related issue:** #4015 (DoE classifier + fleet-dispatch policy comparison)
- **Related security intake:** #4010
- **Proposal:** [GitHub Command & Workflow Security Gate](../../ops/GITHUB-COMMAND-WORKFLOW-SECURITY-GATE.md)

## Executive request

Build a reusable, deterministic-first security gate for destructive shell operations, SSH exposure, credential handling, remote execution, untrusted artifacts, and GitHub Actions workflow changes. Integrate with the existing Tier-1 classifier and evidence substrate. Keep GitHub CI enforcement distinct from runtime command enforcement, and keep Delphi, MoneyBall, 3L0, DeskQUE, and AdminGraph within their documented ownership boundaries.

## Gantt / dependency plan

| Phase | Start | End | Depends on |
|---|---|---|---|
| P0 baseline + policy contract | T0 | T0+2d | Existing architecture and tests inventory |
| P1 parser-backed deterministic engine | T0+2d | T0+6d | P0 contract freeze |
| P2 GitHub reusable workflow + receipts | T0+5d | T0+9d | P1 engine interface |
| P3 DoE replay and MoneyBall comparison | T0+8d | T0+12d | P1/P2 fixture and receipt contracts |
| P4 DeskQUE/AdminGraph projection + runbook | T0+10d | T0+14d | P2 receipt schema |
| Review / promote or park | T0+14d | T0+14d | CI evidence, DoE report, human security review |

Dates are relative planning targets, not commitments. Parallel work is allowed only across independent deliverables with stable interfaces.

## Scope

### In scope
- Parser-backed shell command and execution-plan normalization.
- Deterministic rules for destructive filesystem operations, SSH exposure, shell injection, credential flows, network/remote execution, untrusted execution, and GitHub Actions supply chain.
- Reusable GitHub workflow and required-check rollout plan.
- Secret-safe receipts, replay fixtures, exceptions, and operator documentation.
- DoE comparison of baseline and candidate policies using synthetic/replay inputs.
- Explainable MoneyBall scoring beside Delphi ballots.
- Read-only DeskQUE/AdminGraph integration.

### Out of scope
- Automatic production deployment or branch-protection changes.
- Live attack simulation, destructive commands, or real credential testing.
- Paid inference or use of unverified free-tier claims.
- Automatic privilege grants, collaborator changes, secret rotation, or merges.
- Replacing the existing Tier-1 registry, GitHub issue router, quota SSOT, or evidence SSOT.

## Delphi panel roles

Use the existing five blind roles and current live weights from the Delphi weights ledger (cold-start defaults are not authoritative when a live ledger exists):

- OPERATOR — policy and owner-risk perspective.
- builder — feasibility and maintainability.
- reviewer — adversarial code and workflow review.
- Scout — evidence, dependencies, and provider-route discovery.
- cost_auditor — quota, cost, and entitlement; retains the documented money veto.

The current gate is rubric-only (`DELPHI_LLM_MAX=0`). Do not enable model ballots in this pass. Any future model-provider participant must first pass the explicit free-inference eligibility checks in the proposal and be recorded as a separate MODEL_PROVIDER evidence class, not silently substituted for a human role.

## DoE / participant treatment plan

Use issue #4015 as the experiment lane. Compare the pre-registered treatments A–D in the proposal against one frozen synthetic corpus. Candidate inference participants may be selected from existing provider/model pools only after verifying an actual invoke route, current availability, exact free entitlement, live quota headroom, and task-compatible capability. Record unavailable/unconfigured/quota-limited/route-missing distinctly. No roster-only or quota-registry-only inference calls.

Every run records `run_id`, `run_attempt`, `head_sha`, experiment ID, cohort, treatment, policy version, participant role, provider/model/adapter, eligibility evidence, latency, token counts where available, and outcome. No prompts, secrets, raw command payloads, or private quota balances in public receipts.

## Free quota / authentication

- **Inference spend:** zero authorized. Only demonstrably no-cost, currently eligible endpoints may be considered in the DoE participant pool; current Delphi gate model ballots remain disabled.
- **GitHub Actions:** standard GitHub-hosted runners for public repositories are documented as free under the applicable GitHub Actions billing policy; this does not establish any provider inference entitlement.
- **Authentication:** no new secret required for the initial deterministic CI baseline. Do not add or expose secret values.

## Failure modes and controls

- Parser gap / ambiguous command → review or quarantine, never allow by default.
- Missing or stale quota evidence → no model-provider invocation.
- Provider listed but invoke route absent → `not_eligible`.
- Public SSH with password authentication or unknown effective config → block/review according to the frozen policy; caller flags cannot weaken the decision.
- Untrusted fork/PR content → no privileged token or secret exposure.
- Model output conflicting with deterministic finding → deterministic rule prevails.
- CI outage or unavailable classifier → explicit unavailable state; do not report pass.
- Exception expired or scope mismatch → reject exception.

## Evidence and acceptance

Acceptance is defined in the proposal's acceptance gates. Each implementation PR must include exact changed paths, contract impact, exact test commands and results, workflow run IDs, source/version pins, portability targets tested, known limitations, and rollback notes.

## Decision request

Evaluate this as a security-policy and engineering RFP. Awarding the RFP admits a bounded implementation trial only; it does not grant production promotion or relax any existing authorization boundary.
