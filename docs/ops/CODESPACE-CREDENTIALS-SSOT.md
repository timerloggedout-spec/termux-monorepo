# Codespace credentials SSOT (#184 plane)

**Status:** proven 2026-09-23 — Codespace `agent-bifrost-006-5g7qvg7pqjggh4jqv` created via API.

## What works

Repo **Actions secrets** (not issue body values):

```text
CODESPACE_CREATE_TOKEN          # optional override
  || ARCHWIZ_GITHUB_TOKEN       # monorepo SSOT (present)
  || OPERATOR_GITHUB_TOKEN      # present
  || OPERATOR_TOKEN
```

Same precedence as `deepseek-ci.yml` / help-wanted workflows.

Issue **#184** is the **inventory of names + scopes**. Token **values** never belong in the issue or chat — only in Settings → Secrets → Actions.

## How to create (agent or Operator)

```bash
# After workflow on master:
gh workflow run codespace-create.yml -R timerloggedout-spec/termux-monorepo \
  -f ref=master -f display_name=agent-work
```

Or: Actions → **Codespace create (dispatch)** → Run workflow.

Job summary prints `name` + `web_url`.

## Machine types

- Do **not** force `basicLinux32gb` — rejected for this repo (`Machine ... is not allowed`).
- Omit `machine` → API selects default (`standardLinux32gb` observed).

## Codespace states (not “rotation”)

| State | Meaning |
|-------|--------|
| **Provisioning** | Starting |
| **Available** | Ready to open |
| **Shutdown** | Idle timeout stopped compute (default **30 min** inactivity). Disk retained. |
| **Deleted** | Retention expired (default up to 30 days stopped) |

`glorious-capybara-wrq7vrqj7xqjh995p` (Shutdown since ~2026-09-15): normal idle stop — **not** a concurrent-limit rotation. Re-open URL or start via API to resume; storage may still bill until deleted.

Limits that *can* block create: spending budget, max codespaces per user/org policy, machine-type policy — distinct from Shutdown.

## Security

- Never paste PAT into issues, PR bodies, or agent chat.
- Agents use workflow_dispatch + secrets; sandbox has no raw PAT env.
- Rotate any token that was ever pasted into #184 before REDACT.

Implements: #184 collaborative path + #775/#776
BIUDL.
