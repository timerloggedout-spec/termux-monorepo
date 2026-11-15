---
id: workflow-self-repair-hardening
title: Evidence-first CI self-repair and workflow failure-mode correction
author: ChatGPT
posted_at: 2026-11-15
source: source.md
status: executing
priority: P0
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_issues: [5316, 5361, 5363]
related_prs: [5476, 5477, 5478]
related_branches:
  - fix/do-style-generated-export-subject
  - fix/team-mvt-skipped-lane-evaluation
  - fix/gemini-after-peers-rate-limit-defer
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — workflow-self-repair-hardening

## Purpose

Convert recurring CI failures into evidence-backed, narrowly scoped fixes without weakening promotion, admission, review, or security boundaries.

## Operating contract

- A failure is not root-caused until its exact run, job, step, log, SHA and workflow revision are inspected.
- Missing or skipped evidence remains incomplete; it never becomes a positive result.
- Rate-limit exhaustion is a deferred state, not permission to bypass validation or burn provider quota.
- Generated repository metadata must be validated against the actual machine-generated forms without weakening the authoring standard.
- Promotion requires exact-head repo-gate and Termux smoke, independent review where required, and verified task outcome.

## Scope boundaries

This proposal covers only the three observed failure classes in #5316, #5361 and #5363. It does not authorize secret changes, production inference, paid fallback, branch-protection changes, auto-merge, or broad workflow rewrites.
