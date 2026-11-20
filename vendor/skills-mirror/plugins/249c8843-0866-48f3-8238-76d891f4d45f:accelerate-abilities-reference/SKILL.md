---
name: accelerate-abilities-reference
description: What can this toolkit do? Full list of available capabilities and data queries. Advanced reference for power users.
license: MIT
category: reference
parent: accelerate
---

# Accelerate — Capabilities reference

This is the internal reference for every Accelerate capability the toolkit can access. Use it when:

- The user asks "what can you do" or "give me the full list".
- Another skill needs to know whether a specific capability exists or what its inputs are.
- You need to pick the right capability for an unusual user question that doesn't fit a workflow skill.

Present the list to users in plain English, grouped by purpose. Do not show ability names, parameter names, or schemas unless the user explicitly asks for the technical detail (e.g., "I'm a developer, show me the raw list").

## For the user — plain-English overview

When a user asks "what can you do", respond with something like:

> I can help with four main things on your Accelerate site:
>
> **Understanding what's happening**
> Weekly / monthly / real-time performance reports, top content, traffic sources, engagement metrics (bounce rate, time on page, scroll depth), trending content, concurrent visitors, underperformance diagnosis, content comparison across time periods, author performance, taxonomy breakdown.
>
> **Running A/B tests**
> Propose test ideas grounded in your data, create tests with multiple variants, monitor live tests, declare winners, pause or stop tests, check experiment results with statistical confidence.
>
> **Personalising content**
> Define audience segments (by referrer, UTM, location, device, behaviour), attach personalised versions of reusable blocks to audiences, update or review existing audiences.
>
> **Analysing campaigns and attribution**
> UTM campaign performance, source breakdown, first-touch vs last-touch attribution, landing page analysis, channel comparison.
>
> What do you want to dig into?

Offer to route them into the right specialised skill from there.

## For the model — full technical reference

Every capability below is invoked via `mcp__wordpress__mcp-adapter-execute-ability` with the ability name and an input object matching the schema. Required inputs are **bold**.

### Understanding what's happening (read-only)

- **`accelerate/get-performance-summary`** — site, block, post, or experiment metrics. Inputs: `entity_type` (site|block|post|experiment, default site), `entity_id`, `date_range_preset` (1h|4h|12h|24h|7d|30d|90d), `date_range`, `granularity`, `segment`.
- **`accelerate/get-post-performance`** — detailed metrics for one post. Inputs: **`post_id`**, `date_range`.
- **`accelerate/get-top-content`** — best-performing content. Inputs: `type`, `limit` (1–50, default 10), `date_range`.
- **`accelerate/get-content-diff`** — period-over-period comparison. Inputs: **`post_ids`**, **`current_period`**, `comparison_period`.
- **`accelerate/get-traffic-breakdown`** — breakdown by country / browser / os / referrer. Inputs: `dimension` (default country), `date_range`, `limit`.
- **`accelerate/get-taxonomy-performance`** — performance by category / tag / taxonomy. Inputs: `taxonomy` (default category), `date_range`, `limit`. Output includes `underserved_score`.
- **`accelerate/get-site-context`** — site design system (colours, typography, spacing, blocks). Inputs: `blocks` (`none`|`styled`|`all`, default `none`). `include_blocks` remains accepted for older sites but is deprecated; use `blocks` for new calls.
- **`accelerate/get-engagement-metrics`** — bounce rate, time on page, scroll depth, recirculation, return visitor rate, exit pages. Inputs: `entity_type` (site|post), `entity_id`, `date_range`.
- **`accelerate/list-active-experiments`** — running tests and personalisation rules. Inputs: `type` (all|abtest|personalization), `post_id`.
- **`accelerate/list-experiments`** — historical and active experiments with pagination, status / type / date / annotation filters. Use this for "every experiment ever", not just live ones. Inputs: `status` (all|active|running|completed|paused|draft), `type` (all|abtest|personalization), `date_range`, `subject_post_id`, `annotation_key`, `annotation_value`, `page`, `per_page` (1–100, default 50). Returns paginated experiments with `total` and `pages`; each result includes `updated_at` and `result_revision` for safe historical-result refreshes.
- **`accelerate/get-audience-segments`** — defined audiences. Inputs: `include_estimates`.
- **`accelerate/get-audience-fields`** — available targeting fields. Inputs: `refresh`.
- **`accelerate/get-author-performance`** — metrics for one or all authors. Inputs: `author_id`, `date_range`, `limit`, `order_by` (views|conversions|conversion_rate|posts_count).
- **`accelerate/get-author-content`** — posts by an author with metrics. Inputs: **`author_id`**, `date_range`, `order_by`, `limit`.
- **`accelerate/search-content`** — find content by title / URL / text. Inputs: **`query`**, `search_in`, `post_type`, `limit`.
- **`accelerate/get-content`** — retrieve a post or page by ID or URL. Inputs: `id`, `url` (one is required; ID takes precedence when both are provided). Requires permission to edit content and the normal per-item reading permission.
- **`accelerate/get-media`** — list media-library items. Inputs: `limit` (1–100, default 20), `offset`, `search`, `mime_type`. Requires permission to upload files; private media stays scoped to content the account may read.

