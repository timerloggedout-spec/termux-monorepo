# Legacy Google Jules PR Request Receipt

This lane records trusted PR-scoped @jules comments as legacy request evidence. Google Jules became read-only after 2026-11-11 and is scheduled to wind down on 2026-12-31.

## Receipt state

`LEGACY_REQUEST_RECORDED`

The receipt captures:
- trusted initiator and source comment ID;
- PR branch, exact baseline head SHA, and base SHA;
- local DoE role guidance and canonical role register;
- workflow run URL and idempotency marker.

## Local DoE role handoff

Use the canonical DoE role register and active provider roster:

- `docs/ops/DOE-ROLES-EPOCH-2026-11-03.md`
- `docs/schemas/agent-roster.yaml`

The locally adapted issue-analysis and action-verification skills are tracked in PR #5722. They map the upstream patterns to observer, scout, builder, operator, steward, reviewer, participant, and gambler duties. Provider execution remains under the live agent roster and verified adapter contract.

## Provenance boundary

Trusted human initiators are limited to OWNER, MEMBER, or COLLABORATOR author associations. The workflow re-fetches the source comment before recording a receipt. Receipt comments are authored by github-actions[bot] and carry an idempotency marker tied to the source comment ID.

## Authority boundaries

- Treat the receipt as historical request evidence.
- Route new implementation through the current agent roster and a verified live adapter.
- Evaluate fresh checks against the exact candidate head.
- Use provider output as supporting evidence and inspect the resulting diff, checks, reviews, and provenance independently.
- Keep merge, force-push, and promotion under the repository's established review and governance controls.

## Historical mutation-observation contract

The 2026-11-19 rate-limit optimization introduced a pending-label gate and a PR synchronization mutation scan. That state machine applied to live Google Jules delegation. The read-only service cutoff retires that execution assumption; the current workflow records the legacy request once and removes the synchronization scan.
