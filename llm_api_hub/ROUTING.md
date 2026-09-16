# llm-api-hub routing

## Resolution order

```
request(model, messages)
  │
  ├─ model starts with wrapper/  → multi-ai-cli backend (cookies/session)
  ├─ model starts with openrouter/ → OpenRouter /v1/chat/completions
  ├─ model starts with openai/     → OpenAI API (optional)
  ├─ model starts with anthropic/  → Anthropic Messages (mapped)
  └─ else → treat as OpenRouter slug if OPENROUTER_API_KEY set
            else fail with clear error
```

## multi-ai-cli backends (master tip)

| name | module |
|------|--------|
| deepseek | `backends.deepseek.DeepSeekBackend` |
| mistral | `backends.mistral_web.MistralWebBackend` |
| claude | `backends.claude_web.ClaudeWebBackend` |
| gemini | `backends.gemini_web.GeminiWebBackend` |
| colab | `backends.colab.ColabBackend` |

Tokens/cookies: `multi-ai-cli/config.yaml` + `~/.multi-ai-tokens/` / deepcli paths.

## Env vars (runtime, not in git)

```
OPENROUTER_API_KEY=
OPENAI_API_KEY=          # optional
ANTHROPIC_API_KEY=       # optional
LLM_API_HUB_PORT=8787    # local server default
LLM_API_HUB_HOST=127.0.0.1
```

## NexusCLI contract

NexusCLI **must not** embed DeepSeek PoW/API directly long-term.

Preferred:

```python
# clients/openai_compat.py
POST http://127.0.0.1:8787/v1/chat/completions
{ "model": "wrapper/deepseek", "messages": [...] }
```

or CLI:

```bash
python -m multi_ai_cli.cli chat -p deepseek "…"
```
