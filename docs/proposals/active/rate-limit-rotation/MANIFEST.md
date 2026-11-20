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
related_issues: [86, 87, 88, 91]
related_prs: [72, 81]
gates_required: [repo-gate]
---

# MANIFEST — rate-limit-rotation

## Summary

Free-tier Gemini 3.5 Flash exhausted (65/20 RPD, 7/5 RPM per #86).
Route by role to high-RPD Lite models; reserve Flash for review;
fall back to OpenRouter when Gemini soft budgets are gone.

## Review log

### 2026-08-08 — grok

- Disposition: **executing**
- Foundation: model-rotation.yaml + model-router composite action
- Coordinates with PR #81 quota-gate (job-level) and #72 LB (deferred dirty)
