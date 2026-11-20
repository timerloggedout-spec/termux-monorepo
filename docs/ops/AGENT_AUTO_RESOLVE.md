# Agent auto-resolve (LIVE on master)

**Agent:** [Grok](https://x.com/grok)

Workflows on **default branch `master`** so `pull_request_review` / review_comment events fire immediately.

| Event | Action |
|-------|--------|
| CodeRabbit / Devin / Copilot review or review comment | GHA posts `@jules` Auto-resolve (20m debounce) |
| Same | Linear subtask under `PR #N agent feedback rollup` + `agent-feedback` |
| CodeRabbit | `.coderabbit.yaml` autofix enabled |

Secrets: `LINEAR_API_KEY` (subtasks), optional `JULES_API_KEY`.

Signed-off-by: Grok <grok@x.ai>
