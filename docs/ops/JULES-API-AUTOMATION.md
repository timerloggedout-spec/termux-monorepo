# Jules API automation — zero HITL recovery

**Implements:** #145 · **PR:** #148

Base URL: `https://jules.googleapis.com/v1alpha`  
Auth: `x-goog-api-key: ${{ secrets.JULES_API_KEY }}`

## Binding

```text
context_key = pr-<number>-<short-head-ref>
work-context cache JSON:
  { context_key, session_id, last_state, last_head_sha, empty_commit_count, continue_preferred }
```

Never store Class 3/4 material.

## Session states → automation

| State | Action |
|-------|--------|
| `AWAITING_PLAN_APPROVAL` | **YOLO:** `POST .../sessions/{id}:approvePlan` (auto-approve). No human. |
| `AWAITING_USER_FEEDBACK` | `POST .../sessions/{id}:sendMessage` with disposition-first continue prompt |
| `FAILED` | `sendMessage` recovery prompt once per debounce window; bind same `session_id` |
| `PAUSED` | resume via API if available; else `sendMessage` |
| `COMPLETED` + head commit `files:[]` / empty stats | treat as **eval FAIL** (empty commit); `sendMessage` “non-empty diff required”; increment `empty_commit_count` |
| `IN_PROGRESS` / `PLANNING` / `QUEUED` | no-op (wait) |
| no `session_id` bound | create session **only** if concurrent quota allows; else `@jules` comment secondary path |

## YOLO mode

Repo var `JULES_YOLO_APPROVE=1` (default **on** for this ADE). When set:

1. Poll bound session state on continuous-ops + after auto-jules invoke.
2. If `AWAITING_PLAN_APPROVAL` → approvePlan immediately.
3. Log `<!-- jules-yolo-approve -->` marker on PR (audit only).

## Continue-only quota

- Free tier soft gates: concurrent ≤3, daily ≤15 (verify docs; surface skip reason).
- Prefer `sendMessage` on bound session over `POST /sessions` create.
- Skip create with visible job summary when at cap.

## Secondary path

`@jules` PR comments remain valid triggers when API key absent. API is primary.

## Related

- [`jules-session-management.md`](jules-session-management.md)
- [`AGENT-EVAL-MATRIX.md`](AGENT-EVAL-MATRIX.md)
- #120 agent-context-store · continuous-ops · `agent-review-auto-jules.yml`

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-jules-api
