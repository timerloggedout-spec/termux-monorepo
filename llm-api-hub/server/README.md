# llm-api-hub local server

`llm-api-hub` is the canonical local model plane for the Termux monorepo ADE. It exposes an OpenAI-compatible `POST /v1/chat/completions` endpoint and keeps provider-specific credentials and wrapper session state outside the repository.

## Start the server

From the repository root:

```bash
python3 -m pip install -r llm-api-hub/server/requirements.txt
cd llm-api-hub/server
uvicorn app:app --host 127.0.0.1 --port 8787
```

Because the directory name contains a hyphen, launching from the server directory is the portable form in Termux:

```bash
cd llm-api-hub/server
uvicorn app:app --host "${LLM_API_HUB_HOST:-127.0.0.1}" --port "${LLM_API_HUB_PORT:-8787}"
```

The server binds to loopback by default. Set `LLM_API_HUB_KEY` to require a Bearer token; never commit provider keys or hub keys.

## Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Process health and configured-upstream status; does not require a key. |
| `GET /v1/models` | Advertises wrapper models and configured upstream families. |
| `POST /v1/chat/completions` | Accepts OpenAI chat-completion requests. |
| `GET /docs` | Local FastAPI documentation. |

Example request:

```bash
curl -s http://127.0.0.1:8787/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer local' \
  -d '{
    "model": "wrapper/deepseek",
    "messages": [{"role": "user", "content": "Say hello."}],
    "stream": false
  }'
```

## Routing

| Model prefix | Route | Required runtime configuration |
|---|---|---|
| `wrapper/deepseek` | Existing `multi-ai-cli` DeepSeek wrapper | `DEEPSEEK_TOKEN`, configured token file, or existing token provider |
| `wrapper/mistral` | Existing Mistral WebSocket bridge | Bridge on `ws://127.0.0.1:9876` |
| `wrapper/claude` | Existing Claude web wrapper | Claude token configuration |
| `wrapper/gemini` | Existing Gemini web wrapper | Gemini token/cookie configuration |
| `wrapper/colab` | Existing Colab wrapper | Colab cookie configuration |
| `openrouter/<model>` | OpenRouter OpenAI-compatible API | `OPENROUTER_API_KEY` |
| `openai/<model>` | OpenAI-compatible upstream | `OPENAI_API_KEY` and optional `OPENAI_BASE_URL` |
| `anthropic/<model>` | Anthropic Messages API mapped to OpenAI shape | `ANTHROPIC_API_KEY` |

Wrapper backends are synchronous today. If a caller sets `stream: true`, the hub emits a standards-compatible SSE sequence after the wrapper or upstream completes; it does not claim token-level streaming from a wrapper that cannot provide it.

## Client contract

Use [`../clients/openai_compat.py`](../clients/openai_compat.py) from Python consumers. The client targets `/v1` by default and reads `LLM_API_HUB_BASE` and `LLM_API_HUB_KEY` from the environment. The server may also be used by any OpenAI-compatible SDK by setting its base URL to `http://127.0.0.1:8787/v1`.
