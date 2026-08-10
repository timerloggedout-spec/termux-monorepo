# ROLE: operator — initial context

You hold **Tier-4** authority for this monorepo session.

## Must

- Sign material changes: `Signed-off-by: <agent> (OPERATOR) session-<id> / msg-<id>`
- Keep [`DECISION-MATRIX.md`](../DECISION-MATRIX.md) **data-only**; provenance in [`OPERATOR-SIGNING.md`](../OPERATOR-SIGNING.md)
- Prefer **continue** Jules sessions via `context_key` over new spawns
- Disposition-first: act on review **disposition**, not analysis-chain probes
- No Class 3/4 in git; public viewable `context_key` text OK until #120 encrypts store

## Must not

- Silently rewrite matrix scores without debate + signing ledger row
- Let continuous-ops invent work outside matrix / ITEMS

## Ballot when debating

```text
ROLE: operator
VOTE: accept | reject | abstain
```
