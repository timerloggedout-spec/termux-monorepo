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
