---
name: persona-list
description: This skill should be used when the user asks to "list personas", "show personas", "what personas are configured", "show githubclip agents", or runs the /persona-list command. Lists all configured githubclip personas with their runtime settings.
version: '0.1.0'
---

# List Personas

Display all configured githubclip personas for this repository.

## Procedure

### Step 1: Load Config

Read `.githubclip/config.yaml`. If missing, report that githubclip is not initialized and suggest `/githubclip-init`.

### Step 2: Read Persona Details

For each persona in the `personas` config map:

1. Read `config.yaml` from the persona's path (`.githubclip/<persona.path>/config.yaml`)
2. Check if `SOUL.md` and `TOOLS.md` exist
3. Collect: name, role, label, model, thinking effort, max turns, escalates_to, required tools

### Step 3: Format Output

```
githubclip Personas
──────────────────
Name              Label       Model    Turns  Escalates  Tools
Orchestrator      (default)   haiku    50     ceo        GitHub
CEO               ceo         sonnet   100    board      GitHub
Backend Engineer  backend     opus     300    ceo        GitHub
Frontend Engineer frontend    sonnet   200    ceo        GitHub

Files:
  Orchestrator: .githubclip/personas/orchestrator/ ✓ SOUL ✓ TOOLS ✓ config
  CEO:          .githubclip/personas/ceo/         ✓ SOUL ✓ TOOLS ✓ config
  Backend:      .githubclip/personas/backend/     ✓ SOUL ✓ TOOLS ✓ config
  Frontend:     .githubclip/personas/frontend/    ✓ SOUL ✓ TOOLS ✓ config
```

Flag missing files with `✗` so the user knows what needs attention.

### Step 4: Suggest Actions

- If any persona has missing files, suggest fixing them
- Mention `/persona-create` for adding new personas
