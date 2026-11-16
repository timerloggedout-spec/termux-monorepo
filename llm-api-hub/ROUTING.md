# llm-api-hub Routing

## Priority order (outbound)

1. **Local web wrappers** (highest priority when healthy)
   - DeepSeek wrapper (already available)
   - Future: Claude/Anthropic, Gemini, Grok, etc. browser/session wrappers

2. **OpenRouter**
   - Single key, broad model catalog
   - Prefer for evaluation, failover, and models without a dedicated wrapper

3. **multi-ai-cli** provider registry / ChatDispatcher
   - Full matrix of backends
   - Session stores, adapters (Figma, GitHub, …)

4. **Direct provider keys** (only when explicitly enabled in config)
   - Last resort; ADE code itself must never embed keys

## Model alias examples

| Alias | Resolves to | Notes |
|-------|-------------|-------|
| `hub/default` | multi-ai-cli default or OpenRouter auto | Safe default for ADE |
| `hub/deepseek-chat` | DeepSeek wrapper → deepseek-chat | Coding / cost sweet spot |
| `hub/claude-sonnet` | Anthropic Messages (via adapter) or OpenRouter | Strong reasoning |
| `hub/gemini-pro` | Gemini generateContent (via adapter) | Long context / multimodal |
| `openrouter/auto` | OpenRouter router | Best-effort cheapest/best |
| `multi-ai/<engine>` | Named multi-ai-cli engine | Explicit control |

## Inbound acceptance

- Primary: OpenAI Chat Completions (`/v1/chat/completions`)
- Optional alternate paths (normalize immediately):
  - `/v1/messages` (Anthropic)
  - `/v1beta/models/{model}:generateContent` (Gemini)

All responses returned in the format the client requested (or OpenAI if unspecified).

## Health & fallback

- Each backend exposes a cheap health probe.
- On 4xx/5xx or timeout the router tries the next priority that can serve the requested model family.
- Circuit-breaker style cooldown per backend to avoid thundering herd.
