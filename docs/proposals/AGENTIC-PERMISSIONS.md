# Why You Still Have To Do Anything — Agentic Permissions

Honest boundary list. Everything else is already agent-operable via the GitHub connector on this account.

## What the agent CAN do today (proven this session)

| Action | Status |
|--------|--------|
| Read repo, branches, PRs, files, checks | ✅ |
| Create branches | ✅ |
| Create/update files + commit | ✅ |
| Open PRs | ✅ |
| Comment on issues/PRs | ✅ |
| Merge PRs (when mergeable + allowed) | ✅ (merged #11) |
| Retarget PR base branch | ✅ (retargeted #10 → master-staging) |
| Submit PR reviews (COMMENT / REQUEST_CHANGES / APPROVE) | ✅ tool present |

## What still needs YOU (human-only or policy)

| Blocker | Why agent cannot | Fix to go fully agentic |
|---------|------------------|-------------------------|
| **Credential rotation** | Secrets live on device / provider dashboards; agent must not exfiltrate or re-commit them | You rotate once; agent only verifies tree is clean via gate |
| **History rewrite + force-push** | Destructive; needs explicit operator approval; coordinated clone resets | Grant a documented one-shot approval in an issue ("authorized rewrite window"); agent can then script the rewrite under that issue ID |
| **Protected branch rules on `master`** | `master` is `protected: true` — settings API may be outside app scope | In GitHub → Settings → Branches: allow the GitHub App / your user to push or require only status checks the agent can satisfy |
| **GitHub App permission gaps** | Some orgs restrict Administration, Secrets, Workflows, or Environments | Settings → Applications → installed app → **Repository permissions**: Contents R/W, PRs R/W, Checks R/W, Commit statuses R/W, Workflows R/W (if editing Actions), Administration R if managing protection rules |
| **Device-side Termux state** | Agent runs in cloud connector, not on your phone | Optional: self-hosted runner on Termux **or** you run `termux_smoke.py` locally when hardware-specific |
| **Provider API keys / browser logins** | Auth is interactive / ToS-bound | Store in Termux-local env only; agent uses capability registry (`authenticated: true/false`) never the raw secret |
| **Linear / external trackers** | Only if not connected | Connect Linear MCP (already partially available) and grant write |

## Minimum permission checklist (GitHub App / token)

Grant these on **timerloggedout-spec/termux-monorepo** (and keep Secrets out of git):

- [ ] **Contents:** Read and write
- [ ] **Pull requests:** Read and write
- [ ] **Checks:** Read and write
- [ ] **Commit statuses:** Read and write
- [ ] **Workflows:** Read and write (only if agent maintains `.github/workflows`)
- [ ] **Issues:** Read and write (for proposal tracking issues)
- [ ] **Administration:** Read (optional Write only if agent may edit branch protection)
- [ ] **Members / metadata:** Read

**Do not** grant the agent org-wide secrets creation unless you accept that risk.

## Branch protection recipe (agent-friendly)

On `master`:

1. Require status checks: `repo gate` / `hygiene + portability gate` and `agentic termux smoke`
2. Do **not** require human review if you want full agent merge (or require review only from a bot account the agent controls)
3. Allow force pushes: **off** except for a break-glass role
4. Restrict who can push: include the GitHub App identity used by the connector

On `master-staging`:

- Prefer **no** protection or soft protection so agents can iterate quickly; promote to `master` only when both gates are green.

## Fully agentic target state

```
Proposal posted → registry.yaml updated by agent
  → items executed on branches off master-staging
  → PRs opened, gates run, agent merges to master-staging
  → agent opens promotion PR to master
  → required checks pass → agent merges to master
```

Human intervenes only for: credential rotation, destructive history ops, and first-time permission grants above.

## ChatGPT connector note

ChatGPT's GitHub connector previously returned `403 Resource not accessible by integration` on write. This Grok connector **can** write. If you want ChatGPT to execute the same pipeline, mirror the permission checklist on the ChatGPT GitHub App installation.
