---
description: Generate a performance report for recent email campaigns with metrics, trends, and recommendations.
argument-hint: "[campaign name or count]"
---

# /campaign-report

Generate a performance report for recent email campaigns.

## Instructions

When the user runs `/campaign-report`, produce a comprehensive campaign performance summary.

> **Server rule:** The MCP server does not compute aggregates. Report the per-campaign counts that `get_campaign` returns. Do **not** synthesize a blended "average open rate" or "total sends" across campaigns — present each campaign's own numbers and let the reader compare. If the user explicitly wants account-wide averages, tell them that lives in AC's native reporting.

### Steps

1. **Fetch recent campaigns**: Use `list_campaigns` with status "sent" to get the most recently sent campaigns. Default to the last 10 campaigns unless the user specifies a different range. (One call per turn; follow `next_page` only if you need more records to show.)

2. **Get per-campaign numbers**: For each campaign, use `get_campaign` to read the send count, open count, click count, bounce count, and unsubscribe count **as the API returns them**. If `get_campaign` returns a rate directly, show it; if it returns only raw counts, show the counts — do not derive new rates from a population the server told you not to aggregate.

3. **Get link performance**: For the few campaigns with the most clicks, use `get_campaign_links` to identify which links drove clicks.

4. **Present the report** in this format:

```
## Campaign Performance Report

### Campaigns (Last [N], status: sent)
| Campaign | Sent Date | Sends | Opens | Clicks | Bounces | Unsubs |
|----------|-----------|-------|-------|--------|---------|--------|
| ...      | ...       | ...   | ...   | ...    | ...     | ...    |

(Show each campaign's own counts exactly as returned. Include a rate column only if the API itself returned that rate.)

### Standouts
1. **[Campaign Name]** — highest opens/clicks in this set
   - Top link: [URL] ([X] clicks)

### Patterns
- [Qualitative observation grounded in specific campaigns — e.g. "your three most recent sends each had fewer opens than the one before"]

### Recommendations
- [Specific, actionable suggestion tied to the records above]

### Not measured here
- Account-wide averages/rates aren't available via MCP — see AC's native campaign reporting for those.
```

### Handling edge cases
- If no sent campaigns exist, tell the user and suggest creating their first campaign
- If the user specifies a campaign by name, use `list_campaigns` to search for it and report on that specific campaign
- If a campaign's returned numbers look unusual, flag it qualitatively and suggest possible causes (deliverability, list quality) — without inventing a rate the API didn't provide

### Arguments
- The user may optionally specify a campaign name, date range, or number of campaigns to include
- Example: `/campaign-report last 5` or `/campaign-report "March Newsletter"`
