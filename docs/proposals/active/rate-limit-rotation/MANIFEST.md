---
id: rate-limit-rotation
title: "Rate limits, model rotation, OpenRouter fallback"
author: grok
posted_at: 2026-08-08
status: executing
priority: P0
reviewers:
  - id: grok
    role: author+executor
    status: posted
related_issues: [86, 87, 88, 91, 94]
related_prs: [72, 81, 101, 102, 104, 105]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — rate-limit-rotation

## Summary

Free-tier Gemini soft budgets are residual only.
**OmniRoute ↔ OpenRouter** are first-class free peers selected by role + soft budget;
real HTTP invoke via `http-llm-invoke` (not notification stubs).

## Review log

### 2026-08-09 — grok

- Disposition: **executing**
- #101/#102: peer selection + after-peers capacity on master
- #104: active free model matrix + candidate fallback loop (APPROVED)
- RL-05 closes on #104 merge; then land #105 fail-fast if non-conflicting
- Next: RL-10 (#81 quota-gate on master), RL-17 (yq), #90 compression

### 2026-08-08 — grok

- Disposition: **executing**
- Foundation: model-rotation.yaml + model-router composite action
- Coordinates with PR #81 quota-gate (job-level) and #72 LB (deferred dirty)