### Real-time

- **`accelerate/get-concurrent-visitors`** — live visitor count with polling guidance. Inputs: `post_id`, `active_window_minutes` (1–15, default 5), `include_breakdown`.
- **`accelerate/get-trending-content`** — content ranked by velocity (rising / flat / falling). Inputs: `window` (1h|4h|12h|24h, default 1h), `metric` (views|conversions|visitors), `content_type`, `limit`, `min_threshold`.

### Attribution and campaigns

- **`accelerate/get-attribution-comparison`** — first-touch vs last-touch breakdown with insights (best introducer / closer / most undervalued). Inputs: `date_range`, `conversion_goal`.
- **`accelerate/get-source-breakdown`** — traffic by source / medium / campaign / referrer_domain. Inputs: `date_range`, `group_by`, `limit`.
- **`accelerate/get-utm-performance`** — UTM metrics by campaign / source / medium / term / content. Inputs: `date_range`, `group_by`, `campaign`.
- **`accelerate/get-landing-pages`** — top entry pages. Inputs: `date_range`, `limit`.

### Running experiments (write, requires confirmation)

- **`accelerate/get-variants`** — inspect a block's current variants. Inputs: **`block_id`**. (Read-only.)
- **`accelerate/add-variant`** — add one variant to a block. Inputs: **`block_id`**, **`content`**, `title`, `percentage`, `audience_id`.
- **`accelerate/update-variant`** — modify an existing variant. Inputs: **`block_id`**, **`variant_index`**, `content`, `title`, `percentage`, `audience_id`.
- **`accelerate/remove-variant`** — delete a variant. Inputs: **`block_id`**, **`variant_index`**. Destructive.
- **`accelerate/create-ab-test`** — create a multi-variant test on a block. Inputs: **`block_id`**, **`variants`** (min 2), `hypothesis`, `goal` (engagement|click_any_link|submit_form), `traffic_percentage`, `annotations`. For a recoverable creation, include both `expected_content_hash` and a stable `request_id`.
- **`accelerate/restore-ab-test`** — restore a recoverable A/B-test creation only after showing the user the exact restoration and receiving confirmation. Inputs: **`block_id`**, **`request_id`**, **`expected_current_hash`**. It refuses to overwrite content that changed after the test was created.
- **`accelerate/set-block-goal`** — set a block's success metric. Inputs: **`block_id`**, **`goal`**.
- **`accelerate/set-traffic-percentage`** — adjust how much traffic enters the experiment. Inputs: **`block_id`**, **`percentage`**.
- **`accelerate/get-experiment-results`** — full results with winner recommendation and `selection_provenance` (`manual` or null), so a selected version is not mistaken for statistical evidence. Inputs: `block_id` or `experiment_id` (one is required), `refresh`. Use `experiment_id` for a completed experiment found through `list-experiments`.
- **`accelerate/stop-experiment`** — pause / resume / stop / declare winner. Inputs: **`block_id`**, **`action`** (pause|resume|stop|declare_winner), `winner_variant_index` (required for declare_winner).

### Personalisation (write, requires confirmation)

- **`accelerate/create-audience`** — define an audience. Inputs: **`title`**, **`rules`**, `description`.
- **`accelerate/update-audience`** — modify an existing audience. Inputs: **`audience_id`**, `title`, `description`, `rules`.
- **`accelerate/create-personalization-rule`** — attach personalised content to a block for an audience. Inputs: **`block_id`**, **`audience_id`**, **`personalized_content`**, `fallback_content`.
- **`accelerate/broadcast-content`** — push blocks site-wide. Inputs: **`block_ids`**, **`title`**. Destructive.

### Raw data (power users)

- **`accelerate/query-events`** — raw event queries with custom filters. Inputs: `filters`, `fields`, `date_range`, `limit`, `offset`.
- **`accelerate/get-event-schema`** — available event fields. Inputs: `refresh`.
- **`accelerate/aggregate`** — custom aggregations with flexible dimensions and metrics. Inputs: **`metrics`**, `dimensions`, `filters`, `date_range`, `limit`.
- **`accelerate/export-events`** — full event dump for a date. Inputs: **`date`** (YYYY-MM-DD), `format` (json|csv). Admin only.
- **`accelerate/get-export-status`** — check availability of exported data. Inputs: **`date`**.

## Rules

- Always check capability existence before suggesting it. If a user asks about something Accelerate doesn't support (multivariate tests, revenue, heatmaps, etc.), say so directly.
- The reference above is exhaustive for the current toolkit. If a capability you expected isn't listed, it genuinely isn't available.
- Permission tiers: read analytics accepts either `edit_posts` or `view_accelerate_analytics`; testing and audience changes require `edit_posts`; broadcasts, stopping experiments, and event exports require `manage_options`. Reading content and media has additional WordPress content permissions: `get-content` requires `edit_posts` plus the relevant post-reading permission, while `get-media` requires `upload_files` and keeps private items scoped. If a call fails with a permission error, tell the user their WordPress account needs the appropriate role and suggest they check with their site admin.
