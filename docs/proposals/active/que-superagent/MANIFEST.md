---
id: que-superagent
title: "QUE ⇐ dsh-superagent domain model (Mandate, Report, serial Eval, fan-out, shadow)"
author: Hark
posted_at: 2026-11-15
source: LESSONS.md
status: executing
priority: P1
reviewers:
  - {id: timerloggedout-spec, role: operator-authorizer, status: accepted}
related_prs: [5483]
related_branches: [hark/que-superagent-p1]
gates_required: [repo-gate]
---

# MANIFEST — que-superagent

## Summary

Port the dsh-superagent domain rules (Trigger ⇒ Eval ⇒ Ticket, immutable Mandate, Report enum, structured Attention, Subscription fan-out, shadow mode, attention-first panel) into QUE. Map: `LESSONS.md`. Issue: #5482 (parent #5232). Templates: `refTemplates/06_Task_Tracking/que-superagent/`.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| timerloggedout-spec | operator-authorizer | accepted | 2026-11-15 | Owner dispatch main→que-superagent |
| Hark | author+executor (P1) | executing | 2026-11-15 | P2–P4 ⇒ termux-ops loop runner |
