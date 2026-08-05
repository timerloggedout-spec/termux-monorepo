# llm-api-hub

**Unified OpenAI-compatible API surface for the Fully Automated Agentic Development Environment (ADE).**

NexusCLI, multi-ai-cli consumers, kai9000 skills/workflows, and any agent **must** route model calls through this hub (or `multi-ai-cli` backends that implement the same contract).  
No direct provider API keys in ADE code paths. Keys live only in hub / multi-ai-cli / wrapper config.

## Contract

Primary public surface (OpenAI Chat Completions shape):

```
POST /v1/chat/completions
Authorization: Bearer <hub-or-multi-ai-token>
Content-Type: application/json
```

Request/response follow the OpenAI Chat Completions schema (see `schemas/`).  
The hub normalizes inbound traffic and routes outbound to:

| Priority | Backend | Notes |
|----------|---------|-------|
| 1 | Local web wrappers | e.g. DeepSeek wrapper already done |
| 2 | OpenRouter | single key, many models |
| 3 | multi-ai-cli ChatDispatcher / provider registry | full provider matrix |
| 4 | Direct provider (only if explicitly enabled) | fallback |

Virtual model names (examples):

- `hub/deepseek-chat`
- `hub/claude-sonnet`
- `hub/gemini-pro`
- `openrouter/auto`
- `multi-ai/default`

## Common LLM API formats (why we normalize)

| Format | Endpoint pattern | Used by | Notes |
|--------|------------------|---------|-------|
| **OpenAI Chat Completions** | `POST /v1/chat/completions` | OpenAI, OpenRouter, DeepSeek, most aggregators, local servers | **Internal lingua franca of this hub** |
| **OpenAI Responses** | `POST /v1/responses` | Newer OpenAI surface | Optional adapter |
| **Anthropic Messages** | `POST /v1/messages` | Anthropic Claude, some DeepSeek modes | Converted → OpenAI shape |
| **Google Gemini** | `POST /v1beta/models/{model}:generateContent` | Gemini | Converted → OpenAI shape |
| OpenAI-compatible | various | Groq, Together, Fireworks, Ollama, vLLM, etc. | Pass-through after auth rewrite |

Hub accepts the OpenAI Chat Completions request and (optionally) accepts Anthropic/Gemini on alternate paths, normalizes to internal OpenAI, then routes.

## Layout

```
llm-api-hub/
├── README.md                 # this file
├── ROUTING.md                # priority + model alias table
├── schemas/
│   ├── openai-chat-completions.example.json
│   └── provider-capabilities.md
├── clients/
│   └── openai_compat.py      # thin Python client (urllib, no heavy deps)
├── server/
│   └── README.md             # bind multi-ai-cli ChatDispatcher to :8787
└── docs/
```

## Consumers (must use hub or multi-ai-cli)

- NexusCLI (sessions, TUI, export)
- kai9000 ADE skills & workflows (coding, MCP, product-builder, research)
- Any future agent that needs models

## Crypto isolation rule

Crypto / Hermes / Binance / Polymarket / portfolio agents **must not** live in the ADE monorepo path.  
They are referenced only via sparse checkout / pointer under `_1-Projects/a/kai9000-crypto/`.  
See `docs/ADE_KAI9000_SPLIT.md`.

## Quick start (client)

```python
from llm_api_hub.clients.openai_compat import chat_completions, assistant_text

resp = chat_completions(
    model="hub/deepseek-chat",
    messages=[{"role": "user", "content": "Hello from ADE"}],
    base_url="http://127.0.0.1:8787/v1",
)
print(assistant_text(resp))
```

Default port for the local hub server: **8787**.

## Status

Scaffold + contract + split docs. Server binding to multi-ai-cli is the next production step.
