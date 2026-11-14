---
id: qdesk-self-repair
title: "QDesk self-repair loop (SIE → Desk QUE)"
author: timerloggedout-spec
status: executing
path: active/qdesk-self-repair/
related_workflows:
  - .github/workflows/qdesk-self-repair.yml
  - .github/workflows/proposal-lifecycle.yml
gates_required:
  - proposal-lifecycle
  - repo-gate
---

# MANIFEST — qdesk-self-repair

## Purpose
Formalize the existing QDesk self-repair proposal already present in PROPOSAL.md and its scheduled workflow. The loop observes failures, stale feeds and open Desk issues; researches root causes; prepares RFPs and candidate patches; delegates evaluation to DoE; promotes only under the stated authority boundaries; and records outcomes.

## Authority and safety
- Desk is the operator; Swarm is the builder; ledger operations steward the record; DoE is the external reviewer.
- The loop does not select its own winning candidate.
- Self-generated evidence remains uncorroborated until independently checked.
- Changes are additive only under the proposal's stated constraints.
- Destructive changes, secrets, spending and third-party repository changes require an Owner packet.
- The Fleet Swarm App installation is suspended; writes follow the PAT route described in the proposal.

## Source of truth
- PROPOSAL.md contains the originating scope and operating constraints.
- .github/workflows/qdesk-self-repair.yml is the scheduled workflow implementation.
- The workflow's run evidence and the outcome ledger remain the evidence of execution; this manifest is registration metadata only.
