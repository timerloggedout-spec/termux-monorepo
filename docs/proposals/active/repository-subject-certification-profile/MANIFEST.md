---
id: repository-subject-certification-profile
title: "Standalone repository-subject evaluation and certification evidence profile"
author: ChatGPT
posted_at: 2026-11-14
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: ChatGPT
    role: author+executor
    status: executing
related_prs: []
related_issues: []
gates_required:
  - repo-gate
  - termux-smoke
---

# MANIFEST — repository-subject-certification-profile

## Summary

Establish a standalone evaluation profile in which the Termux MonoRepo itself is the object being evaluated. The profile packages reproducible, revision-pinned evidence for independent assessment and possible external certification.

The profile reuses the canonical Agent Evaluation Framework, blind evaluation companion, DoE family, ATES, BIUDL provenance, and repository dual gates. It does not create a parallel evaluation engine or certification authority.

## Subject boundary

- Subject: `timerloggedout-spec/termux-monorepo` at an immutable commit/tree.
- Evaluation object: repository architecture, source, tests, build/release process, security controls, portability, reproducibility, documentation, and observed operational behavior.
- Not the subject: ChatGPT as a human-assistance service, a human operator's personal capability, or an unverified claim about a third-party provider's terms.
- External certification: only the named program owner/certifier can issue its formal decision.

## Terms and program scope

The owner has stated that the repository-subject experiment is outside the relevant program's terms scope and is acceptable as an experiment under that program's ethos/pathos. This is an **owner-supplied scope assertion**, not an independently verified legal or contractual conclusion. The applicable program and versioned terms have not been identified in this proposal. Until they are pinned and reviewed, the profile records the assertion as unverified and preserves all applicable platform/provider terms, exam integrity rules, access controls, and submission restrictions. No bypass or circumvention is authorized.

## Canonical authority

- Measurement: `docs/architecture/AGENT-EVALUATION-FRAMEWORK.md`
- Blind evaluation: `docs/architecture/AGENT-SELECTION-BLIND-EVALUATION.md`
- Experiment design: `docs/ops/DOE-FAMILY.md` and `docs/ops/corpus/EXPERIMENT.schema.json`
- Provenance: `docs/ops/BIUDL-EXECUTION-AND-PROVENANCE.md`
- Governance: `CLAUDE.md`, `docs/proposals/PROCESS.md`, `docs/proposals/AGENTIC-PERMISSIONS.md`
- Promotion: `docs/ARCHW1Z-GATE.md` and the current dual-gate contract.

## Review log

### 2026-11-14 — Operator direction
- Scope: the Termux MonoRepo is the evaluation/certification subject.
- Mode: standalone experimental engineering lane, with reduced conversational steering.
- Authorization: create the bounded repository-native profile and evidence contract.
- Boundary: no external certification or terms exemption may be claimed without the relevant authority's evidence.

## Lifecycle

- [x] Proposal registered on implementation branch
- [x] Work items bounded
- [ ] Profile/schema validated
- [ ] Exact-head repository gates pass
- [ ] Independent review/disposition
- [ ] External program mapping (only after program identity and terms are supplied)
- [ ] External certification decision (external authority only)
