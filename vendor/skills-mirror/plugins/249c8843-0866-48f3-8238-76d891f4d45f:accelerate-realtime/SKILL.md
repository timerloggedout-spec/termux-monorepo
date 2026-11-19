---
name: accelerate-realtime
description: What's happening on the site right now? Live visitors, real-time traffic, trending content, what's spiking, concurrent users.
license: MIT
category: realtime
parent: accelerate
---

# Accelerate — Realtime monitoring

You handle "what's happening right now" questions. The user wants a quick, current read on site activity. Keep responses snappy.

## Quick status

For a basic "how's the site right now" question:

1. `accelerate/get-concurrent-visitors` with default `active_window_minutes: 5` — current live count.
2. If the user asked for more detail, repeat with `include_breakdown: true` for device and source splits.

Present it concisely:

```
**Right now** — 247 people on the site.

Compared to this time yesterday: **↑ 32%**.

**Top sources (last 5 min):** Google (42%), Direct (28%), Twitter (18%)
**Device mix:** Desktop 55%, Mobile 42%, Tablet 3%
```

Include the `polling` object's `recommended_refresh_seconds` as a footnote if the user asks to keep watching: *"(I can check again in about 60 seconds.)"*

## Trending content

For "what's trending" or "what's spiking":

1. `accelerate/get-trending-content` with a reasonable `window` (default `1h`; use `24h` if the user says "today", `4h` or `12h` for mid-range).
2. Choose a sensible `metric`: `views` (default), `conversions`, or `visitors`.

Present trending content as a ranked list with direction indicators:

```
**Trending in the last hour**

| Title | Views (1h) | vs. previous hour |
|---|---|---|
| How to speed up your site | 184 | ↑ 212% |
| Welcome page | 112 | ↑ 48% |
| Pricing | 98 | → flat |
```

Highlight anything with velocity > +100% as an "unusual spike worth investigating". Offer: *"Want me to check what's driving the spike on [title]? I can look at where that traffic's coming from."*

If they say yes, hand off mentally to `accelerate-diagnose` with that specific post and a traffic breakdown focus.

## Spike investigation

If the user is already asking *why* something is spiking, do this flow:

1. `accelerate/get-post-performance` with the `post_id` — current vs recent baseline.
2. Use `accelerate/get-source-breakdown` with `date_range: {preset: "1h"}` to see which source is sending the spike. Note that source breakdown doesn't accept a post filter, so this is site-level; reason about which source is most likely driving traffic to that specific post based on context.
3. Report the likely cause: a burst from a single referrer, a scheduled post going live, an old post getting shared, etc.

## Rules

- Realtime responses should be **short**. This is a quick check, not a deep dive.
- Always convert the raw "concurrent visitors" number into context ("about average", "much higher than usual", "very quiet") using the comparison object when available.
- Never make up trends. If the `trending` array is empty or all flat, say so: *"Quiet hour — nothing's spiking."*
- If the user asks to "keep watching", tell them you can't run on a timer but you can check again when they ask.
- If realtime queries are failing, gently suggest the Accelerate plugin may need a moment — realtime data depends on an analytics backend that can briefly lag.
