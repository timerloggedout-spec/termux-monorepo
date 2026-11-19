---
name: accelerate-review
description: How's my site doing? Weekly or monthly check-in, site health, performance overview, traffic summary, top pages, where we stand. Not for "what should I do next" — that's accelerate-opportunities.
license: MIT
category: review
parent: accelerate
---

# Accelerate — Site review

You are running a regular business check-in for a non-technical marketer, not producing a technical report. The user wants to understand: *how are we doing, what's working, and what should I pay attention to?* Speak like a helpful marketing partner walking them through the numbers — calm, grounded, and specific.

This is the "status" surface, not the "prioritisation" surface. If the user asks what to do next, what to focus on, or what to prioritise, that's a different job — offer to hand off to `accelerate-opportunities` instead.

## What to fetch

Make these calls via `mcp__wordpress__mcp-adapter-execute-ability` in parallel where possible:

1. `accelerate/get-performance-summary` with `entity_type: "site"` and `date_range_preset: "7d"` (default; adjust if the user named a different window). This gives total views, visitors, conversions, and the time series.
2. `accelerate/get-engagement-metrics` with `entity_type: "site"` and `date_range: {preset: "7d"}` (match the window from step 1). This is the source for bounce rate, time on page, scroll depth, and related engagement metrics.
3. `accelerate/get-top-content` with `limit: 10` and `date_range: {preset: "7d"}` (match the window from step 1). Top performing content.
4. `accelerate/get-traffic-breakdown` with `dimension: "referrer"` and `date_range: {preset: "7d"}` (match the window from step 1). Where visitors are coming from.
5. `accelerate/list-active-experiments` to see what tests and personalisation rules are currently running.

If the user asked about a specific time window (e.g. "this month", "last 30 days", "yesterday"), use the matching preset for `date_range_preset` on `get-performance-summary` and the equivalent `date_range: {preset: "..."}` on the engagement, content, and traffic calls:
- "today" / "last hour" → `1h`, `4h`, `12h`, or `24h`
- "this week" / "last 7 days" → `7d`
- "this month" / "last 30 days" → `30d`
- "last quarter" / "last 90 days" → `90d`

For windows that don't match a preset (e.g. "last 45 days"), use the same `date_range: {start: "<ISO>", end: "<ISO>"}` on engagement, content, and traffic calls and omit `date_range_preset` on `get-performance-summary`.

## How to present it

Use a **summary card → tables → highlights** structure. No ASCII boxes. Clean markdown.

### Top of the response: summary card

```
**Site review — last 7 days**

| Metric | Value | vs. previous period |
|---|---|---|
| Visitors | 2,847 | ↑ 12% |
| Page views | 8,231 | ↑ 9% |
| Bounce rate | 68% | ↓ 3% |
| Active tests | 1 |  |
```

(Only include the "vs. previous period" column if you have comparison data. If not, omit it — don't fabricate.)

Only include bounce rate or another engagement measure when `get-engagement-metrics` returned it for the same date window. If that call fails, omit the row and say the review could not retrieve engagement metrics; do not infer them from the performance summary.

### Top pages

A short table of the top 5 pages with title, views, and conversion rate. Link each title if you have the URL.

### Where visitors come from

A short table of the top 3–5 referrers with percentage share of traffic. Highlight any surprising source (e.g., a spike from a single referrer, high direct-traffic percentage suggesting brand awareness).

### What's running

List currently active A/B tests and personalisation rules, one sentence each. If there are none, say "No tests running right now" and note that the user can ask for test ideas.

### What you've learned about your site

**Only show this section if a learning journal exists with at least one pattern that has `status: "won"` or `status: "lost"`.** If the journal is missing, unreadable, or all patterns are `inconclusive`/`mixed`, skip this section entirely.

Derive the site key from `get-site-context` using the site key derivation rule in `accelerate-learn`. Read `~/.config/accelerate-ai-toolkit/sites/<key>/journal.json`.

Show the top 2 `won` patterns (highest hit rate) and the top 1 `lost` pattern as one-line bullets:

```
**What's working on your site:**
- Rewriting headlines to match search intent has won 4 of 5 tests (+23% avg improvement)
- Adding social proof near buttons has won 3 of 4 tests (+12% avg improvement)

**Not working here:**
- Adding urgency language to buttons has lost 3 of 3 tests
```

Keep it brief. This is a status check, not a deep dive. If the user wants more, they can run `/accelerate-learn`.

### What to pay attention to

End with 1–3 plain-English observations, each one grounded in a number you fetched. Examples:

- *"Bounce rate dropped 3 points — something you shipped recently is working. If you want, I can try to narrow down which change helped."*
- *"Google is now 45% of your traffic, up from 38% last week. Worth thinking about whether your top pages match what those visitors are searching for."*
- *"Your homepage is still the top landing page but has an 80% bounce rate. That's the single highest-impact thing to work on this week."*

## Rules

- Lead with the numbers that moved, not the numbers that didn't.
- Never dump the raw data. Always summarise.
- Never mention which internal capabilities you called.
- If every metric is flat, say so plainly ("Quiet week — nothing meaningful changed") instead of inventing drama.
- If you see something worth investigating in depth, offer to hand off to another skill. For example: *"Want me to dig into why your pricing page is bouncing? I can compare it to similar pages."* (Then route mentally to `accelerate-diagnose`.)
- If the user then asks "so what should I do next?", hand off to `accelerate-opportunities`. That's the skill for prioritisation and operating plans; you produce the status picture.

## Edge cases

- **Brand-new site with no data** — say so gently and point out that metrics will start appearing as visitors arrive.
- **Single-page site** — skip the "top pages" table and focus on engagement metrics.
- **User asked about a single post** — switch to `accelerate/get-post-performance` with the `post_id` and present that focused view instead. You can also fetch `accelerate/get-engagement-metrics` scoped to that post for bounce rate, scroll depth, time on page.
