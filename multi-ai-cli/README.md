# Multi-AI CLI — Lightweight Termux Web-Wrapper Hub

This package provides a parent-owned, Termux-compatible provider hub that function-matches the repository’s reverse-engineering corpus. It uses the repository’s existing Chromium/Puppeteer pattern, user-owned per-provider browser profiles, manual sign-in, selector readiness probes, browser-mediated UI sends, and normalized responses. It does **not** modify `deepseek-cli/deepterm`, import ChapitoAI’s Selenium code, run Selenium or Playwright, invoke direct provider endpoints, or create another OpenRouter server.

## Provider lifecycle

Each provider/account alias progresses through the following local lifecycle:

```text
connect-required → connect → probe-required → probe → send-ready → chat
```

The `connect` command opens a visible provider browser. Complete the provider-owned sign-in or challenge there, then interrupt the command and run `probe`. The probe stores only readiness and selector metadata in `~/.multi-ai-cli/wrappers/status/`; the browser profile itself stays under `~/.multi-ai-cli/wrappers/profiles/` and is not read or exported by the hub.

| Provider | Initial state | Source lineage | Next action |
|---|---|---|---|
| `deepseek` | `probe-required` | DeepSeek stable wrapper, manual login, and runtime-suite examples. | Connect, probe, then chat. |
| `mistral` | `probe-required` | Mistral diagnostics/harvesters and Chapito-style selector example. | Connect, probe, then chat. |
| `ai_studio` | `probe-required` | Chapito-style WIP selector profile. | Connect, probe, then chat only when probe succeeds. |
| `perplexity` | `probe-required` | Chapito-style selector profile. | Connect, probe, then chat only when probe succeeds. |
| `openai_web` | `probe-required` | Chapito-style browser selector profile. | Connect, probe, then chat. |
| `liner` | `discovery-required` | No verified shared selector fixture. | Configure a local selector profile, connect, probe, then chat. |
| `openrouter` | `delegated` | Existing repository compatibility/routing workstream. | Use its owning workstream; it is not a browser-wrapper entry. |

## Commands

Run commands from `multi-ai-cli/`.

```bash
# Inspect every provider state without starting Chromium.
python3 cli.py providers list
python3 cli.py providers capabilities deepseek --account personal

# Open a visible, user-mediated browser for login; then stop it with Ctrl+C.
python3 cli.py providers connect deepseek --account personal

# Verify selector/readiness metadata after the user completes sign-in.
python3 cli.py providers probe deepseek --account personal

# Send only after the prior probe reports send-ready.
python3 cli.py chat --provider deepseek --account personal "Explain this repository layout."
```

Use `--profile-root /path` on `providers` or `chat` to choose an alternate local state root. This is useful for an isolated account alias or tests.

### Liner and future provider discovery

A provider with no committed selector fixture must be configured locally before it can be probed. The configuration is data-only; it contains the user-validated URL and browser selectors, never cookies, tokens, endpoint headers, or response data.

```bash
python3 cli.py providers configure liner --account personal \
  --url 'https://provider.example/chat' \
  --input-mode textarea \
  --input-selector 'textarea#prompt' \
  --submit-selector 'button#send' \
  --response-selector 'article.answer:last-child' \
  --ready-selector 'textarea#prompt'

python3 cli.py providers connect liner --account personal
python3 cli.py providers probe liner --account personal
```

The command writes the local selector profile with owner-only permissions. A selector profile becomes send-capable only after its readiness probe passes. If a provider UI changes, the probe reports selector drift and `chat` remains blocked until the local fixture is corrected.

## Privacy and control boundaries

The wrapper catalog and normalized status contain non-secret descriptors, timestamps, selector booleans, and fingerprints only. The hub does not read or print cookies, browser local storage, tokens, headers, request bodies, response bodies, screenshots, or session identifiers. Login, MFA, CAPTCHA, and other challenge steps are completed by the user in the provider browser; the hub has no challenge-solver behavior.

## Offline validation

The focused tests never start Chromium and never contact provider services:

```bash
node tests/test_lightwrap_contract.mjs
python3 -m unittest tests/test_lightwrap_backend.py -v
```
