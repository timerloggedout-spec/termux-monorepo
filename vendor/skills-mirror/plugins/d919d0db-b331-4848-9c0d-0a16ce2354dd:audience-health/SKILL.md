---
description: Analyze contact list health, engagement levels, and data quality with cleanup recommendations.
argument-hint: "[list name]"
---

# /audience-health

Analyze contact list health, engagement levels, and data quality.

## Instructions

When the user runs `/audience-health`, produce a comprehensive health assessment of their contact database.

> **Server rule:** The MCP server does not compute aggregates or percentages, and you must not page the entire contact database to derive them. Use each `list_*` query's returned count for a given status filter (one call per turn per tool), and present those counts as-is. Do not turn them into percentages of a fabricated total, and do not compute an "average field completion %". Where you can only sample, label it clearly as a sample, not a measured rate.

### Steps

1. **List overview**: Use `list_lists` to get lists and the subscriber counts the API returns per list.

2. **Contact status counts**: Use `list_contacts` filtered by status, one status per query as needed, and report the count each query returns: active, unsubscribed, bounced, unconfirmed. Present them as raw counts side by side — do not convert to percentages of a total.

3. **Tag analysis**: Use `list_tags` to assess tag usage qualitatively — how many tags exist, whether naming looks consistent, signs of ad-hoc/over-tagging.

4. **Custom field coverage**: Use `list_contact_custom_fields` to see what fields exist. You may `get_contact` on a *small sample* to illustrate which fields tend to be filled — present this explicitly as anecdotal sampling, never as an "average completion %".

5. **Engagement sampling**: Use `list_email_activities` to sample recent engagement and describe, qualitatively, who is engaging recently vs. who looks dormant. Label these as observations from a sample, not full-population segment sizes.

6. **Present the health report** in this format:

```
## Audience Health Report

### Contact Status (counts as returned per status query)
| Status | Count |
|--------|-------|
| Active | [N] |
| Unsubscribed | [N] |
| Bounced | [N] |
| Unconfirmed | [N] |
(Raw counts from each filtered query — not percentages of a total.)

### Lists
| List | Subscribers (as returned) | Notes |
|------|---------------------------|-------|
| ...  | ...                       | ...   |

### Engagement (from a sample, not a full census)
- Recently engaged (opened/clicked, last ~30d): observed in the sample
- Looks dormant (no recent activity in the sample): …
> These are qualitative observations from sampled activity. For true engagement segment sizes, build a segment in AC.

### Data Quality
- **Custom fields defined**: [N]
- **Fields that looked sparsely filled in the sample**: [names] (anecdotal, from sampled contacts)

### Tag Organization
- **Total tags**: [N]
- **Naming consistency**: [qualitative read]
- **Suggestions**: [specific tag cleanup recommendations]

### Recommendations

#### Immediate Actions
1. **Review bounced contacts** — [N, the returned count] bounced contacts can hurt deliverability
2. [Other immediate action]

#### Short-term Improvements
1. **Re-engagement campaign** — for contacts that look dormant
2. [Other improvement]

#### Long-term Strategy
1. **Sunset policy** for long-inactive contacts
2. [Other strategic recommendation]

### Not measured here
- Percentages, averages, and full-population engagement segment sizes aren't available via MCP — build a segment in AC or use native reporting for those.
```

### Handling edge cases
- If the contact database is small (<100), focus on data quality and growth opportunities rather than engagement sampling
- If no email activities are available, skip the engagement section and note that tracking data will build over time
- If custom fields aren't being used, recommend key fields to add for better segmentation

### Arguments
- `/audience-health` — full health report
- `/audience-health [list name]` — focus on a specific list
