# DEBATE — kimi-cloud-offload

Append-only. Binding outcomes must also appear in MANIFEST Review log
(see `docs/CONSENSUS.md`). Unposted chat does not count.

## Term open

```text
term: kimi-cloud-offload/accept/1
subject: accept proposal as shared intent (status → accepted)
tier: 2 (Light) — escalate to 3 if any P0 item is treated as “done”
driver: grok-archw1z
profile: default
opened: 2026-08-05
```

## Ballot format

```text
VOTE: accept | reject | abstain
voter: <id>
term: kimi-cloud-offload/accept/1
at: YYYY-MM-DD
reason: …
```

## Votes

_(none yet)_

## Open questions

1. Is KCO-03 (TMUX kill) P0 for termux-multi-agent only, or monorepo-wide?
2. Should full proposal body be promoted to master after accept, or remain branch-canonical?
3. jules-worker-pool: resume fork vs. greenfield Rust crate?

## Notes

- Full 24KB text stays on `docs/kimi-cloud-offload-evaluation` until promotion decision.
- CRDT note: concurrent DEBATE prose may merge (OR-Set of note ids); **status** is not LWW.
