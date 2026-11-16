---
id: archwiz-markov-trellis-lab
title: "ArchWiz Markov recombining tree/trellis visualization and evaluation sandbox"
author: ChatGPT
posted_at: 2026-10-01
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
  - id: ChatGPT
    role: author+executor
    status: executing
related_issues: [966]
related_prs: [967]
related_branches:
  - experiment/archwiz-markov-trellis-lab
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — archwiz-markov-trellis-lab

## Summary

Isolate the supplied Gemini Markov visualization concept into a research lane that can be evaluated independently before any production ArchWiz integration.

## Architecture boundary

- Model layer: deterministic transition validation, tree expansion, trellis recombination, probability propagation, sampling.
- Presentation layer: standalone Canvas sandbox plus React/SVG reference.
- Evidence layer: deterministic tests, GitHub CI, Gemini adversarial review, and proposal review log.
- Production boundary: no routing, provider admission, telemetry SSOT, or context-relationship graph mutation.

## Review posture

Gemini is an external design/research reviewer for this lane. Its output is untrusted evidence and must be independently validated.

## Checklist

- [x] Registered in docs/proposals/registry.yaml
- [x] ITEMS.md itemized
- [x] Standalone implementation sandbox added
- [x] Deterministic model fixtures added
- [x] Gemini review request dispatched
- [ ] Gemini findings recorded and dispositioned
- [ ] repo-gate + termux-smoke green
- [ ] Evaluate graduation candidate(s)
- [ ] Close or promote proposal deliberately