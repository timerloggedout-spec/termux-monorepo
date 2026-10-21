# Agent/Jules PR Handoff Evidence Contract

This lane makes PR-scoped `@jules` delegation observable without treating delegation as execution or completion.

## State machine

`DISPATCHED -> MUTATION_OBSERVED -> FRESH_GATES -> VERIFIED`

- **DISPATCHED** records the trusted initiator, PR branch, exact baseline head SHA, base SHA, context key, and source comment ID.
- **MUTATION_OBSERVED** is emitted only after a subsequent PR synchronization proves the head SHA changed from the recorded baseline.
- **FRESH_GATES** requires checks evaluated against the exact observed head, not merely a merge ref or an earlier commit.
- **VERIFIED** is a steward disposition after independent inspection of the resulting diff, checks, reviews, and provenance.

## Provenance boundary

Trusted human initiators are limited to `OWNER`, `MEMBER`, or `COLLABORATOR` author associations. The only automation initiator admitted by the workflow is `github-actions[bot]`; other bots must not create a handoff receipt merely by mentioning `@jules`.

The workflow re-fetches the source comment before accepting it as evidence and re-validates its provenance when processing a later synchronization event. Receipt comments are authored by `github-actions[bot]` and carry an idempotency marker tied to the source comment or observed head SHA.

## Non-authority rules

A comment is not completion. A changed SHA is not correctness. Provider prose is evidence only. This workflow never merges, force-pushes, or promotes a PR.
