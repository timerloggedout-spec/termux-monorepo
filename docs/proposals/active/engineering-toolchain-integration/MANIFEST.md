---
id: engineering-toolchain-integration
title: "Engineering Toolchain Integration — CAD, EDA, CAE, manufacturing and silicon"
author: ChatGPT
posted_at: 2026-11-28
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: ChatGPT
    role: author-executor
    status: executing
related_issues: []
related_prs:
  - 5957
related_branches:
  - feat/engineering-toolchain-activation
gates_required:
  - repo-gate
  - termux-smoke
---

# MANIFEST — engineering-toolchain-integration

## Summary

Activate a FOSS-first engineering capability family inside Termux MonoRepo. The family covers mechanical CAD, electronics and electrical design, computational simulation, manufacturing handoff, semiconductor design and technical visualization. It connects the engineering taxonomy to the Integration Intelligence catalog, the Termux Agentic Hub's named capability boundary, ArchWiz discovery, QUE/QDesk intake, DoE/MVT evaluation, Reverse Engineering, refTemplates and the Learnings lane.

## Operator instruction

On 2026-11-28 the Operator requested active integration of the researched engineering toolchain into Termux MonoRepo, explicitly naming QUE, QDesk, ArchWiz, refTemplates, DoE/MVT, Reverse Engineering, Learnings and Matrices. This proposal records that instruction as the execution authorization for this bounded integration branch.

## Architecture decisions

1. Engineering is an independently owned sibling domain to Reverse Engineering. Each domain retains its own taxonomy, vocabulary and validator.
2. `ops/engineering/taxonomy.json` is the engineering taxonomy SSOT. It records discipline, tool role, license class, access cost, card requirement, formats, source URL, runtime target and stage-based toolchains.
3. `docs/integrations/registry.json` remains the only integration portfolio. Engineering tool records reference it; they do not create a competing provider catalog.
4. The Termux Agentic Hub exposes fixed, named, shell-free capabilities for taxonomy validation and read-only local tool inventory. GUI and compute-heavy applications use an explicitly approved remote Linux runner.
5. QUE/QDesk remain the only task admission, claim, lease, escalation and operator-review plane. Engineering adds task metadata and intake contracts, not another queue.
6. DoE owns experiment design; MVT is nested within DoE; ATES supplies the execution harness. Engineering experiments use the canonical cohort × task × arm × repetition identity.
7. refTemplates supply pinned references and upstream source lineage. They remain read-only inputs until a specific adaptation is reviewed and adopted.
8. Engineering outputs remain source-first and portable. Native design files, neutral exchange artifacts, solver inputs, tool versions, environment fingerprints, validation reports and output hashes travel together.

## Runtime truth

The current ChatGPT session exposes GitHub and research/documentation tools. The installed Termux-related plugin is recognized as installed, while no direct Termux device-operation function is exposed in this session. Repository code can define and test the device-side capability contract; actual device inventory and remote-runner execution require a live Termux receipt.

## Review log

### 2026-11-28 — ChatGPT

- Disposition: initial integration slice opened as draft PR #5957 against master.
- Head SHA at PR creation: `b7fba382c7b8661a11c7444468a0ce5a35c9bcf7`; subsequent commits on the branch require fresh checks.
- Runtime status: repository adapters implemented; live Termux probe and remote CAD/CAE execution remain pending device/runner evidence.


### 2026-11-28 — ChatGPT — integration expansion

- Added active QUE issue-form intake with unique admission identity and existing project-task parser compatibility tests.
- Added ArchWiz cockpit option [21] for the read-only engineering inventory.
- Added engineering taxonomy, probe, Hub protocol and issue-template tests to the required Termux smoke suite.
- Added a public standard GitHub-hosted runner and self-hosted runner profile; actual provisioning remains blocked by workflow permission and runner availability.
- Current branch head at this record: `b4ad26572f666f77923a74484beda537e760c711` (re-fetch before promotion).
- Workflow status on earlier superseded SHAs was cancelled; latest-head validation is pending.


### 2026-11-28 — ChatGPT — taxonomy, tracking and refTemplates audit

- Added the engineering project identity to `ops/tracking/projects.json` and the cohort to `docs/ops/AGENT-EVALUATION-LANE-REGISTRY.md`; generated tracking projections remain single-writer owned.
- Added the engineering taxonomy, probe, QUE template, Hub protocol and lane-classification checks to the required Termux smoke gate.
- Preserved the `refTemplates/` gitignore boundary: tracked reference metadata now lives in `docs/ops/ENGINEERING-REFERENCE-SET.json`; `refTemplates/engineering/` remains a local-only workspace.
- Corrected access evidence: Onshape Free is $0/public/non-commercial, while its Free-plan card requirement remains unknown; SOLIDWORKS for Makers is paid ($48/year or $15/month before tax), personal/non-commercial, with no free version/trial.
- Code state before this log update: `5736355324bd4a10b698c910dee53a5cef201643`. The manifest update itself creates a new head; run all final checks against the resulting branch SHA.
- Current runtime evidence remains repository-only; Termux device probe and runner execution remain blocked pending external receipts.

## Links

- [ITEMS](./ITEMS.md)
- [Source and integration map](./source.md)
- [Superpowers implementation plan](../../../superpowers/plans/2026-11-28-engineering-toolchain-activation.md)
- [Tracked engineering reference set](../../../ops/ENGINEERING-REFERENCE-SET.json)
- [refTemplates ingestion contract](../../../ops/ENGINEERING-REF-TEMPLATES.md)
