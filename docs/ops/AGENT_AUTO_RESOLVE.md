# Agent auto-resolve (implemented)

**Agent:** [Grok](https://x.com/grok)

## What was automated

| Event | Action |
|-------|--------|
| CodeRabbit / Devin / Copilot **PR review** or **review comment** | GHA posts `@jules` **Auto-resolve** (debounced 20m) |
| Same bot comments | GHA creates **Linear subtask** under `PR #N agent feedback rollup` + label `agent-feedback` |
| CodeRabbit config | `.coderabbit.yaml` **autofix enabled** + `master-staging` |

Workflows:

- `.github/workflows/agent-review-auto-jules.yml`
- `.github/workflows/agent-feedback-linear-sync.yml`

## Secrets / vars (operator once)

| Name | Required | Purpose |
|------|----------|---------|
| `LINEAR_API_KEY` | for Linear sync | Subtasks |
| `JULES_API_KEY` | optional | Extra API path; **@jules comment is primary** |
| repo var `JULES_AUTO_INVOKE` | optional | Set `0` to disable API job |

## Jules UI

- Install **Google Labs Jules** App on this repo.
- Create GitHub label **`jules`** (issue auto-start).
- For PR feedback: leave **Reactive Mode off** so Jules acts on review activity; GHA still posts `@jules` for Reactive Mode users.

## Devin (13-day review window)

- Keep **Devin Review** enrolled for this repo.
- Enable **Auto-Fix** in Devin settings when possible (applies suggestions).
- Bot comments still flow into Jules + Linear via GHA even if Devin only reviews.

## Stop noise

- Marker `<!-- agent-auto-jules -->` prevents re-entry loops.
- 20-minute debounce per PR on Jules pings.

Signed-off-by: Grok <grok@x.ai>
