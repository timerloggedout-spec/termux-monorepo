# llm-api-hub local server

Expose OpenAI-compatible `POST /v1/chat/completions` on `127.0.0.1:8787`.

## Implementation plan

1. Thin ASGI/Flask/stdlib HTTP wrapper around `multi-ai-cli` `ChatDispatcher`.
2. Map `model`:
   - `wrapper/deepseek` → `ChatDispatcher.send("deepseek", …)`
   - `wrapper/mistral` → `mistral`
   - `openrouter/...` → HTTPS to OpenRouter
3. Convert multi-turn hub `messages` → backend context list.
4. Return OpenAI-shaped JSON (see `schemas/provider-capabilities.md`).

Until the server lands, NexusCLI may call:

```bash
cd multi-ai-cli && python cli.py chat -p deepseek "prompt"
```

Do not ship NexusCLI as a second DeepSeek client long-term (PR #40 architectural constraint).
