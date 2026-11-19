---
name: githubclip-init
description: This skill should be used when the user asks to "initialize githubclip", "set up githubclip", "githubclip init", "configure githubclip for this repo", or runs the /githubclip-init command. Scaffolds a repo with githubclip config, persona directories, and GitHub labels/Project fields.
version: '2.0.0'
---

# githubclip Initialization (GitHub)

Initialize githubclip in the current GitHub repository. This creates the `.githubclip/` directory with config, persona templates, GitHub labels, and validates/creates a GitHub Project with required custom fields.

## Prerequisites

Before starting, verify the GitHub MCP is available:

1. Check that GitHub MCP tools are callable (repo, issues, labels operations)
2. If not available, stop and instruct the user to connect GitHub MCP first:
   - **Recommended:** Install the GitHub plugin from the Claude marketplace (`claude-plugins-official / GitHub`)
   - Or: ensure GitHub CLI (`gh`) is authenticated (`gh auth status`) and add GitHub MCP manually to `.mcp.json`
   - Restart Claude Code session, then re-run `/githubclip-init`

## Initialization Procedure

### Step 1: Gather GitHub & Repo Context

1. Prompt for repository target (or auto-detect from current `.git` context)
   - Validate format: `owner/repo`
   - Verify repo is accessible via GitHub MCP

2. Prompt for current user GitHub login (or detect from `gh auth` context)
   - This login is used for heartbeat identity and @-mentions

3. Present findings and ask confirmation:
   - Repository: `owner/repo`
   - Your GitHub login: `username`

### Step 2: Choose Provider & Persona Preset

1. Confirm GitHub is the provider (`provider: github`).

2. Ask which persona set to scaffold:

| Preset | Personas Created |
|--------|-----------------|
| **engineering** (default) | Orchestrator, CEO, Backend, Frontend |
| **full** | Orchestrator, CEO, Backend, Frontend, Infra, QA |
| **minimal** | Orchestrator, CEO only |
| **custom** | Orchestrator, CEO + user-specified personas |

For "custom", ask the user to name each persona and its label.

### Step 3: Select or Create GitHub Project

1. Ask: "Do you have an existing GitHub Project (v2) for this work, or should githubclip create one?"
   - **Existing:** Ask for project number or URL, then validate/inspect fields
   - **Create:** Ask owner (user or org), create new project, then proceed to schema enforcement

2. **If existing project:**
   - Fetch project via GitHub MCP GraphQL (or `gh api graphql`)
   - Inspect current custom fields
   - Check if `Status` and `Priority` fields exist with required options
   - If missing or mismatched: warn user and offer to add/repair fields
   - If user agrees: add missing fields or options (non-destructive)

3. **If creating new project:**
   - Use GitHub MCP to create project under selected owner
   - Name: suggest "`Repo Name - githubclip`" (user can customize)
   - Link project to target repository (or leave unlinked — auto-link on first issue add)

4. **Resolve project ID:**
   - Fetch and store stable GraphQL project ID

### Step 4: Enforce Required Custom Fields (Idempotent)

Create or repair the two mandatory fields:

#### Field: Status (single-select)

1. Check if field exists by name `Status`
   - If exists: fetch field ID and option IDs
   - If missing: create field via GitHub MCP GraphQL mutation (or `gh api graphql`)

2. Ensure all required options exist with exact names:
   - `Todo`
   - `In Progress`
   - `In Review`
   - `Done`
   - `Canceled`

3. For each option:
   - If exists: record its option ID
   - If missing: create with standard color (blue, yellow, orange, green, gray)
   - Never delete unknown options (user-created options are preserved)

4. Store resolved field ID and all option IDs in config

#### Field: Priority (single-select)

1. Check if field exists by name `Priority`
   - If exists: fetch field ID and option IDs
   - If missing: create field via GitHub MCP GraphQL mutation

2. Ensure all required options exist with exact names:
   - `Urgent`
   - `High`
   - `Medium`
   - `Low`
   - `None`

3. For each option:
   - If exists: record its option ID
   - If missing: create with standard color (red, orange, yellow, blue, gray)
   - Never delete unknown options

4. Store resolved field ID and all option IDs in config

**Mutation smoke test:** After field creation/repair, attempt a test mutation on a temporary issue to verify write access and field IDs are correct.

### Step 5: Create or Verify GitHub Labels

Create githubclip label group and child labels in the target repository:

1. Use GitHub MCP to create labels (or verify existing):
   - `agent-working` — state label for active work (color: `pending` or custom)
   - `agent-blocked` — state label for blocked work (color: `error` or custom)
   - One label per persona that has a non-null label (e.g., `backend`, `frontend`, `ceo`)

2. For each label:
   - Check if exists via `list_repository_labels`
   - If missing: create via `create_label`
   - If exists: verify description matches expected purpose
   - Never delete unknown labels

3. Store resolved label names in config

### Step 6: Scaffold Config & Personas

