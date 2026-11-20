---
name: ingest
description: Process interview transcripts, research notes, survey exports or support tickets placed in the local inbox folder and turn them into JTBD proposals (jobs, steps, outcomes, alternatives, evidence quotes) matched against the existing base (Notion or local). Use when the user drops files to analyze or says "analyze this interview", "process the inbox", "import these notes".
argument-hint: "[file in inbox/ or 'all']"
---

# Ingest: from raw research to JTBD entries

Before anything else, read `${CLAUDE_PLUGIN_ROOT}/reference/rules.md` (data model, scoring, rules) and `jtbd.config.yaml` at the project root (backend, IDs). If the config is missing or `backend` is empty, run `/jtbd-base:setup` first.

Automates method 6 "Analyze research through the JTBD lens" (`${CLAUDE_PLUGIN_ROOT}/skills/method/references/06-analyze.md`).

## Procedure

1. **List inputs.** Files in `inbox/` not yet listed in `inbox/processed.md`, or the file the user named. Ask for the project and, if known, the performer.
2. **Snapshot the base.** Notion: query Jobs, Outcomes and Alternatives for the project (rows mode). Local: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jtbd_local.py" index --project <P>`. Build a compact list (ID, type, statement, parent) to pass to the analyst so it matches instead of duplicating.
3. **Delegate reading.** Launch the `jtbd-base:analyst` agent, one per file when there are several (in parallel), with: the file path, the project, the performer if known, and the snapshot. For a single short note, you can do the analysis yourself.
4. **Merge results.** Combine the analysts' outputs, merge duplicates across files, and count how many participants support each proposal.
5. **Present for validation**, grouped as:
   - Matches to existing entries (with new evidence): propose status upgrades where the rules allow.
   - New jobs and steps, placed in the hierarchy with a proposed Step order.
   - New outcomes, each attached to a step.
   - New alternatives, and forces (Push, Pull, Anxiety, Habit) to add to new or existing alternatives, with the tagged quotes.
   - Unclear items to discuss.
6. **Write after confirmation** using the jtbd-base:capture rules: Evidence rows first (anonymized quotes), then new entries, then relations and status changes.
7. **Log.** Append the file name, date and a one-line summary to `inbox/processed.md` (create it with a `| Date | File | Summary |` table if missing; it stays local, see .gitignore). Never move or delete the user's files.

## Survey exports

For a CSV with importance and satisfaction ratings: compute the mean per statement on the 1 to 7 scale (convert other scales linearly and say so), report the sample size, match statements to Outcome or Job rows, then write the values and one Survey evidence row through jtbd-base:capture.
