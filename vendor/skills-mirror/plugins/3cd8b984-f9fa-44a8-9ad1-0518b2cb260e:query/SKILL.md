---
name: query
description: Answer questions about the JTBD knowledge base (Notion or local), such as listing a performer's jobs, showing the job map, ranking opportunities, finding underserved outcomes, showing the evidence behind an entry, or spotting gaps. Use for any read-only question about the JTBD data.
argument-hint: "[question, e.g. job map of the UX researcher]"
---

# Query: ask the JTBD base

Before anything else, read `${CLAUDE_PLUGIN_ROOT}/reference/rules.md` (data model, scoring, rules) and `jtbd.config.yaml` at the project root (backend, IDs). If the config is missing or `backend` is empty, run `/jtbd-base:setup` first.

## How to read the data (local backend)

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jtbd_local.py" index [--project P] [--kind jobs|outcomes|...]`: every entry with status, links, evidence count and computed Opportunity and Quadrant.
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jtbd_local.py" tree [--project P]`: performer → main jobs → ordered steps → outcomes, plus emotional and social jobs.
- Grep and Read the files for notes, quotes and body content.

## How to read the data (Notion backend)

- **Rows mode** (`query-data-sources` with `mode: rows`) with structured filters on `Project`, `Type`, `Status`, `Performer`, `Parent job`. Best default: it returns relations and numbers. Formula properties come back as opaque references: recompute Opportunity, Quadrant and Satisfaction delta yourself with the formulas in the rules file.
- **View mode** for the saved views: "Opportunity ranking" (outcomes sorted by Opportunity) and "Job map" (jobs grouped by type).
- **SQL mode** only for simple counts or text filters. SQL may be quota-limited depending on the Notion plan.
- **Fetch** a page for its full content and relations.
- Relations come back as page URLs. Resolve them to statements by fetching or by matching against rows already loaded. Load each data source once per question, then join in memory.

## Common questions and how to answer

| Question | Approach |
|---|---|
| "Show the map of performer X" | Performer → main jobs → steps sorted by Step order → outcomes per step, plus emotional and social jobs. Render as a nested list or a table. |
| "Top opportunities" | Outcomes with Importance and Satisfaction, compute Opportunity and Quadrant, sort descending. If no scores exist yet, say so and suggest method 8 "Find and rank opportunities" (`jtbd-base:method`). |
| "What is still a hypothesis?" / "Where is evidence missing?" | Rows with Status = Hypothesis, grouped by main job, with evidence count. |
| "Evidence behind X" | Fetch the entry, list linked Evidence with quote, participant and date. |
| "Who else gets this job done?" | Alternatives linked to the job and its parent. |
| "Why don't they switch?" / "Forces for X" | For each alternative of the job: Push, Pull, Anxiety, Habit, plus the Evidence tagged with each force. Say which side looks stronger (Push + Pull vs Anxiety + Habit) and which forces have no evidence or are empty. |
| "Gaps" | Main jobs with no steps, steps with no outcomes, outcomes with no evidence, performers with no emotional or social job, alternatives linked to nothing, alternatives with no forces documented. |
| "Compare performers" | Side-by-side table of main jobs and shared steps. |

## Answer format

- Lead with the direct answer, then the supporting table or list.
- Always show IDs (JOB-3, OUT-7) and Status so the user can act on them.
- Flag clearly when an answer rests only on hypotheses.
- If the user wants to keep the result (a map, a ranking), offer to save it to `outputs/` or as a Notion page under the hub.
