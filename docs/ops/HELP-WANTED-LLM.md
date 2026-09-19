# Help-wanted + models — USE THE KEYS

## Credential rule (issue #184)

- **Actions secrets by name** — never paste token values into issues, PRs, or chat.
- Inventory SSOT: issue **#184** (names + last-used notes only).
- LLM gate for free peers: **`OPENROUTER_API_KEY`** (also `OMNI_*`, `FELO_AI_API`, `GEMINI_API_KEY`).
- GitHub write path: **`OPERATOR_GITHUB_TOKEN`** / `ARCHWIZ_GITHUB_TOKEN` / `OPERATOR_TOKEN`.

If a value ever appears in an issue body, **rotate it** and keep only the secret name in docs.

## What uses models now

| Workflow | Secrets | Action |
|----------|---------|--------|
| `help-wanted-llm-assist.yml` | `OPENROUTER_API_KEY` (+ omni/felo), OPERATOR PAT | model-router → OpenRouter/Omni chat → comment on **foreign** PR |
| claim / contribute / followup | OPERATOR PAT only | deterministic write path (never blocked on LLM quota) |

## Free-tier

OpenRouter: `:free` suffix or zero pricing (`docs/schemas/model-rotation.yaml`).
Quota miss → skip + notice, do not fail the lane.

## Cadence

- Schedule every 6h + `workflow_dispatch` + `repository_dispatch: help-wanted-llm-assist`

Agent-Identity: Grok (Administrator)
