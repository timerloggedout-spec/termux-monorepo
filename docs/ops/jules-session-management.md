# Jules session management — workflow contract

**Issue:** #145 · **PRs:** #148 (OPERATOR), #147 (Jules parallel)

## context_key

```text
context_key = pr-<number>-<short-head-ref>
```

- Stable across runs for the same PR head branch.
- Emitted in auto-jules and continuous-ops comment bodies.
- Cached under Actions cache key `work-context-<context_key>` (path `.agent-context/`).
- **Viewable text OK** on this public demo repo until #120 encrypted store.
- **Never** store Class 3/4 material (tokens, cookies, PoW, browser profiles).

## Continue-only default

When a recent `<!-- agent-auto-jules -->` or `<!-- continuous-agent-ops -->` marker exists for the PR, prefer **continue existing Jules session** over spawning a new task.

## Disposition-first

Piped instructions must cite **review disposition / open threads**, not analysis-chain probe scripts. See [`review-signal-alignment.md`](review-signal-alignment.md).

## Workflows

| Workflow | Role |
|----------|------|
| `agent-review-auto-jules.yml` | Event-driven: bot feedback → @jules with context_key + probe flag |
| `agent-continuous-ops.yml` | Scheduled: dirty/stale/blocked PRs → @jules with context_key |
| `agent-jules-on-issues.yml` | Issue label / @jules path (unchanged contract; may adopt context_key later) |

## Quota

Jules free tier: treat concurrent/daily limits as soft gates — skip with visible reason rather than silent spawn. Exact numbers: verify against current Jules docs; surface in skip comments.

## Related

- [`DECISION-MATRIX.md`](DECISION-MATRIX.md)
- [`OPERATOR-SIGNING.md`](OPERATOR-SIGNING.md)
- #120 (root durable store) · #118 · #124
