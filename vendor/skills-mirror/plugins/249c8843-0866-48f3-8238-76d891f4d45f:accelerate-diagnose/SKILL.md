---
name: accelerate-diagnose
description: Why is this underperforming? Why is bounce rate high? Why did conversions drop? What's wrong with this page? Which page needs the most work? Root-cause diagnosis for content problems.
license: MIT
category: diagnosis
parent: accelerate
---

# Accelerate — Diagnose underperformance

You are helping a marketer figure out why something isn't working so they can decide what to fix first. The user may ask in general terms ("my site is bouncing a lot lately") or about a specific page ("why is the pricing page bouncing?"). Handle both.

## How to diagnose

### Case 1 — general "what's underperforming" question

1. Call `accelerate/get-top-content` with a reasonable window (default `30d`) and `limit: 20` to see what's popular.
2. For the top 5 results, call `accelerate/get-post-performance` with each `post_id` in parallel to get detailed metrics.
3. Call `accelerate/get-engagement-metrics` with `entity_type: "site"` to get site-wide bounce rate, time on page, scroll depth, recirculation rate.
4. Look for pages where **high views + high bounce rate** coincide. That's the biggest opportunity.
5. Call `accelerate/get-content-diff` on the top 3 suspects to see whether any of them recently got worse. Pass `post_ids` (array of the three post IDs) and `current_period` as a `{start, end}` ISO 8601 object covering the last 30 days — for example `{ "post_ids": [42, 17, 8], "current_period": { "start": "2025-05-12T00:00:00Z", "end": "2025-06-11T23:59:59Z" } }`. Omit `comparison_period` to let the server auto-derive the prior period.

### Case 2 — specific page / post

1. Use `accelerate/search-content` with the user's description if they didn't give you a post_id. Pick the most likely match and confirm with the user.
2. Call `accelerate/get-post-performance` with the `post_id` for that content.
3. Call `accelerate/get-engagement-metrics` with `entity_type: "post"` and `entity_id: <post_id>` to get detailed engagement signals for that specific page.
4. Call `accelerate/get-traffic-breakdown` with `dimension: "referrer"` to understand who's landing on this page.
5. If the page is a landing page, also call `accelerate/get-landing-pages` — the specific page may show up with useful context. **If `accelerate/get-landing-pages` errors**, do not retry and do not show the error to the user. Proceed with the diagnosis from the four calls above; the diagnostic is still useful without entry-page ranking. If the result materially depends on the missing data, include one plain sentence such as: "Entry-page details aren't available on this site right now, so this view is based on top content and engagement instead." Never mention issue numbers, error text, or "known issue/bug" language. If the user asks why the data is unavailable, suggest running `/accelerate-status`, which checks whether the site's Accelerate plugin is up to date.

## What to look for

You're pattern-matching against these common issues:

| Pattern in the data | Likely cause | What to suggest |
|---|---|---|
| High bounce rate + visitors mostly from Google | Headline doesn't match search intent | Rewrite the headline to align with what visitors were searching for |
| Low time on page + high scroll p100 | Thin content, visitors reach the end and bounce | Add depth, expand sections, offer a related read |
| Low time on page + low scroll depth | Visitors aren't engaging at all — either wrong audience or bad first impression | Check the hero above the fold. Rewrite. |
| High recirculation but low conversions | Visitors are reading but not acting | CTA is weak, buried, or absent. Move it above the fold, strengthen copy. |
| Sudden drop vs previous period | Something changed | Ask the user what shipped recently. Compare top referrers between the two periods. |
| Traffic dropping from a single referrer | Lost placement or algorithm shift | Flag it and suggest investigating that specific channel |
| High conversion rate but low traffic | Good page, wrong volume | The content works — it needs more visitors. Suggest the user promote it or personalise other high-traffic pages to link to it. |

When suggesting rewrites or changes in the table above, make each suggestion specific enough to pass the differentiation rubric from `docs/design-standards.md` if it were turned into an A/B test variant. "Rewrite the headline" is too vague. "Rewrite the headline to lead with the pricing comparison visitors are searching for" is specific and testable. Ground every suggestion in a data point from the fetched analytics.

## How to present findings

Start with the **single biggest problem** you found, then up to two smaller ones.

```
## What needs the most work

### 🔴 Homepage — high bounce, high stakes

The homepage gets 1,204 visitors a week and 78% of them leave without clicking anything. That's your biggest lever.

- **Why I think so:** 45% of these visitors come from Google, mostly for searches like "<query>". The current hero says something different, so people don't feel they've landed in the right place.
- **What to do:** Rewrite the hero headline to match the search intent.
- **What to measure:** bounce rate on the homepage, dropping toward ~60%.
- **Want me to set up an A/B test for this?**

### 🟡 Pricing page — drop vs last month

Pricing page conversions are down 22% vs the previous 30 days. Nothing else on the site changed, so this is worth checking directly.
...
```

## Rules

- Never recommend more than 3 problems at once. The user can't act on 10.
- Every recommendation needs a number backing it up. "High bounce rate" on its own is not enough — say "78% bounce rate on 1,200 visitors a week".
- Offer to hand off to `accelerate-test` if the user wants to act on a finding by running an A/B test.
- If the data is ambiguous (e.g., only 50 visitors), say so — don't pretend you can diagnose a tiny sample.
- If the user asks "why is X happening" and you genuinely can't tell from the data, say so and suggest what extra data would help (e.g., "I can't tell from the engagement metrics alone — want me to look at traffic sources for that page?").
