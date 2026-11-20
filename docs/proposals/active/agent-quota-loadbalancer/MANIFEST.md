# MANIFEST — agent-quota-loadbalancer

## Summary

Free-tier agent quotas (Gemini 20 req/day, Jules 15/day with 3 concurrent,
CodeRabbit per-PR limits) are being exhausted by un-throttled CI dispatch.
This proposal introduces:

1. **Quota throttling** — a daily counter gate that skips Gemini jobs when the
   free-tier limit is reached, posting a friendly comment instead of failing CI.
2. **Session continuation** — Gemini review context is cached per-PR so that
   `synchronize` pushes only re-review changed files, not the whole PR.
3. **Load balancing** — a central dispatch router that routes review/triage/invoke
   tasks across available agents (Gemini, Jules, CodeRabbit, Devin) based on
   live quota and concurrency, falling back gracefully.
4. **Capacity maximization** — agent capability registry + utilization tracking
   so work is distributed to the agent with the most headroom.

## Motivation

PR #63 CI showed 14 failing workflows because Gemini's free-tier quota
(20 `generate_content_free_tty_requests`/day on `gemini-3.5-flash`) was
exhausted by multiple PR events firing in parallel. The quota resets daily
but CI had no throttling — every `opened` / `synchronize` / `ready_for_review`
event dispatched a Gemini job, and once the quota ran out, all subsequent
runs hard-failed with `TerminalQuotaError`.

Jules demonstrates the desired pattern: 15/day with 3 concurrent, but one
session can continue through many PR revisions and different PR review
requests, running for an extended period. Gemini (and other agents) need
the same session-continuation discipline.

## Design

### Quota gate (`.github/actions/gemini-quota-gate/`)

A composite action that:

- Reads a daily counter from the GitHub Actions cache
  (`gemini-quota-YYYY-MM-DD`, value = requests consumed today)
- If counter >= `GEMINI_FREE_TIER_DAILY_LIMIT` (default 18, leaving 2 as
  safety margin): sets `skip=true`, posts a graceful comment, exits 0
- Otherwise: increments the counter atomically and sets `skip=false`
- The counter is scoped per-day; stale keys from previous days are ignored

### Session continuation (cache-based)

- `gemini-review.yml` caches the review output per-PR-number + commit SHA
- On `synchronize`, if the cached review exists for the current SHA, the job
  posts "already reviewed" and skips
- On subsequent pushes, only files changed since the last-reviewed SHA are
  passed to Gemini (reduces token usage and API calls)

### Load balancer (`.github/workflows/agent-load-balancer.yml`)

A reusable workflow that:

- Enumerates available agents and their current capacity
- Routes the task to the agent with the most headroom
- Falls back to CodeRabbit (always available, per-PR limits) or a human
  ping if all AI agents are exhausted

## Review log

| Reviewer | Role | Status | Notes |
|----------|------|--------|-------|
| tembo | author+executor | posted | Initial implementation |

## Related PRs

- #63 (trigger: Gemini quota exhaustion CI failure)
