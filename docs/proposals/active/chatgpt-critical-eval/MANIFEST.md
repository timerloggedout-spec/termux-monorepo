---
id: chatgpt-critical-eval
title: "Critical Eval TER0-15 + other branches"
author: ChatGPT
posted_at: 2026-08-02
source: ../../../legacy-hint
status: executing
priority: P0
reviewers:
  - id: chatgpt
    role: author
    status: posted
  - id: grok-archw1z
    role: reviewer+executor
    status: accepted
related_prs: [2, 3, 5, 6, 9, 10, 11]
related_branches: [master-staging, termux-smoke, termux-monorepo]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — chatgpt-critical-eval

## Summary

Canonical recon of branch topology, PR readiness, security (session stores),
provider abstraction failures, DeepForge direction, and the recommended
integration spine. Authoritative for P0/P1 sequencing.

**Canonical text:** `docs/proposals/legacy/ChatGPT_Critical-Eval.md`
(flat original on `master`; mirrored under legacy/ on staging as available)

Also referenced as:
`docs/proposals/ChatGPT_Critical-Eval(TER0-15+other-branches).md` on `master`.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| chatgpt | author | posted | 2026-08-02 | Original eval |
| grok-archw1z | reviewer+executor | accepted | 2026-08-02 | Executing gate spine + specs |

## Review log

### 2026-08-02 — grok-archw1z

- Disposition: **accepted** (with execution priority order)
- Notes: Do not merge #2/#6 as-is. Promote repo-gate + termux-smoke first.
  Session SSOT elevated above TER-8. PR #9 best direction; #10 small win;
  #3 incomplete until A+B+C.

## Checklist (process)

- [x] Registered in `registry.yaml`
- [x] ITEMS.md itemized
- [x] Non-author review recorded (grok-archw1z)
- [x] Status → executing
- [x] PRs cite gates / disposition comments
- [x] repo-gate + termux-smoke live
- [ ] All P0 items terminal
- [ ] Closed + moved to `closed/`

## Links

- ITEMS: ./ITEMS.md
- Status board: ../../ARCHW1Z-STATUS.md
- Security: ../../SECURITY-REMEDIATION.md
