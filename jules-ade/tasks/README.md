# Task queue (multi-agent)

YAML tasks under `queue/` are claimable work items for agents building `jules-ade`.

## Schema (minimal)

```yaml
id: JULES-ADE-03
title: short title
status: todo | doing | done | blocked
owner: null  # agent id when claimed
priority: P0 | P1 | P2
prompt: |
  Instructions for the implementing agent OR for a Jules cloud session.
repo: timerloggedout-spec/termux-monorepo
branch: master-staging
require_plan_approval: false
notes: |
  Optional context.
```

When `status: doing`, set `owner`. Prefer one owner per task.
