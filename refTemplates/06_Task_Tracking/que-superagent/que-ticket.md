# [QUE·item] {short title}

Thread: #{issue_or_pr} · Source: github · receiving scope: {issues.new | comment | pr | ci}
Owner: LoggedOut Timer

## Scope

{What this item may do, in one or two sentences. Wider scope ⇒ new item, ¬ edit this one.}

## State

ticket: open | ended · ended by: {ready | dropped | stopped-by-person | revoked}
assignment: pending | running | ended · lease: {executor 120m | seat-queue 240m}
latest report: {progress | waiting | ready | blocked | failed | dropped} · see que-report

## Mandate (immutable)

<!-- que-mandate/v1
{
  "schema": "que-mandate/v1",
  "policy_version": "{e.g. queue.dispatch-tiers/v2@1a2b3c4d}",
  "scope": "{template or route this item may act on}",
  "strength": "explicit",
  "matched_rules": ["{rule id}"],
  "source": "github",
  "receiving_scope": "issues.new",
  "sender": "{login on this Source}",
  "trigger_id": "{hark-key or comment id}"
}
-->

Rules: only accept creates it · a person's stop withdraws it · failed revalidation against the current policy revokes it · ¬ edited in place.

## Subscriptions

- #{thread} (origin, ¬ droppable)
- #{related} (context only: no authority, ¬ resumes)
