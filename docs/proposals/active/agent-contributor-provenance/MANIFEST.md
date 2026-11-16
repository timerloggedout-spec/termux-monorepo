---
id: agent-contributor-provenance
title: "Evidence-backed agent contributor attribution and source citation ledger"
author: ChatGPT
posted_at: 2026-10-18
source: "Issue #1241 and explicit operator directive"
status: in_review
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
  - id: ChatGPT
    role: author+executor
    status: executing
related_issues: [1241]
related_prs: [1244]
related_branches: [feat/biudl-full-stack-provenance]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — agent-contributor-provenance

## Summary

Add evidence-backed contributor attribution and a complete, deterministic citation ledger to the existing Agent Evidence Substrate and ATES pipeline. The work covers agentic PAT ambiguity, provider/model/settings/context provenance, workflow/job/run and PR/issue linkage, manager/scout/orchestrator evaluation lanes, and source curation from daily briefs plus the existing resource/procurement/radar corpus.

This proposal extends the existing contracts; it does not create a new orchestrator, telemetry store, or source of truth.

## Non-negotiable boundaries

- GitHub actor and triggering actor are not provider/model authorship.
- Provider/model attribution must cite its evidence method; missing model/settings/context stays null.
- Settings/context are SHA-256 fingerprints only; never retain raw prompts, completions, credentials, cookies, or raw session context.
- Bridge/tunnel/Pinggy health is infrastructure evidence and must not be counted as agent task throughput.
- Citation extraction is offline and provenance-preserving; it does not fetch URLs or assert that a cited claim is true.
- Correctness and integrated task outcome outrank speed, activity, and nominal $0 cost.

## Canonical dependencies

- `CLAUDE.md`, `docs/proposals/registry.yaml`, and `docs/proposals/PROCESS.md`
- `docs/ops/AGENT-EVIDENCE-SUBSTRATE.md`
- `docs/ops/AGENT-TEAM-ORCHESTRATION.md`
- `docs/ops/AGENT-MONIKERS.md` and `docs/ops/AGENT-TEAM-ROSTER.md`
- `docs/architecture/AGENT-EVALUATION-FRAMEWORK.md`
- `docs/ops/AGENT-THROUGHPUT-EVENT.schema.json`
- `docs/briefing/DAILY-DIGEST-SPEC.md`, `docs/research/BRIEFING-INGEST.md`, `docs/research/FOSS-PROCUREMENT-MATRIX.md`, `docs/research/FORESIGHT-RADAR.md`

## Promotion

Promotion requires repo-gate and termux-smoke success on the same immutable head SHA, current review/check disposition, and an explicit classification of cancelled, quota-limited, failed, and successful collaborator runs. A provider cooldown is not review completion. A green status is evidence about that check only.
