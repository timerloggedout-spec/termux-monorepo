---
description: Review active automations and surface ones worth attention — entered/completed counts, likely drop-off, stale workflows, and recommendations.
argument-hint: "[automation name]"
---

# /automation-audit

Review automation performance and identify automations that need attention.

## Instructions

When the user runs `/automation-audit`, analyze all active automations and surface issues, opportunities, and recommendations.

> **Server rule:** The MCP server does not compute aggregates, so a true account-wide "completion rate" or "average duration" is not available. `list_automations` returns each automation's name, status, and the contact counts the API exposes on the record itself (e.g. entered / completed counts). Report those per-automation numbers as returned. Do not page through `list_contact_automations` for every contact to compute a rate yourself — that violates the server's rules and is what AC's native automation reporting is for. Frame "needs attention" qualitatively from the per-record numbers, not from a threshold you calculated across the dataset.

### Steps

1. **Get all automations**: Use `list_automations` to fetch automations and their status (active/disabled) plus whatever entered/completed counts the records carry. (One call per turn; follow `next_page` only to show more automations.)

2. **Read per-automation signals from the records themselves**: For each automation, use the counts already present on the `list_automations` record — entered count, completed count, status. If the user wants detail on one specific automation, you may use `list_contact_automations` filtered to *that* automation to show individual run statuses — but describe them qualitatively, don't compute a fleet-wide percentage.

3. **Flag qualitatively** (based only on the returned per-record numbers):
   - Automations where the record shows many entered but few completed — note as a possible drop-off to investigate in native reporting
   - **Stale** — active but the record shows little/no recent entry
   - **No goals set** — automations without a measurable outcome
   - **Possible overlap** — multiple automations that appear to target the same audience

4. **Present the audit** in this format:

```
## Automation Audit

### Overview
- **Active automations**: [N]   **Disabled**: [N]

### Active Automations
| Automation | Status | Entered | Completed | Notes |
|-----------|--------|---------|-----------|-------|
| ...       | active | [as returned] | [as returned] | [qualitative flag] |

(Show counts exactly as the API returns them. The "Notes" column is your qualitative read — e.g. "many entered, few completed — worth a look in native reporting" — not a computed rate.)

### Worth a closer look
- [Automation] — [why, in plain language, citing its returned counts]

### Inactive (Disabled)
| Automation | Notes |
|-----------|-------|
| ...       | Consider reactivating or archiving |

### Recommendations
1. [Highest priority action]
2. [Second priority]

### Not measured here
- Completion rates, average durations, and goal-conversion percentages aren't computed via MCP — use AC's native automation reporting for those.
```

### Handling edge cases
- If no automations exist, explain the value of automations and suggest starting with a welcome series
- If everything looks healthy from the returned counts, say so and suggest optimization opportunities (A/B testing, adding goals)
- If there are many automations (20+), focus on the ones whose returned counts suggest drop-off or staleness, and list the rest by name

### Arguments
- `/automation-audit` — audit all active automations
- `/automation-audit [name]` — audit a specific automation by name
