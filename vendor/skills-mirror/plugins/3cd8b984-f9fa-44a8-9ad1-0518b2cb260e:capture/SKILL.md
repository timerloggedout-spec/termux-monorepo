---
name: capture
description: Add, edit, link or deprecate entries in the JTBD knowledge base (Notion or local) (job performers, jobs, job steps, emotional and social jobs, desired outcomes, alternatives, evidence). Use when the user wants to create, rewrite, move, merge, re-status or link JTBD entries.
argument-hint: "[what to add or change, e.g. outcome: researchers waste time re-tagging]"
---

# Capture: add and edit JTBD entries

Before anything else, read `${CLAUDE_PLUGIN_ROOT}/reference/rules.md` (data model, scoring, rules) and `jtbd.config.yaml` at the project root (backend, IDs). If the config is missing or `backend` is empty, run `/jtbd-base:setup` first.

Configuration (backend, IDs, projects) is in `jtbd.config.yaml`. Writing rules are in the concepts page (Notion) or `<vault_path>/concepts.md` (local).

## Backend

- **Notion:** create pages with the data source as parent; relations take page IDs or URLs as JSON arrays. Unique IDs (JOB-n) are assigned by Notion.
- **Local:** create one file per entry from the templates in `${CLAUDE_PLUGIN_ROOT}/skills/setup/schema.md`. Get the ID with `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jtbd_local.py" next-id <PREFIX>` (one call per new entry, or increment yourself within a batch). File name = ID. Store only child-to-parent links (`parent`, `job`, `performer`, `jobs`, and the relation lists on Evidence). Keep `aliases` equal to the statement. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jtbd_local.py" lint` after writing, then `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jtbd_local.py" graph` to refresh `Graph/index.md`.

## Procedure

1. **Identify the target.** Which project, which performer, which main job. If the user gives free text ("researchers hate re-tagging"), decide what it is: a job, a step, an outcome, an alternative or an evidence quote. One input can produce several rows.
2. **Load context.** Notion: query the relevant data source(s) in rows mode, filtered on Project (and Performer or Parent job when known). Local: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jtbd_local.py" index --project <P>`.
3. **Write well-formed statements.**
   - Job / step: verb + object + context. Remove solutions ("use a tool to", "with AI") and quality words ("quickly", "easily").
   - Outcome: Minimize or Increase + time / likelihood / effort / number / cost / risk + object + context. Set `Direction` and `Metric` accordingly. Prefer Minimize.
   - Emotional: "Feel..." or "Avoid feeling...". Social: "Be perceived as..." or "Avoid being perceived as...".
   - Alternative: name what people actually use (a competitor, a workaround, "Do nothing"), set Type, then fill the forces of progress when known: Push, Pull, Anxiety, Habit, one short sentence each from the performer's view. Leave a force empty rather than guessing. Notion: the four properties. Local: the `## Push`, `## Pull`, `## Anxiety`, `## Habit` body sections.
   - If the user's wording breaks a rule, propose the corrected version and say in one line why.
4. **Deduplicate.** Compare meaning with existing rows. If a near duplicate exists, propose: update it, merge (keep one, deprecate the other with a note pointing to the kept ID), or keep both with a reason.
5. **Place it in the hierarchy.**
   - Steps and sub-jobs: set `Parent job` and `Step order`. When inserting a step in the middle, propose renumbering siblings.
   - Emotional and social jobs: `Parent job` = the main job.
   - Outcomes: `Job` = the most specific step they measure (not the main job, unless no step fits).
   - Alternatives: `Jobs` = the jobs they help get done.
   - Always set `Performer` on jobs and `Project` everywhere.
6. **Set status from evidence.** New = Hypothesis. If the user provides a real quote or source, create the Evidence row too, link it, and set the entry to Supported. Validated only with 3+ participants or a survey.
7. **Show, then write.** Present a compact table of the entries to create or change (statement, type, parent, status, evidence). Write after confirmation, following the backend rules above.
8. **Report.** List what was created or changed with their IDs (and Notion links on the Notion backend). Mention any gap you noticed (for example a step with no outcome).

## Editing and status changes

- Rewrites: update the title in place; add the previous wording to Notes if the meaning shifted.
- Deprecation: never delete. Set Status = Deprecated and write the reason (and replacement ID if any) in Notes.
- Survey results: write `Importance` and `Satisfaction` as averages on the 1 to 7 scale, create one Evidence row of Type Survey with sample size and date, link it to every rated row. Post-launch results go in `Satisfaction post-launch`.

## Evidence rows

Title: short label ("P03 on re-tagging after each study"). Type, Date, Participant (anonymized code), Quote (verbatim, short, anonymized), Force (Push, Pull, Anxiety or Habit, only when the quote illustrates one), Source (file name or URL), relations to every entry it supports.
