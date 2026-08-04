# Why You Still Have To Do Anything — Agentic Permissions

Honest boundary list. Everything else is already agent-operable via the GitHub + Linear connectors on this account.

## What the agent CAN do today (proven)

| Action | Status |
|--------|--------|
| Read repo, branches, PRs, files, checks | ✅ |
| Create branches | ✅ |
| Create/update files + commit | ✅ |
| Open PRs | ✅ |
| Comment on issues/PRs | ✅ |
| Merge PRs (when mergeable + allowed) | ✅ (merged #11) |
| Retarget PR base branch | ✅ |
| Submit PR reviews (COMMENT / REQUEST_CHANGES / APPROVE) | ✅ |
| **Linear: list / get / create / update issues** | ✅ MCP `linear___*` |
| **Linear: start / done / comment via CLI** | ✅ `archwiz/linear_client.py` |
| **Linear agent protocol (binding)** | ✅ `docs/LINEAR-AGENT-PROTOCOL.md` |

## What still needs YOU (human-only or policy)

| Blocker | Why agent cannot | Fix to go fully agentic |
|---------|------------------|-------------------------|
| **Credential rotation** | Secrets live on device / provider dashboards; agent must not exfiltrate or re-commit them | You rotate once; agent only verifies tree is clean via gate |
| **History rewrite + force-push** | Destructive; needs explicit operator approval; coordinated clone resets | Grant a documented one-shot approval in an issue ("authorized rewrite window"); agent can then script the rewrite under that issue ID |
| **Protected branch rules on `master`** | `master` is `protected: true` — settings API may be outside app scope | In GitHub → Settings → Branches: allow the GitHub App / your user to push or require only status checks the agent can satisfy |
| **GitHub App permission gaps** | Some orgs restrict Administration, Secrets, Workflows, or Environments | Settings → Applications → installed app → **Repository permissions**: Contents R/W, PRs R/W, Checks R/W, Commit statuses R/W, Workflows R/W (if editing Actions), Administration R if managing protection rules |
| **Device-side Termux state** | Agent runs in cloud connector, not on your phone | Optional: self-hosted runner on Termux **or** you run `termux_smoke.py` locally when hardware-specific |
| **Provider API keys / browser logins** | Auth is interactive / ToS-bound | Store in Termux-local env only; agent uses capability registry (`authenticated: true/false`) never the raw secret |
| **LINEAR_API_KEY on device** | Needed only for on-device `linear_client` / `linear_sync` (MCP path does not need it) | Export in Termux env; never commit |

## Linear is connected

Agents **must** follow `docs/LINEAR-AGENT-PROTOCOL.md`:

- Start work → issue **In Progress**
- Open PR → `Implements: TER-N` + comment PR URL on issue
- Merge to **`master-staging`** → **Done** + evidence

Connected agents use MCP (`linear___save_issue`, etc.). On-device/CI use:

```bash
export LINEAR_API_KEY=lin_api_...
python3 -m archwiz.linear_client start TER-14
python3 -m archwiz.linear_client done TER-14 --pr 16
```

## Branch model (binding)

```
feature/*  ──PR──►  master-staging   ← integration spine (always exists)
                        │
                        │  selective cherry-pick / focused promotion PRs only
                        │  NEVER merge master-staging → master wholesale
                        ▼
                     master          ← stable, green, protected
```

**`master-staging` is a permanent gate, not a temporary buffer.**

- Agents land work on `master-staging` via feature PRs.
- Promotion to `master` is **selective**: only commits/PRs that are ready, never “merge the whole staging branch.”
- `master-staging` must **not** be deleted, fast-forward-merged away, or treated as disposable.

See also Operator note on TER-14: *"master-staging is for selective merge to master meaning master-staging is meant to never merge to master completely."*

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

- Soft or no protection so agents can iterate; **keep the branch permanently** as the integration target.

## Fully agentic target state

```
Linear TER-* + registry.yaml → agent picks Todo
  → Linear In Progress + branch off master-staging
  → PR Implements: TER-N → gates green → merge to master-staging
  → Linear Done + ITEMS.md update
  → selective promotion PR(s) of ready commits to master (never wholesale staging merge)
```

Human intervenes only for: credential rotation, destructive history ops, and first-time permission grants above.

## ChatGPT connector note

ChatGPT's GitHub connector previously returned `403 Resource not accessible by integration` on write. This Grok connector **can** write. If you want ChatGPT to execute the same pipeline, mirror the permission checklist on the ChatGPT GitHub App installation. Connect Linear MCP (or pass LINEAR_API_KEY) for full tracker parity.
