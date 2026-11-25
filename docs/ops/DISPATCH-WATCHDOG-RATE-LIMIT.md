# Dispatch Watchdog — GitHub API Budget and Deferral

Status: implementation candidate on `fix/dispatch-watchdog-rate-limit-deferral-20261125`.

## Incident evidence

The 2026-11-25 08:20 UTC run [45575427717](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/45575427717) minted the Termux Fleet Swarm App token and completed checkout. Its first queue-discovery request then returned HTTP 403:

```text
API rate limit exceeded for installation ID 177357774
GET /repos/timerloggedout-spec/termux-monorepo/issues
    ?state=open&labels=dispatch-queued&per_page=100&page=1
```

The failed run skipped feed publication. Its diagnostic was recorded on [issue #4164](https://github.com/timerloggedout-spec/termux-monorepo/issues/4164). The issue had accumulated 137 comments, including 81 rate-limit diagnostics at the recorded inspection.

The failure is an exhausted App-installation core bucket. The minted token draws from a dedicated installation bucket shared by workflows using that same App installation. Repository metadata and authenticated connector reads remain available through a separate connection and permission context.

## Runtime controls

1. **Preflight:** read `GET /rate_limit` once before queue discovery. Derive the reserve as `max(100, floor(core.limit / 10))`.
2. **Admission:** after the queue page arrives, estimate the issue-list and per-issue comment-page reads. Defer before comment scanning when the projected reads would cross the reserve.
3. **Cheap reads:** skip the comments endpoint when the issue's comment count is zero.
4. **Rate-limit classification:** treat HTTP 429 and rate-limit-class HTTP 403 responses as deferrals. Use `X-RateLimit-Reset` or `Retry-After` to publish the defer-until time. Permission and other non-rate-limit 403 responses remain hard failures.
5. **Graceful state:** emit a workflow notice and summary, set the `deferred=true` step output, return success for the deferred cycle, and skip feed publication. The next scheduled cycle resumes the work.
6. **Diagnostic coalescing:** record failure evidence in the Actions run summary. Keep the issue ledger for durable task state rather than posting one diagnostic comment for every failed sweep.
7. **Partial-cycle recovery:** if a rate limit arrives after an action begins, stop the cycle and skip feed publication. The next sweep re-reads the issue state and uses the existing claim/flag/escalation markers to reconcile prior effects.

## Boundaries

- Keep the Termux Fleet Swarm App identity and current repository permissions.
- Keep the 15-minute scheduled recovery cadence; this change does not alter cadence ownership.
- Keep issue state, claims, leases, feed schemas, and promotion authority unchanged.
- Keep primary-rate exhaustion, secondary-rate controls, and permission failures as distinct classifications.
- Incremental comment-history reads remain a follow-up under rate-limit governance. Any cursor/ETag cache must preserve receipt age, current lease ownership, manual-claim precedence, user-activity detection, and stall-event history. Raw comment bodies remain outside the public cache.

## Validation

The focused suite in `scripts/dispatch/test_rate_limit.py` covers derived reserves, reset-aware 403 deferral, permission-error classification, graceful workflow output, queue-read admission, zero-comment optimization, and summary-only diagnostics.

Required evidence remains the exact-head repo gate and Termux smoke run, followed by a live watchdog cycle that either completes within the shared reserve or records a deferral and resumes after the reset window.

Related work: [rate-limit governance #5219](https://github.com/timerloggedout-spec/termux-monorepo/issues/5219), [QUE auto-claim #5286](https://github.com/timerloggedout-spec/termux-monorepo/issues/5286), and [lease idempotency PR #5859](https://github.com/timerloggedout-spec/termux-monorepo/pull/5859).
