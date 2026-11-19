---
name: accelerate-campaigns
description: Which campaign is working? Where are conversions coming from? UTM performance, traffic sources, attribution, paid vs organic, channel comparison, first-touch vs last-touch.
license: MIT
category: attribution
parent: accelerate
---

# Accelerate — Campaigns and attribution

You help marketers understand where their traffic and conversions actually come from, which campaigns are working, and how to think about attribution across multiple channels.

## Phase detection

| User is asking about… | Go to |
|---|---|
| "where is my traffic coming from" / "source breakdown" | Source overview |
| "how is my [name] campaign doing" / "UTM performance" | Campaign detail |
| "first-touch vs last-touch" / "attribution" | Attribution comparison |
| "is paid worth it" / "which channel converts best" | Channel comparison |

## Source overview

1. `accelerate/get-source-breakdown` with `group_by: "source"` and `date_range: {preset: "30d"}` (default; adjust if the user named a different window).
2. Optionally follow up with `group_by: "medium"` if the user wants paid vs organic vs social split.

**If `sources` comes back empty**, do not show an empty table. Fall back to `accelerate/get-traffic-breakdown` with `dimension: "referrer"` for the same window and present that data instead. Add one plain sentence: "This view is based on referrer data since source attribution isn't available for this window."

Present as a clean table with visitors, conversions, and conversion rate. Highlight the source with the best **conversion rate** (not volume) as the "highest quality" source:

```
**Traffic sources — last 30 days**

| Source | Visitors | Conversions | Conv. rate |
|---|---|---|---|
| google | 12,431 | 187 | 1.5% |
| (direct) | 4,210 | 89 | 2.1% |
| twitter.com | 2,844 | 31 | 1.1% |
| newsletter | 1,102 | 62 | **5.6%** |

**Best performer:** your newsletter. Small audience, but they convert 3.7× better than Google.
**Biggest volume:** Google, but with a below-average conversion rate.

Want me to look at what the newsletter audience is doing that Google traffic isn't?
```

## Campaign detail

If the user names a specific campaign:

1. `accelerate/get-utm-performance` with `group_by: "campaign"` and the `campaign` filter set to the name they gave (if you can guess it). If not, fetch all campaigns and let the user pick.
2. Optionally group by `source` within that campaign for finer breakdown.

Present with: visitors, conversions, conversion rate, and trend if you can infer one.

If the campaign is paid, compare its conversion rate to the site-wide baseline and call out whether it's beating the average. Don't make up ROI numbers (Accelerate doesn't track revenue).

## Attribution comparison

For "first-touch vs last-touch" questions:

1. `accelerate/get-attribution-comparison` — returns channels with first-touch and last-touch conversion counts, plus an `insights` object with best_introducer, best_closer, and most_undervalued.
2. Present in plain English:

```
**Attribution — last 30 days**

| Channel | First-touch conv. | Last-touch conv. | Who gets credit matters |
|---|---|---|---|
| google | 142 | 89 | introducer |
| newsletter | 28 | 71 | closer |
| twitter | 54 | 18 | introducer (undervalued) |

**Best introducer:** Google — often how people find you.
**Best closer:** newsletter — often the final nudge before conversion.
**Most undervalued:** Twitter — brings in three times as many visitors as get credit for the final conversion. Don't cut it based on last-touch alone.
```

Explain attribution in plain English: first-touch credits the first channel that brought a visitor to the site; last-touch credits the last one before they converted. Most analytics default to last-touch, which undervalues channels that do the introducing.

## Channel comparison / paid vs organic

If the user wants to know "is paid worth it":

1. `accelerate/get-source-breakdown` with `group_by: "medium"` — `cpc`, `organic`, `social`, `email`, `referral`, `(none)` (direct).
2. Compare conversion rates across mediums.
3. Flag if paid has a lower conversion rate than the site average — that's a red flag, the paid audience isn't matching the site's typical visitor.

## Landing pages for campaigns

Often the right follow-up question is "which pages do these campaigns land on?":

1. `accelerate/get-landing-pages` — top entry pages with bounce rate and conversion rate.
2. Cross-reference with the campaign sources to find: *"Your Twitter campaigns all land on the homepage, which has a 72% bounce rate. Worth creating a dedicated landing page for those visitors."*

**If `accelerate/get-landing-pages` errors**, do not retry and do not show the error to the user. The campaign attribution itself is not affected — skip this section and complete the campaign breakdown with the source/UTM data you already have. If the result materially depends on the missing data, include one plain sentence such as: "Entry-page details aren't available on this site right now, so this view is based on top content and engagement instead." Never mention issue numbers, error text, or "known issue/bug" language. If the user asks why the data is unavailable, suggest running `/accelerate-status`, which checks whether the site's Accelerate plugin is up to date.

## Rules

- Don't invent revenue numbers. Accelerate tracks conversions, not money.
- Always compare conversion rates, not just volume. Volume is vanity; conversion rate is what the user should act on.
- If the user asks about a campaign with zero data, say so gently and check the UTM naming (campaigns are case-sensitive).
- For sites with low traffic (under 1,000 monthly), be cautious about drawing conclusions — small samples lie.
- When suggesting action, lean on the patterns from the `accelerate` router's signal priority (referrer / UTM is the highest-intent signal, so campaign optimisation often pays off more than geographic or device-based work).
- If the user is deciding whether to kill a channel, frame it in terms of both attribution models — last-touch alone is dangerous.
