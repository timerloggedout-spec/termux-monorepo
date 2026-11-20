---
description: Generate a weekly marketing digest summarizing activity across campaigns, automations, contacts, and deals.
argument-hint: "[time range]"
---

# /weekly-digest

Generate a weekly marketing digest summarizing activity across campaigns, automations, contacts, and deals.

## Instructions

When the user runs `/weekly-digest`, produce a comprehensive weekly summary of their ActiveCampaign activity.

> **Server rule:** The MCP server does not compute aggregates or totals. Report the counts and per-record numbers the tools return. Do **not** sum deal values into a "total pipeline value", average campaign rates, or tally "contacts completed this week" by paging the whole dataset. Where you can only show records (not a total), show the records and say so. Point users to AC's native reporting for true roll-ups.

### Steps

1. **Campaign activity**: Use `list_campaigns` to find campaigns sent in the last 7 days. For a notable one, use `get_campaign` to read its returned counts. Show each campaign's own numbers — don't blend them.

2. **Automation activity**: Use `list_automations` to list active automations and the entered/completed counts carried on each record.

3. **Contact growth**: Use `list_contacts` with date filters to find contacts added in the last 7 days (show the count the query returns / the records). Use `list_lists` for list names and the subscriber counts the API returns per list.

4. **Deal activity**: Use `list_deals` filtered by status and date to show deals created / won / lost in the window as records, sorted by value where useful. Use `list_deal_pipelines` / `list_deal_stages` for pipeline context. Do not total the values — list the deals.

5. **Present the digest** in this format:

```
## Weekly Marketing Digest
**Week of [Date Range]**

---

### Campaigns Sent ([N] this week)
| Campaign | Date | Sends | Opens | Clicks |
|----------|------|-------|-------|--------|
| ...      | ...  | ...   | ...   | ...    |
(Counts as returned by the API. Include a rate column only if the API returned it.)

**Most opens/clicks this week**: [Campaign Name]

---

### Automations
- **Active automations**: [N]
- Notable per-automation movement this week (from the records): [e.g. "Welcome series — 40 entered"]

---

### Contacts
- **New contacts this week**: [N returned by the dated query]
- **Lists**: [list name — subscriber count as returned], …

---

### Deals (last 7 days)
| Deal | Status | Value | Stage |
|------|--------|-------|-------|
| ...  | won/open/lost | [as returned] | ... |
(Individual deals — not summed. For total pipeline value, see AC's native deal reporting.)

---

### Key Takeaways
1. [Most notable thing that happened, grounded in the records above]
2. [Area worth attention]
3. [Suggested action for next week]

### Not measured here
- Totals, averages, and blended rates aren't available via MCP — see AC's native reporting.
```

### Handling edge cases
- If no campaigns were sent this week, note it and show the most recent campaign for context
- If deals are not being used (no pipelines), skip that section
- If data is limited (new account), adjust the digest to show what's available and suggest setup steps

### Arguments
- The user may specify a different time range: `/weekly-digest last 14 days`
- Default is the last 7 days
