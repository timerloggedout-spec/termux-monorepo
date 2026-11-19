# Agent/Jules PR Handoff Evidence Contract

This lane makes PR-scoped `@jules` delegation observable while separating dispatch, mutation, fresh gates, and verification.

## State machine

`DISPATCHED -> MUTATION_OBSERVED -> FRESH_GATES -> VERIFIED`

- **DISPATCHED** records the trusted initiator, PR branch, exact baseline head SHA, base SHA, context key, and source comment ID.
- **MUTATION_OBSERVED** is emitted only after a subsequent PR synchronization proves the head SHA changed from the recorded baseline.
- **FRESH_GATES** requires checks evaluated against the exact observed head, not merely a merge ref or an earlier commit.
- **VERIFIED** is a steward disposition after independent inspection of the resulting diff, checks, reviews, and provenance.

## Provenance boundary

Trusted human initiators are limited to `OWNER`, `MEMBER`, or `COLLABORATOR` author associations. The only automation initiator admitted by the workflow is `github-actions[bot]`; other bots must not create a handoff receipt merely by mentioning `@jules`.

The workflow re-fetches the source comment before accepting it as evidence and re-validates its provenance when processing a later synchronization event. Receipt comments are authored by `github-actions[bot]` and carry an idempotency marker tied to the source comment or observed head SHA.

## Authority boundaries

- Treat the dispatch comment as initiation evidence.
- Verify a later head mutation against the exact recorded baseline SHA.
- Evaluate fresh checks against the exact observed head.
- Use provider output as supporting evidence and inspect the resulting diff, checks, reviews, and provenance independently.
- Keep merge, force-push, and promotion under the repository's established review and governance controls.


## API load control — 2026-11-19

The PR synchronization path uses the `jules-handoff-pending` label as an event-payload gate. The trusted `@jules` handoff path creates the label after its idempotency check and before posting the dispatch receipt. The mutation job paginates PR comments only while that label is present, records `MUTATION_OBSERVED`, and clears the label after the receipt. Duplicate mutation receipts also clear the pending label.

Both `actions/github-script` steps use the immutable v7.1.0 commit pin. The gate reduces comment-list API calls across ordinary PR synchronization events while preserving the existing trusted-actor, source-comment, baseline-SHA, and independent-verification checks.

The 2026-11-19 PR #5664 check run recorded a GitHub App installation API rate-limit response in the mutation job. The label gate addresses the high-frequency scan path; the workflow's trusted handoff and mutation receipts remain the authority for Jules delegation state.
