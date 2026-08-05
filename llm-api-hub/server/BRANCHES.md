# Server variants & branches

| Branch | Server mode | Dependency on ChatDispatcher | Use case |
|--------|-------------|------------------------------|----------|
| `main` (or `ter-40-…`) | **Integrated** | Yes – binds into multi-ai-cli | Primary ADE production path |
| `ter-41-hub-server-standalone` | **Standalone** | No – pure HTTP process | Independent hub, web-wrapper demos, isolation testing |

Both expose the same OpenAI Chat Completions contract on `:8787`.

## Google AI Studio / Gemini note (standalone)

Standalone already demonstrates a **non-OpenAI** upstream:

- `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
- Also available: `streamGenerateContent`, `countTokens`, `embedContent`, `batchGenerateContent`, Live `BidiGenerateContent` (WebSocket), and the newer **Interactions** API (`POST /v1beta/interactions`).

The hub normalizes those responses back to OpenAI Chat Completions so NexusCLI stays format-agnostic.
