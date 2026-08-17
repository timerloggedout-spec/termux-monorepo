# llm-api-hub — LLM API Unification Hub

**Canonical model plane for the Termux monorepo ADE.**

NexusCLI, kai9000 (dev skills), archwiz dispatch, and agents **must** call this hub
(or `multi-ai-cli` which implements it). Do not hard-code provider SDKs in face CLIs.

## Why not a dotfile (`~/.mcp`, `~/.llm-api`)?

| Concern | Decision |
|---------|----------|
| Versioned code + schemas | **Tracked in repo** → `llm-api-hub/` at monorepo root |
| Secrets / runtime tokens | **Dot dirs** → `~/.multi-ai-tokens/`, `~/.deepcli/`, session stores |
| MCP server configs | May live under `~/.kai9000/mcp/` or `.mcp/` **locally**; templates stay in-repo |

Rule: **code and contracts in git; credentials and session blobs out of git.**

## Common LLM HTTP formats (what we normalize to)

### 1. OpenAI Chat Completions (de-facto standard)

Most gateways speak this:

```http
POST /v1/chat/completions
Authorization: Bearer <key>
Content-Type: application/json

{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "system", "content": "…"},
    {"role": "user", "content": "…"}
  ],
  "stream": false,
  "temperature": 0.7
}
```

Compatible / near-compatible:
- **OpenAI** native
- **OpenRouter** (`https://openrouter.ai/api/v1`)
- **Groq**, **Together**, **Fireworks**, **DeepSeek official API**, **Mistral API**, **xAI Grok API**, many local servers (Ollama openai compat, vLLM, LM Studio)

### 2. Anthropic Messages API

```http
POST /v1/messages
x-api-key: <key>
anthropic-version: 2023-06-01

{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 1024,
  "messages": [{"role": "user", "content": "…"}]
}
```

Hub maps Anthropic ↔ OpenAI message shapes when routing.

### 3. Google Gemini (generateContent)

Google AI Studio / Vertex use a different body (`contents` / `parts`).
Hub adapters convert to OpenAI messages for callers.

### 4. Web-wrapper / session backends (no API key)

deepcli, multi-ai-cli backends (`DeepSeekBackend`, `MistralWebBackend`, …) use
cookies/tokens + proprietary endpoints. Hub exposes them as **virtual models**:

| Virtual model id | Backend |
|------------------|--------|
| `wrapper/deepseek` | multi-ai-cli deepseek |
| `wrapper/mistral` | multi-ai-cli mistral |
| `wrapper/claude` | multi-ai-cli claude web |
| `wrapper/gemini` | multi-ai-cli gemini web |
| `openrouter/<slug>` | OpenRouter key |
| `openai/<model>` | OpenAI key (optional) |

## Layout

```
llm-api-hub/
  README.md
  schemas/
  server/
  clients/
  ROUTING.md
```

## Routing priority (production)

1. Web wrappers / multi-ai-cli backends (no spend key when session valid)
2. OpenRouter (keys you already hold; broad model menu)
3. Direct provider keys (only when required)

## Consumers

- **NexusCLI** → only `multi-ai-cli` or this hub (`POST /v1/chat/completions`)
- **kai9000 ADE skills** → same hub (not raw Anthropic/Google keys in skill env)
- **archwiz dispatch** → multi-ai-cli / hub for model calls

## Crypto vs ADE split

| Track | Location |
|-------|----------|
| ADE / orchestrator skills, MCP templates, workflows (dev) | monorepo: `llm-api-hub/`, `.agents/skills/`, `archwiz/` |
| Crypto-facing kai9000 + Hermes | `_1-Projects/a/kai9000-crypto/` (pointer / sparse ref) |

See `docs/ADE_KAI9000_SPLIT.md`.
