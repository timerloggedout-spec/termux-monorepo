---
name: heartbeat
description: This skill should be used when the user asks to "run a heartbeat", "run the agent loop", "process GitHub issues", "check for work", or runs the /heartbeat command. Executes the githubclip heartbeat — picks up GitHub Project issues, resolves personas, does work, and reports back with structured comments.
version: '1.0.0'
---

# githubclip Heartbeat (GitHub)

Execute the githubclip heartbeat cycle: pick up assigned GitHub Project issues, resolve the right persona, do the work, and report back with structured comments.

**Arguments:**
- `--dry-run` — Show what would be picked up without doing work
- `--persona <name>` — Only pick issues matching a specific persona

**Reference files** (consult as needed during execution):
- `${CLAUDE_PLUGIN_ROOT}/references/comment-format.md` — Comment templates and rules
- `${CLAUDE_PLUGIN_ROOT}/references/label-conventions.md` — Label lifecycle and read-modify-write pattern
- `${CLAUDE_PLUGIN_ROOT}/references/status-mapping.md` — GitHub Project states, sort order, inbox filtering
- `${CLAUDE_PLUGIN_ROOT}/references/github-status-mapping.md` — GitHub-specific state details

## Step 1: Load Config & Validate Setup

1. Read `.githubclip/config.yaml`. If missing, stop and instruct the user to run `/githubclip-init`.
2. Validate provider is `github`: if not, stop with error message about provider mismatch.
3. Validate all required fields are present and resolved:
   - `github.project.project_id` (GraphQL ID)
   - `github.fields.status.field_id` and all option IDs
   - `github.fields.priority.field_id` and all option IDs
4. Check for lockfile at `.githubclip/.heartbeat-lock`:
   - If exists and is **less than** `stale_lock_hours` old → stop: "Previous heartbeat still active. Skipping."
   - If exists and is **older than** `stale_lock_hours` → delete it, log: "Cleaned stale lockfile."
   - If no lockfile → proceed.
5. Create lockfile with current ISO timestamp.
6. **On any exit path** (success, error, or early return), delete the lockfile.

Check quiet hours: if `quiet_hours.enabled` and current time is within the quiet window:
- `behavior: "skip"` → delete lockfile and exit: "Quiet hours active. Skipping."
- `behavior: "triage-only"` → proceed but only load Orchestrator persona (skip worker personas in step 3).

## Step 2: Fetch and Build Queue

Implement schema drift sentry: compute checksum of field IDs and option IDs from config; if mismatch detected, run repair preflight and prompt user to re-run init.

**Query Project items:**
1. Use GitHub MCP (or fallback to `gh api graphql`) to fetch paginated Project items:
   - Filter: `content_type = Issue` (exclude DraftIssue, PullRequest)
   - Query: project items with `status` and `priority` field values
   - Include issue `number`, `title`, `assignees`, `updatedAt`

2. **Repair missing Project items** (auto-add policy):
   - For each fetched issue, check if it has a Project item
   - If not: add to project, set `Status=Todo`, set `Priority=None`
   - If item exists but missing field values: set defaults

3. **Filter to queue candidates:**
   - Keep: `repo` matches `owner/repo` from config
   - Keep: `assignee` includes current GitHub actor login
   - Keep: `Status` in (`Todo`, `In Progress`)
   - Skip: `Status` in (`In Review`, `Done`, `Canceled`)
   - Skip: `agent-blocked` label UNLESS new human comments exist since last agent heartbeat comment

4. **Detect and clean stale locks:**
   - If issue has `agent-working` label but no heartbeat comment within `stale_lock_hours`
   - Remove `agent-working` label, post cleanup comment, add to queue

5. **Sort queue** (deterministic order):
   - Primary: `Status` rank (`In Progress` = 0, `Todo` = 1)
   - Secondary: `Priority` rank (`Urgent` = 1 → `None` = 5)
   - Tertiary: `updatedAt` (most recent first)
   - Quaternary: `issue_number` (lowest first, tie-break)

## Step 3: Pick Issue

1. If `--persona <name>` flag set, filter queue to issues matching that persona label only.
2. Pick first issue from sorted queue.
3. If `--dry-run`, report findings and exit:
   ```
   Dry run — would pick:
     #123 [backend] "Issue title" (In Progress, High)
   
   Queue:
     #124 [frontend] "Other issue" (Todo, Medium)
   ```
4. If no issues match → delete lockfile and exit: "No issues in queue. Heartbeat complete."

## Step 4: Resolve Persona

1. Read issue labels. Find persona label by matching against `config.yaml` → `personas[*].label`.
2. If no persona label found → load persona with `is_default: true` (typically Orchestrator).
3. Load persona files from `.githubclip/<persona.path>/`:
   - `SOUL.md` → inject as identity instructions
   - `TOOLS.md` → inject as tool guidance
   - `config.yaml` → read runtime settings

Apply runtime config from persona's `config.yaml`:
- `model` — note the target model
- `thinking_effort` — apply if supported
- `max_turns` — respect as work budget
- `enable_chrome` — note for browser-dependent tasks

## Step 5: Validate Tools

