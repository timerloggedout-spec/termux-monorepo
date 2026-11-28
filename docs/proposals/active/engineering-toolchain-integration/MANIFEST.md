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
related_prs: []
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

## Links

- [ITEMS](./ITEMS.md)
- [Source and integration map](./source.md)
- [Superpowers implementation plan](../../../superpowers/plans/2026-11-28-engineering-toolchain-activation.md)
