# Why You Still Have To Do Anything — Agentic Permissions

## What the agent CAN do

Read repo/PRs, create branches, create/update files, open PRs, comment, merge when allowed, retarget PR base, submit reviews.

## What still needs YOU (human)

| Blocker | Why |
|---------|-----|
| Credential rotation | Secrets on device / provider dashboards |
| History rewrite + force-push | Destructive; needs explicit Operator approval |
| Protected branch rules on master | Settings may be outside app scope |
| GitHub App permission gaps | Contents/PRs/Checks/Workflows |
| Device-side Termux state | Agent is cloud connector, not phone |
| Provider API keys / browser logins | Interactive / ToS-bound |

## Minimum permission checklist

- [ ] Contents R/W
- [ ] Pull requests R/W
- [ ] Checks + Commit statuses R/W
- [ ] Workflows R/W
- [ ] Issues R/W
- [ ] Administration Read

Human intervenes only for: credential rotation, destructive history ops, first-time permission grants.
<<<<<<< HEAD
=======

## CodeRabbit / third-party review bots

**Repo admins cannot grant `workflows: write` to an app that does not request it.**

CodeRabbit’s published GitHub App permissions are:
- Contents, PRs, Issues, Commit statuses: Read & write
- Actions, Checks, Metadata, Discussions: Read-only
- **Workflows: not requested**

Consequence: CodeRabbit autofix can change `*.py` / docs, but GitHub will reject pushes that touch `.github/workflows/**`. That is platform policy + app manifest — not a setting an agent “removed.”

### What to do instead

1. Accept any **pending CodeRabbit permission updates** at  
   `https://github.com/settings/installations` → CodeRabbit → Configure.
2. For Actions `GITHUB_TOKEN` (jobs, not apps):  
   Settings → Actions → General → Workflow permissions → **Read and write**.
3. Workflow file edits: **OPERATOR PAT** (full scope) or a **custom GitHub App you own** with Workflows R/W.

Do not expect review bots to own CI YAML. OPERATOR owns `.github/workflows/**`.
>>>>>>> pr238
