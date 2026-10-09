# ATES identity skip — 2026-10-09

Bound to master `8e4fbc08484887bbce177c5c4c17d13ef8f95d5e`.

## Failure being closed

- Issue: https://github.com/timerloggedout-spec/termux-monorepo/issues/1026
- Workflow: Agent Throughput Evidence
- Failed run: https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/37125900597
- Failed job: 111211005831, step `Collect trusted workflow metadata`
- Cause: `core.setFailed` when `workflow_run.name` was outside the explicit Gemini/DeepSeek identity map.

## Current tip evidence

- Later master runs of the same workflow concluded success:
  - https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/37879228774
  - https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/37879228651
- PR production ledger recent master runs also concluded success (issue #1025 is stale relative to tip).

## Change

Unmatched identity and installation rate-limit paths set `skip=true` and return. Downstream emit steps require `steps.collect.outputs.skip != 'true'`.

Credential material from issue #184 is not copied into this receipt. Last-used evidence stays on the issue; token values must be rotated if they were ever pasted into comments.