1. Create the directory structure:
   ```
   .githubclip/
   ├── config.yaml
   └── personas/
       ├── orchestrator/
       │   ├── SOUL.md
       │   ├── TOOLS.md
       │   └── config.yaml
       ├── ceo/
       │   ├── SOUL.md
       │   ├── TOOLS.md
       │   └── config.yaml
       ├── backend/          (if selected)
       │   ├── SOUL.md
       │   ├── TOOLS.md
       │   └── config.yaml
       └── frontend/         (if selected)
           ├── SOUL.md
           ├── TOOLS.md
           └── config.yaml
   ```

2. Copy templates from `${CLAUDE_PLUGIN_ROOT}/templates/`:
   - Read each template file
   - Replace placeholders:
     - `{{OWNER}}` → repository owner
     - `{{REPO}}` → repository name
     - `{{USER_NAME}}` → current GitHub login
   - Write to `.githubclip/`

3. Populate GitHub-specific config sections:
   - `github.owner`, `github.repo`, `github.user_name`
   - `github.project.project_id`, `project_number`
   - `github.fields.status.field_id` and all option IDs
   - `github.fields.priority.field_id` and all option IDs
   - `github.api_mode` (default: `mcp_only`)

4. Update `config.yaml` personas section to match selected preset — remove entries for unselected personas

### Step 7: Validate Configuration

1. Perform preflight checks:
   - Can read `.githubclip/config.yaml` and parse valid YAML
   - All required GitHub fields are resolvable
   - Project field IDs and option IDs are valid (not null)
   - All persona directories exist with required files
   - All required GitHub labels exist

2. Run **mutation smoke test** (anti-fragile):
   - Create a temporary test comment on the repository (e.g., "githubclip init test #XYZ")
   - Attempt low-risk field update on a non-critical issue (if available)
   - If mutation succeeds: log "✓ Field mutations working"
   - If mutation fails: log error and prompt user for remediation

3. If any validation fails, stop and provide explicit remediation instructions

### Step 8: Offer Schedule Setup

Ask the user if they want to set up a recurring heartbeat:

- **Yes** → Suggest: `/schedule 30m /heartbeat` and explain cadence options (30m, 1h, 2h, custom)
- **Not now** → Explain they can run `/heartbeat` manually or set up `/schedule` later

### Step 9: Print Summary

Display what was created or modified:

```
✓ githubclip initialized!

GitHub context:
  Owner: myorg
  Repo: myrepo
  Your login: myusername

GitHub Project:
  Project ID: PVT_XYZ123
  Project URL: https://github.com/orgs/myorg/projects/5
  Fields:
    ✓ Status (field ID: PVT_FIELD_1, 5 options)
    ✓ Priority (field ID: PVT_FIELD_2, 5 options)

GitHub labels created:
  ✓ agent-working
  ✓ agent-blocked
  ✓ backend
  ✓ frontend
  ✓ ceo

Config: .githubclip/config.yaml
Personas:
  ✓ orchestrator → default (no label)
  ✓ ceo          → "ceo" label
  ✓ backend      → "backend" label
  ✓ frontend     → "frontend" label

Next steps:
  1. Review .githubclip/config.yaml (project ID, field IDs are set)
  2. Customize persona SOUL.md files for your project
  3. Run: /heartbeat --dry-run (to validate setup)
  4. Run: /heartbeat (to pick up and start work)
  5. Or set up schedule: /schedule 30m /heartbeat

✓ Mutation smoke test passed — writes are working
```

## Re-initialization (Update)

If `.githubclip/config.yaml` already exists:

1. Read existing config version
2. Ask the user: **overwrite** (fresh start), **merge** (add missing personas/update fields), or **cancel**

### Merge behavior:
- Only create persona directories that don't exist
- Only create labels that don't exist
- Only add missing Project field options (never delete unknown user options)
- Detect field/option ID drift: if names changed but IDs are stable, re-resolve IDs
- Preserve user customizations in persona SOUL.md files

### Overwrite behavior:
- Back up existing config to `config.yaml.bak`
- Back up persona directories to `.githubclip-backup/`
- Rebuild from scratch
- User must manually restore any customizations

## Error Handling

| Error | Response |
|-------|----------|
| GitHub MCP not available | Stop. Print setup instructions for connecting GitHub MCP. |
| Repository not found | Stop. Ask user to verify repo exists and is accessible. |
| Project not found | Stop. Ask user to provide valid project number or create new project. |
| Field mutation fails | Log error, suggest re-running init or checking GitHub account permissions. Circuit breaker: disable field writes if repeated failures. |
| Label creation fails | Log each failure, continue with remaining labels, report summary. |
| `.githubclip/` already exists | Ask user: overwrite, merge, or cancel. Default to merge. |
| YAML parse fails | Log parse error, ask user to review config manually or contact support. |

## Anti-Fragile Initialization

- **Idempotent field creation:** re-running init never deletes user fields or options
- **ID caching:** store resolved IDs to avoid repeated GraphQL lookups
- **Drift detection:** checksum field IDs on heartbeat start; warn if mismatch
- **Smoke testing:** validate write access before declaring success
- **Backup on overwrite:** preserve old config if user chooses fresh init
