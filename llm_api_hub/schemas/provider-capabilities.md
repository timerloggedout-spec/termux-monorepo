# Provider capabilities (hub contract)

| Provider | Transport | Auth | Stream | Tools | Notes |
|----------|-----------|------|--------|-------|-------|
| wrapper/deepseek | multi-ai-cli | cookies/token | yes* | limited | Prefer over official key when session live |
| wrapper/mistral | multi-ai-cli | cookies/token | * | * | Web backend |
| wrapper/claude | multi-ai-cli | cookies/token | * | * | Web backend |
| wrapper/gemini | multi-ai-cli | cookies/token | * | * | Web backend |
| wrapper/colab | multi-ai-cli | cookies | no | code exec | Not a chat LLM primary |
| openrouter/* | HTTPS OpenAI-compat | API key | yes | yes | Free peer + paid optional; CI free-only on exhaustion |
| openai/* | HTTPS | API key | yes | yes | Optional |
| anthropic/* | HTTPS Messages | API key | yes | yes | Map to OpenAI messages at edge |
| omni/* | HTTPS OpenAI-compat | API key | yes | * | OmniRoute peer; http-llm-invoke |
| felo/* | HTTPS OpenAI-compat | API key | yes | * | Felo peer; base https://openapi.felo.ai/api/v1 |
| bifrost/* | HTTPS OpenAI-compat or MCP | gateway-held keys | yes | **MCP native** | Evaluation gateway (bifrost_fork). Not CI primary. Drop-in base_url when self-hosted. |

\* Stream support depends on backend implementation maturity.

## Required fields on every hub response (non-stream)

OpenAI-shaped:

```json
{
  "id": "chatcmpl-…",
  "object": "chat.completion",
  "choices": [{
    "index": 0,
    "message": {"role": "assistant", "content": "…"},
    "finish_reason": "stop"
  }],
  "model": "wrapper/deepseek",
  "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
}
```

Hub may set usage to 0 when wrappers do not report tokens.

## Resolution order (see ROUTING.md)

1. `wrapper/*` → multi-ai-cli backends
2. `openrouter/*` → OpenRouter
3. `openai/*` / `anthropic/*` optional direct
4. else → OpenRouter slug if key set, else clear error

Bifrost evaluation: callers may point OpenAI SDK `base_url` at a running Bifrost instance instead of llm_api_hub when measuring gateway overhead (benchmarking_fork + mocker).
