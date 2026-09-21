# Provider Capability Registry

> **Status:** SPEC (P1) — expanded 2026-09-18 (BIFROST-004)

Every provider implements identity, capabilities, availability, authenticate, create_session, send, stream, history, export, health.

Capability flags: installed, authenticated, session_create/resume, streaming, history, attachments, thinking, web_search, code_execution, browser_tls, export, indexing, dispatch.

`curl_cffi` ≠ stdlib `requests`. If `requires_browser_tls` and only requests available → fail clearly.

## Live routing matrix (chat plane)

| Surface | Role | Stream | Tools/MCP | Free-tier path | Notes |
|---------|------|--------|-----------|----------------|-------|
| **Gemini AI Studio** | Primary triage/review/invoke | yes | limited | soft RPD budgets | model-router primary |
| **OpenRouter** | Free peer fallback | yes | yes | `:free` or zero pricing (ox-alpha) | Never paid on exhaustion path |
| **OmniRoute** | Free peer | yes | * | free catalog | http-llm-invoke `omni` |
| **Felo** | Free peer | yes | * | API key | http-llm-invoke `felo`; base openapi.felo.ai |
| **wrapper/** (multi-ai-cli) | Session backends | varies | limited | cookies/session | deepseek, mistral, claude, gemini web, **colab** |
| **llm_api_hub** | Unification face | yes | via upstream | N/A | OpenAI-compat contract for NexusCLI/ADE |
| **Bifrost** (evaluation) | Gateway + MCP gateway | yes | **native MCP** | self-host / provider keys in gateway | Fork: bifrost_fork; measure via bifrost-benchmarking_fork |
| **HuggingFace** | Research / optional | * | * | HF endpoints or via OpenRouter | Not first-class in model-router yet |
| **CELLCOG** | Optional human view | * | * | key present | engineering-health is zero-credit script only |

## Capability flags (selected)

| Provider | streaming | tools | browser_tls | code_execution | dispatch |
|----------|-----------|-------|-------------|----------------|----------|
| gemini (API) | yes | limited | no | no | model-router |
| openrouter | yes | yes | no | model-dep | model-router + http-llm-invoke |
| omni | yes | * | no | * | http-llm-invoke |
| felo | yes | * | no | * | http-llm-invoke |
| wrapper/colab | no | code exec | * | yes | multi-ai-cli only |
| bifrost | yes | **MCP agent loop** | no | via MCP tools | evaluation — not CI primary |

## Authority

- Runtime soft budgets: `.github/actions/model-router` + `docs/schemas/model-rotation.yaml`
- Hub contract: `llm_api_hub/ROUTING.md` + `llm_api_hub/schemas/provider-capabilities.md`
- Orchestration map: `docs/ops/ROUTING-ORCHESTRATION-MAP.md`
- Bifrost proposal: `docs/proposals/active/bifrost-gateway-integration/`
