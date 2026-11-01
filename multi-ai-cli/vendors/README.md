# multi-ai-cli / vendors

Curated reverse-engineered / web-wrapped / zero-token provider templates.
All entries are forks under `timerloggedout-spec` and registered as shallow submodules.

## Active submodules (2026-08-19)

**Registration state (corrected 2026-10-31, GAPFIX on brief #1801):** declaration in `.gitmodules` alone does not place a template in the tree — a gitlink entry is also required. Verified @master: `Chapito` is REGISTERED (gitlink @ `91721f58d25a` of `timerloggedout-spec/Chapito`, shallow per `.gitmodules`; template files present in the fork tree: `chapito/*_chat.py` provider modules + `proxy.py` + `main.py`). `CLIProxyAPI`, `gpt4free` and `ai-manus` remain DECLARED-ONLY (`.gitmodules` entries exist; gitlinks not yet registered, so their templates are NOT available as in-repo context until registered).

| Path | Upstream | Technique | Notes |
|------|----------|-----------|-------|
| `CLIProxyAPI` | router-for-me/CLIProxyAPI | OAuth CLI → local OpenAI/Anthropic/Gemini endpoints | High durability |
| `gpt4free` | xtekky/gpt4free | Public endpoint aggregation | Fallback pool |
| `ai-manus` | Simpleyyt/ai-manus | Full agent sandbox (Docker) | Reference architecture |
| `Chapito` | Yajusta/Chapito | Browser automation → local proxy | Multi-chatbot template (Anthropic, DeepSeek, Gemini, Grok, Kimi, AI Studio…) |

## Priority: Manus computer-environment replay

Manus support confirmed full Computer panel / sandbox event stream must be scraped from the web UI (no complete official export).

- Official API (`api.manus.ai` / `api.manus.im`) still useful for task metadata + files.
- Computer replay (terminal + browser + file events) lives in the authenticated web layer + `?replay=1` share links.
- Probe path: deepcli core (WAF / AWS cookies / WASM POW) + `curl_cffi` + optional Playwright for WS intercept.
- Target schema for ML pipeline: timestamped JSONL of `{event_type, payload, task_id, share_id}`.

## Next operators

```bash
git submodule update --init --recursive multi-ai-cli/vendors
# then extend multi-ai-cli/harvesters/manus_*.{py,mjs}
```

See also the research dump in the conversation that seeded this expansion.
