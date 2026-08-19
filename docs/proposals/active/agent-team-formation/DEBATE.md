# DEBATE — agent-team-formation

## Term: agent-team-formation/1

**Driver:** Manus AI  
**Status:** Open for Operator and independent-review input.

## Decisions requested

| Decision | Options | Proposed default | Required authority |
|---|---|---|---|
| Canonical role names | Keep playful display names; adopt canonical names; map display aliases to canonical names. | Preserve display aliases, route and score through canonical team names. | Operator review. |
| Minimum evidence sample | Fixed task count; Bayesian confidence threshold; score decay only. | At least five independently evaluated tasks plus a confidence threshold before routing preference or any rotation decision. | Operator review and independent reviewer input. |
| Protected roles | None; security only; security + delivery + orchestration. | Security Assurance, Delivery Reliability, and Orchestration are protected from automatic cull/clone. | Operator review; security reviewer concurrence. |
| Score aggregation | Global ELO only; weighted role scores; role scores plus shared safety floor. | Role scores plus shared safety floor; aggregate ELO/3L0 is display-only and traceable. | Operator review and independent reviewer input. |
| PR #131 status | Treat as merged; treat as open; reconcile using commit evidence. | Reconcile using authoritative branch/commit evidence before any extension. | Delivery Reliability evidence; Operator disposition if records conflict. |
| APK intake | Start analysis from issue list; require artifact authorization. | Require authorization and provenance before any target is selected. | Operator approval per target; security review for elevated work. |

## Non-negotiable constraints

No proposal decision in this file authorizes credential changes, history rewriting, app-permission changes, third-party attacks, DRM/anti-cheat bypass, cracking, warez distribution, real-money wagering, or analysis outside documented authorization. Those matters remain human-only or out of scope.

## Review log

### 2026-08-18 — Manus AI

- **Disposition:** commented.
- **Evidence:** Existing repository governance requires social evidence for proposal acceptance; the live PR and lane SSOT disagree about PR #131's status.
- **Request:** The Operator should choose canonical naming and protected-role policy. A distinct reviewer should validate the scope and score controls before the proposal is promoted.
