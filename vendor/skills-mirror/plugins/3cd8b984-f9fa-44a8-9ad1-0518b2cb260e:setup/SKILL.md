---
name: setup
description: Initialize or extend the JTBD knowledge base, either in Notion (creates the hub page, the five linked databases, views and the concepts page) or locally as a Markdown vault, then writes the configuration into jtbd.config.yaml. Also adds a new project, switches backend, or upgrades an existing base to the latest schema. Use when the user says "set up the JTBD base", "initialize", "install in my Notion", "work locally", "add a project", "upgrade the base", or when jtbd.config.yaml is missing or empty.
argument-hint: "[local | notion | add project <name> | migrate to local|notion]"
---

# Setup: create the JTBD base

Before anything else, read `${CLAUDE_PLUGIN_ROOT}/reference/rules.md` (data model, scoring, rules). The user's configuration is `jtbd.config.yaml` at the project root; it may not exist yet, that is what this skill creates.

Files of this skill, in `${CLAUDE_SKILL_DIR}`:
- `schema.md`: canonical model, Notion DDL in creation order, local file templates
- `seed/concepts.md`: concepts and writing rules page

The JTBD methods are not installed in the base: they live in the `jtbd-base:method` skill (`references/`).

## 0. Check the current state

Read `jtbd.config.yaml` at the project root. If it does not exist, start from `${CLAUDE_PLUGIN_ROOT}/jtbd.config.example.yaml`.
- If a backend is already configured and the user did not ask for a new base, offer instead: add a project (section 3), switch backend (section 4), upgrade the schema (section 6), or repair (re-run only the missing steps).
- Never create a second hub on top of a working one without explicit confirmation.
- **Notion, even without a config:** before creating anything, search the workspace for an existing "JTBD Hub" page and "Job Performers" / "Jobs" databases. Notion unique ID prefixes (JP, JOB, OUT, ALT, EV) must be unique across the whole workspace, so a second base with the same prefixes cannot be created. If a base is found, fetch the hub, show the user its projects (the Project options and their row counts) and offer: connect this project to it and add the project (section 3, then write the config with its IDs), or use the local backend. Never create the hub page first and discover the conflict on the first database.

## 1. Ask (one AskUserQuestion call, defaults in bold)

1. Backend: **Notion** (shareable, multi-user) or Local (Markdown vault, private, works offline, Obsidian friendly).
2. First project name (e.g. the product being researched).
3. Notion only: parent page (URL) or **a private page at the workspace root** (can be moved later).
4. Bootstrap: **empty base** or draft starter hypotheses from a short description of the product and its users.

## 2a. Notion backend

Use the Notion MCP tools. Keep every returned ID.

1. **Hub page.** Create "JTBD Hub" (icon 🧭) under the chosen parent, or with draft mode for a private root page. Content: one paragraph on what the base holds, a callout on the status lifecycle (Hypothesis, Supported, Validated), then a heading "Knowledge base" and a line saying the methods are available through the `jtbd-base:method` skill.
2. **Databases.** Create the five databases under the hub with the DDL in `schema.md`, in order: Job Performers, Jobs (+ Parent job self-relation), Outcomes, Alternatives, Evidence. Replace `<PROJECT>` and the `<..._DS>` placeholders with real values from previous steps. If a creation fails with "Unique ID prefix is already in use", stop: another base exists in the workspace (see section 0). Tell the user, offer to move the pages created so far to the trash (only with their confirmation), and continue with the options of section 0.
3. **Views.** Create the two views listed in `schema.md`.
4. **Concepts page.** Create "JTBD Concepts and Writing Rules" (icon 📘) under the hub, content = `${CLAUDE_SKILL_DIR}/seed/concepts.md` without its H1.
5. **Tidy the hub.** Replace the hub content so the five databases and the concepts page sit under "Knowledge base" (keep the exact `<database>` and `<page>` tags returned by fetch).
6. **Write the config** (section 5) with every ID.
7. **Verify.** Fetch the hub (5 databases + 1 page). Report the hub link.

## 2b. Local backend

1. Ask for the vault folder name (**jtbd-base**). Create `performers/ jobs/ outcomes/ alternatives/ evidence/` inside it.
2. Copy `${CLAUDE_SKILL_DIR}/seed/concepts.md` to `<vault>/concepts.md`.
3. Write the config (section 5) with `backend: local`.
4. Verify with `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jtbd_local.py" lint`, then build the graph hub with `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jtbd_local.py" graph`.
5. Tell the user they can open the vault folder in Obsidian; links use `[[ID]]`, and `Graph/index.md` links every entry for the graph view.

## 2c. Bootstrap (optional, both backends)

Ask for: the product in two sentences, who uses it, what they use today instead. Then draft, all with Status = Hypothesis and a note "Seeded from founder knowledge on <date>, no evidence yet":
- 1 to 3 performers (with could be, aspiration, context)
- 1 to 2 main jobs per performer, 4 to 8 ordered steps each, 1 emotional and 1 social job
- 1 to 2 outcomes per step
- 3 to 7 alternatives
Show the draft as a table, adjust with the user, then write it following the jtbd-base:capture skill.

## 3. Add a project

- Notion: for each of the five knowledge data sources (Performers, Jobs, Outcomes, Alternatives, Evidence), fetch the schema, then `ALTER COLUMN "Project" SET SELECT(...)` listing **all existing options plus the new one** (omitted options are deleted). Then add the name to `projects` in the config.
- Local: add the name to `projects` in the config. Nothing else.
- Offer the bootstrap (2c) for the new project.

## 4. Switch backend or migrate

Ask whether to migrate existing data or start empty in the new backend.
- Notion to local: query every data source in rows mode, write one file per row following the templates in `schema.md`, keeping the Notion IDs (JOB-3 becomes JOB-003) and converting relations to `[[ID]]` links. Then switch `backend`.
- Local to Notion: run 2a, then create rows in dependency order (performers, main jobs, steps, other jobs, outcomes, alternatives, evidence), mapping local IDs to new page IDs for relations. Notion assigns its own unique IDs; keep a mapping table in the report.
- Keep the old data untouched until the user confirms the migration is correct.

## 5. Config file format

Write `jtbd.config.yaml` at the project root (create it if missing, otherwise update only the keys that change). It holds workspace IDs: if the project is a git repository, offer to add it to `.gitignore` together with `inbox/`, `outputs/` and `jtbd-base/`.

```yaml
backend: notion            # notion | local
projects: [Acme]
vault_path: jtbd-base      # local backend only
notion:
  hub_page: <id>
  concepts_page: <id>
  performers_ds: collection://<id>
  jobs_ds: collection://<id>
  outcomes_ds: collection://<id>
  alternatives_ds: collection://<id>
  evidence_ds: collection://<id>
  view_job_map: view://<id>
  view_opportunity_ranking: view://<id>
```

For a local-only setup, leave the `notion` values empty.

## 6. Upgrade an existing base

When `schema.md` gained properties after the base was created (see "Upgrading an existing base" in `schema.md`):
- Notion: fetch each data source listed there, compare its properties with the DDL, and run only the missing `ADD COLUMN` statements. Show the list first and apply after confirmation. Existing rows keep their values; new properties start empty.
- Local: nothing is required, missing fields and sections read as empty. Offer to add the empty sections (for example `## Push` to `## Habit` on alternatives) so they show up in Obsidian.
- Report what changed.