Read `required_tools` from persona config. For each entry, verify the tool prefix is available:
- `github` tools for issue/label/comment operations
- If a required tool prefix has **no matching tools** available → stop immediately
  - Post blocked comment naming missing tool
  - Apply `agent-blocked` label (read-modify-write)
  - Remove `agent-working` if present
  - Proceed to step 11 (next issue)

## Step 6: Lock Issue

**Acquire distributed lock:**
1. Fetch current issue state (labels, last heartbeat comment timestamp)
2. If `agent-working` already present: check timestamp in last heartbeat comment
   - If timestamp is recent (within `stale_lock_hours`), issue is already locked by active heartbeat → skip to step 11
   - If timestamp is old (stale), clean the old lock and proceed
3. Otherwise: append `agent-working` label via read-modify-write pattern
   - Fetch current labels
   - Append `agent-working`
   - Write full label set back

## Step 7: Understand Context

1. Fetch issue title, description, and all comments (paginated)
2. If issue references a parent issue, fetch parent for broader context
3. Identify new comments since last heartbeat: look for comments after last `Heartbeat #N` comment
4. Parse heartbeat counter: find last comment matching `Heartbeat #N` pattern. Next will be `#N+1`. If none found, start at `#1`.
5. Append action record to `.githubclip/heartbeat-log.jsonl`:
   ```json
   {"timestamp": "ISO", "issue": "#123", "heartbeat": N, "step": "understand", "status": "ok"}
   ```

## Step 8: Do Work

Follow the persona's SOUL.md instructions. This step varies by persona:

**Orchestrator persona:** Triage the issue – apply persona labels, create sub-issues, or escalate. Never write code.

**CEO persona:** Make strategic decisions – prioritization, scope, architecture, coordination. Never write code.

**Worker personas (backend, frontend, etc.):**
- Use repo tools (Read, Write, Edit, Bash, Grep, Glob) to implement changes
- For large scope: create GitHub issues via GitHub MCP (not sub-issue model; use `related to` comment reference instead)
- For small scope: work directly, use internal tasks to track progress
- Commit changes with descriptive conventional commit messages
- Respect `max_turns` from persona config as a work budget

**If GitHub MCP becomes unavailable mid-work:** Stop immediately. Leave `agent-working` label in place (will be cleaned as stale on next heartbeat). Log error. Delete lockfile and exit.

**Canary check (anti-fragile):** Before full state mutations, attempt a low-risk field update test (e.g., Priority toggle) on the selected issue. If it fails, downgrade this run to read-only and post health comment.

## Step 9: Report

Post a structured comment on the GitHub issue.

Follow the comment format from `${CLAUDE_PLUGIN_ROOT}/references/comment-format.md`:
- Include `Heartbeat #N` counter (incremented from step 7)
- Include timestamp and duration
- Include persona name in footer
- List commits with SHAs, related issues created, and next steps
- For blocked status: name who needs to act (Board user from config `github.user_name`)

Append heartbeat metadata to `.githubclip/heartbeat-log.jsonl`:
```json
{"heartbeat": N, "timestamp": "ISO", "issue": "#123", "persona": "name", "duration_sec": N, "status": "completed|blocked|more_work|triaged", "actions": ["description"], "step": "report"}
```

## Step 10: Update State

Apply outcome-specific transitions via Project field mutations and label updates.

**Transition matrix (from plan):**

| Outcome | Project Status | Labels | Action |
|---|---|---|---|
| **completed** | Set `Done` | Remove `agent-working` | Optional: close issue if config `close_on_done: true` |
| **blocked** | Keep `In Progress` | Remove `agent-working`, add `agent-blocked` | Post blocking comment |
| **more_work** | Keep `In Progress` | Keep `agent-working` | (state unchanged) |
| **triaged** | Set `Todo` | Add persona label if missing | (no label changes if persona already set) |

**Implementation steps:**
1. Determine outcome from work result
2. If outcome requires Project field update:
   - Use GitHub MCP mutation (or fallback to `gh api graphql`) with stable field IDs and option IDs from config
   - On mutation failure: post error comment, keep `agent-working`, log error
   - If write failures exceed circuit-breaker threshold: auto-downgrade to read-only, don't attempt state changes
3. If outcome requires label change:
   - Fetch current issue labels
   - Modify locally (filter/append)
   - Write full label set back via read-modify-write
4. Append action record to log:
   ```json
   {"timestamp": "ISO", "issue": "#123", "heartbeat": N, "step": "update_state", "status": "ok|error", "outcome": "completed"}
   ```

## Step 11: Next Issue or Exit

1. Increment work counter for this heartbeat
2. If counter < `max_issues_per_heartbeat`, return to **Step 2** to pick next issue
3. Otherwise or on final issue, proceed to exit:
   - Delete lockfile (critical: all exit paths must do this)
   - If 0 todo issues remain in queue, suggest pausing the schedule
   - If 3+ issues are blocked, suggest Board attention
   - Summarize: issues worked, outcomes, any degradation mode status
   - Append final record to heartbeat log with session summary

**Anti-fragile exit behaviors:**
- If circuit-breaker was triggered: post summary comment marking run as degraded
- If recovery journal is enabled: recovery information is in `.githubclip/heartbeat-log.jsonl` for crash resume
- If reconciliation pass enabled: optionally run cleanup (remove orphaned `agent-working` labels, re-sync inconsistent statuses)
