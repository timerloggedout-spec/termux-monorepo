---
name: githubclip-status
description: This skill should be used when the user asks to "check githubclip status", "show agent status", "what is githubclip doing", "show heartbeat status", "what's in the queue", or runs the /githubclip-status command. Shows current githubclip state, issue queue, and blocked items.
version: '0.1.0'
---

# githubclip Status

Display the current state of githubclip in this repository: schedule info, last heartbeat, issue activity, queue, and blocked items.

**Arguments:**
- `--history` — Show recent heartbeat history from the log file

## Status Procedure

### Step 1: Load Config

Read `.githubclip/config.yaml`. If missing, report that githubclip is not initialized and suggest `/githubclip-init`.

### Step 2: Check Schedule

Report whether a recurring heartbeat is active. Check if `/schedule` is running `/heartbeat` by noting this is informational — the user knows their schedule state.

### Step 3: Last Heartbeat

Read the last line of `.githubclip/heartbeat-log.jsonl` (if it exists). Report:
- Heartbeat number, timestamp, and how long ago it ran
- Which persona and issue were involved
- Outcome (completed, in progress, blocked)

If no log file exists, report "No heartbeat history found."

### Step 4: Current Issues

Use GitHub MCP to list issues assigned to the current user (`mcp__github__list_issues` with `assignee: "me"`). Filter and categorize:

**Since last heartbeat** (issues that changed since the last logged heartbeat timestamp):
- `✓` Completed issues
- `→` In Progress issues
- `✗` Blocked issues
- `+` Newly created issues

**Queue** (next heartbeat would pick these up):
- Issues with persona labels, status Todo or In Progress, sorted by priority
- Show: issue number, persona label, status, priority, title

**Blocked** (needs Board attention):
- Issues with `agent-blocked` label
- Show: issue number, Board user mention, blocker summary from last agent comment

### Step 5: Format Output

```
githubclip Status
────────────────
Last beat:    Heartbeat #N — X min ago

Since last heartbeat:
  ✓ #XX  [persona]   Completed    "Title"
  → #XX  [persona]   In Progress  "Title"
  ✗ #XX  [persona]   Blocked      "Title"

Queue (next heartbeat):
  #XX  [persona]  Status  Priority  "Title"

Blocked (needs Board):
  #XX  @User — blocker summary
```

## History Mode

When `--history` is passed, read `.githubclip/heartbeat-log.jsonl` and display the last 10 entries:

```
Heartbeat History (last 10)
───────────────────────────
#N  HH:MM  persona  #XX  Status      (duration)
#N  HH:MM  persona  #XX  Status      (duration)
```

If the log file doesn't exist or is empty, report "No heartbeat history found."
