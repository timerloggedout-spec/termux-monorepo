# Help-wanted follow-up (timely relevance)

## Problem

Opening the upstream PR is not the end. Maintainers leave **CHANGES_REQUESTED** / issue comments; without triggers those rot (e.g. vedantnimbarte/zero#81).

## Triggers

| Mechanism | Latency | Scope |
|-----------|---------|--------|
| `help-wanted-followup.yml` **schedule** `*/2h` | ≤ ~2h | All open PRs `author:timerloggedout-spec review:changes_requested` |
| `workflow_dispatch` `mode=poll` | on demand | same |
| `workflow_dispatch` `mode=zero-81-revise` | on demand | Apply known revision for zero#81 |
| Foreign **webhooks** | near real-time | Requires GitHub App install on target repos (backlog) |

Monorepo-internal review already has `peer-review-orchestrator` (`pull_request_review`, `issue_comment`). External help-wanted targets do **not** fire those events into our repo.

## Models used so far (routing SSOT)

From `docs/ops/ROUTING-ORCHESTRATION-MAP.md` + `docs/schemas/model-rotation.yaml` / success matrix:

| Plane | Models / providers selected in practice |
|-------|------------------------------------------|
| **Review / ops (GHA)** | Gemini family primary when quota allows (`gemini-*-flash` / rotation); OpenRouter **free** fallback (`:free` / zero price) — e.g. `qwen/qwen3-coder:free`, `deepseek/deepseek-r1:free`, `meta-llama/llama-3.3-70b-instruct:free`, `google/gemma-*-it:free` |
| **Peer PR review** | CodeRabbit (default `REQUIRED_PROVIDERS`); optional Jules / other Apps via policy vars |
| **Chat / llm_api_hub** | OpenRouter, multi-ai-cli wrappers (DeepSeek, Colab, …), engine aliases → OpenRouter |
| **Help-wanted execute** | Deterministic scripts + OPERATOR PAT — **not** an LLM pick for claim/PR machinery |

Free-tier rule unchanged: exhaustion → OpenRouter free only; never hard-fail CI on quota.

Agent-Identity: Grok (Administrator)
