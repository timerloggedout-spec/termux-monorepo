# Roadmap

## Now
- Fly.io Hindsight trial (~3 days) — verify memory loop with OpenRouter + Gemini
- Prove `hindsight_retain` / `recall` / `reflect` round-trip

## Next (1-2 weeks)
- Migrate Hindsight to persistent free tier (Hindsight Cloud or Oracle Always Free)
- Wire Hindsight's LLM provider to our own `/v1/chat/completions` via a **named** Cloudflare tunnel (stable URL, not rotating)
- Account 1 / 2 routing in session_store (concurrent DeepSeek sessions)
- Fleet roles: sweep / self-improve / tribute-4πchw1z / quota watcher

## Later
- TOON codec (once numpy aarch64 is resolvable, or pure-python encoder)
- Agora SSE `stream: true` compatibility
- Dynamic tool list from `_TOOL_TAXONOMY`
- Multi-agent concurrency with per-account quota caps
- Worktree auto-GC with `--apply`

## Parked
- `dsh` runtime (Node/pnpm on device — never fits)
- Local Hindsight (min 512MB slim — device has ~74MB free)
