---
description: Review deal pipeline structure and surface deals by stage, top deals by value, and likely stuck deals.
argument-hint: "[pipeline name]"
---

# /deal-pipeline-review

Analyze deal pipeline health, velocity, and conversion across stages.

## Instructions

When the user runs `/deal-pipeline-review`, produce a comprehensive analysis of their sales pipeline.

> **Server rule:** The MCP server will not compute win rate, average deal value, total stage value, conversion rate, or time-in-stage, and you must not page the whole deal set to derive them. Show the deals and the counts each query returns, sorted by a supported field (e.g. value). Frame bottlenecks and risk qualitatively from the records you can see. For true pipeline aggregates, point the user to AC's native deal reporting.

### Steps

1. **Get pipeline structure**: Use `list_deal_pipelines` to get pipelines, then `list_deal_stages` to read each pipeline's stage flow.

2. **Get deal records by status**: Use `list_deals` filtered by status — open, won, lost — and sorted by value where useful. Report the count each query returns and show the deals. (One call per status per turn; follow `next_page` only to show more deals.)

3. **Read deals per stage**: Show how many deals each query surfaces in each stage and list them. Do not sum stage values into a total or compute a stage-to-stage conversion rate.

4. **Deal activity**: Use `list_deal_activities` on a few notable deals to describe recent movement qualitatively.

5. **Present the review** in this format:

```
## Deal Pipeline Review

### Pipeline: [Pipeline Name]

#### Snapshot (counts as returned per status query)
- **Open deals**: [N]
- **Won (in the window queried)**: [N]
- **Lost (in the window queried)**: [N]
> Win rate and average deal value aren't computed here — see AC's native deal reporting.

#### Stage Breakdown
| Stage | Deals (as returned) | Notable deals |
|-------|---------------------|---------------|
| ...   | ...                 | ...           |
(Counts and deals as returned — not summed values or conversion rates.)

#### Pipeline Flow
[Stage 1] → [Stage 2] → [Stage 3] → [Won]
  [N] deals    [N] deals    [N] deals    [N] deals
(Deal counts per stage as returned. No value totals.)

#### Top Deals (sorted by value, as returned)
1. **[Deal Title]** — $[Value] — Stage: [Stage] — Owner: [Owner]
2. **[Deal Title]** — $[Value] — Stage: [Stage] — Owner: [Owner]
3. **[Deal Title]** — $[Value] — Stage: [Stage] — Owner: [Owner]

#### Observations (qualitative)
- **Possible bottleneck**: [stage with conspicuously many open deals, from the counts]
- **Risk**: [specific deals that appear idle or long-stuck, by name]

#### Recommendations
1. [Highest priority action]
2. [Second priority]
3. [Third priority]
```

> **Acting on the review:** This command is read-only. If the user then wants to *act* — reorganize stages, move stuck deals, or reassign owners — hand off to the **deals-crm** skill, which uses the write tools (`create_deal_stage`, `move_deals_to_stage`, `deal_owner_bulk_update`) with a preview-and-confirm step.

### Handling edge cases
- If no pipelines exist, explain what deal pipelines are and offer to set one up (via the deals-crm skill)
- If the user has multiple pipelines, summarize each and recommend which to focus on
- If there are very few deals (<5), focus on pipeline structure rather than reading patterns into thin data

### Arguments
- `/deal-pipeline-review` — review all pipelines
- `/deal-pipeline-review [pipeline name]` — review a specific pipeline
