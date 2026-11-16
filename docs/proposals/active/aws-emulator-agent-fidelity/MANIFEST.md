---
id: aws-emulator-agent-fidelity
title: "AWS Emulator adoption and agent-built fidelity engineering loop"
author: ChatGPT
posted_at: 2026-11-16
source: user-supplied research set; upstream AWS and Anthropic documentation
status: posted
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_prs: []
related_branches:
  - feat/aws-emulator-agent-fidelity
related_proposals:
  - aws-free-tier-strands-delphi-oracle
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — aws-emulator-agent-fidelity

## Summary

Adapt the most transferable ideas from AWS Emulator's agent-built engineering system into the existing Termux monorepo without cloning AWS's product, duplicating the existing Agent Team Control Plane, adding a second queue/evidence ledger, or making AWS a runtime dependency.

The programme establishes a model/specification-driven fidelity workflow: authoritative contracts and reference behavior produce deterministic tests; independent discovery finds gaps; bounded implementation tasks fix one issue at a time; independent gates validate correctness, security, and regressions; observed outcomes feed the existing evidence and manager-evaluation systems.

## Existing-system reuse

- Existing QUE/QDesk and Agent Team Control Plane own admission, claims, routing, and task coordination.
- Existing Brain owns typed planning and policy-aware reasoning; it does not gain tool-execution authority.
- Existing Actions, repo-gate, Termux smoke, proposal lifecycle, and promotion controls remain authoritative.
- Existing SHE / JSONL / ATES / 3L0 / Moneyball records remain the outcome and evaluation plane.
- Existing AWS Free Tier + Strands Delphi proposal remains the owner of AWS account, cost, and Bedrock decision-oracle experiments.
- AWS Emulator and its evaluation suite are optional external test tools, not vendored dependencies or production infrastructure.

## Current state and honesty

- Proposal and contract validator are committed on `feat/aws-emulator-agent-fidelity`.
- The contract is research-only and runtime-disabled.
- No AWS account, AWS credentials, real-cloud calls, emulator binary, Docker image, package, or Termux device execution is claimed.
- AWS Emulator documents Linux x86_64/aarch64 source builds but a full cold build needs approximately 100 GB free disk; Android/Termux is not documented as a supported host. Use hosted Linux CI or a supported developer host for initial execution.
- Emulator results are not production certification: unsupported operations, incomplete fidelity, throttling/outage/region gaps, and unsandboxed test code require explicit limits and real-cloud validation before deployment.

## Decision requested

Review the P1 architecture and first bounded implementation. Keep the integration disabled until an independently reviewed host-runtime pilot, deterministic fixtures, security checks, and exact-SHA CI evidence exist. No account provisioning, paid calls, merge, deployment, or production routing change is requested.

## Acceptance evidence

1. Proposal lifecycle validation on the exact branch head.
2. Contract validator and unit tests pass on the exact branch head.
3. Repo-gate and Termux smoke report their actual host/device status without conflating Linux CI with Android device proof.
4. A separate approved pilot records pinned emulator/evaluation-suite versions, supported services, fidelity gaps, runtime resource use, and sanitized receipts.
5. Human review accepts the security and operational boundary before any runtime enablement.
