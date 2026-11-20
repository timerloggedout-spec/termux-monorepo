# Provider capabilities (hub contract)

| Provider | Transport | Auth | Stream | Tools | Notes |
|----------|-----------|------|--------|-------|-------|
| wrapper/deepseek | multi-ai-cli | cookies/token | yes* | limited | Prefer over official key when session live |
| wrapper/mistral | multi-ai-cli | cookies/token | * | * | Web backend |
| wrapper/claude | multi-ai-cli | cookies/token | * | * | Web backend |
| wrapper/gemini | multi-ai-cli | cookies/token | * | * | Web backend |
| wrapper/colab | multi-ai-cli | cookies | no | code exec | Not a chat LLM primary |
| openrouter/* | HTTPS OpenAI-compat | API key | yes | yes | Primary paid fallback |
| openai/* | HTTPS | API key | yes | yes | Optional |
| anthropic/* | HTTPS Messages | API key | yes | yes | Map to OpenAI messages at edge |

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
