---
id: auditengine-adapt
title: "RinDig AuditEngine (Ethics Engine) adapt pass"
author: timerloggedout-spec
posted_at: 2026-09-10
source: operator-directive
status: draft
priority: P2
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_prs: []
related_branches: []
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — AuditEngine Adapt

## Summary

Adapt RinDig/AuditEngine (Ethics Engine — psychometric assessment of LLMs) after the cost-of-remembering evidence lane lands. Scope: own fork, shallow reference pin under `refTemplates/smods/`, native knowledge/operations card, **no** automatic Vercel/Railway deploy, **no** API-key custody in monorepo.

## Upstream

- https://github.com/RinDig/AuditEngine
- Live demo reference: ethicsengine.eduba.io
- Stack: Next.js frontend + FastAPI backend; scales RWA/LWA/MFQ/etc.

## Boundary

- Reference + adapt patterns only until operator authorizes a runtime surface.
- Provider keys stay outside monorepo secrets unless a separate Tier-4 proposal is accepted.

## Checklist

- [ ] Fork `AuditEngine_fork` (or `AuditEngine`) under timerloggedout-spec
- [ ] Knowledge/operations card
- [ ] `.gitmodules` + gitlink
- [ ] template-candidates entry
- [ ] PR against master-staging/master

## Depends on

- cost-of-remembering-integration (PR #485) preferred first
