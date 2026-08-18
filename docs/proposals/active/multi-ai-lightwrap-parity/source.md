# Source — Termux Lightweight Multi-AI Web-Wrapper Parity Hub

## Problem statement

The historical TER-9 provider tree is a **Chapito-style scaffold**, not a live implementation. The current parent backends mix browser-wrapper intent with direct endpoint/token paths that the operator identified as misdirected. The replacement must be a Termux-compatible wrapper hub driven by the repeated functions of the full reverse-engineering corpus, not by a single script.

## Corpus-derived contract

| Function | Corpus evidence | Parent-owned behavior |
|---|---|---|
| Runtime | 36 scripts resolve Termux Chromium and Puppeteer. | Resolve local Chromium and the repository-installed Puppeteer package. |
| Identity persistence | 29 scripts use a browser data/profile directory. | Keep provider/account profiles outside Git; never parse or export their contents. |
| User auth handoff | 25 scripts support manual login or wait for a signed-in browser. | `connect` opens a visible provider browser; user handles provider challenges. |
| Capability discovery | 25 scripts discover fields and controls; 18 record endpoints. | `probe` emits redacted selector and request-metadata counts only. |
| Conversation transport | 14 scripts set UI fields, click send, and extract browser output. | `send` performs browser-mediated UI actions through declared selectors and normalizes only final response text. |
| Drift intelligence | Full suites cache selector and endpoint metadata. | Compare metadata-only fingerprints; mark a provider not ready when required selectors drift. |

> `probe-expert-abc.mjs` is an example in this corpus, not the canonical implementation. It is excluded from parent-hub code because it accesses direct endpoint/token behavior.

## User-owned AI Studio proxy/API references

The operator identified additional user-owned reverse-engineering references not included in the initial ChapitoAI/DeepSeek inventory. Static source-tree and manifest review covered `AIStudio2API_fork`, `AIStudioProxy_fork`, `AIStudioToAPI_fork`, `AIstudioProxyAPIClient_fork`, `AIstudioProxyAPI_fork`, `AIstudioProxyAPI_fork-node`, and `aistudio-gemini-mcp_fork`.

| Reference fork | Static role observed | Hub disposition |
|---|---|---|
| `AIstudioProxyAPI_fork` | Modular selector catalog, page-controller layers, response parsing, streaming, and extensive tests. | Reuse ordered selector fallback and visible/actionable readiness concepts only. |
| `AIStudio2API_fork` and `AIStudioProxy_fork` | Browser-proxy implementations with anti-detection browser tooling and persisted profile systems. | Reference-only; excluded from the Termux lightweight runtime. |
| `AIstudioProxyAPIClient_fork` and `AIstudioProxyAPI_fork-node` | Browser-driven OpenAI-compatible proxy variants using heavyweight automation. | Reference-only; no Playwright, Camoufox, or anti-detection component is imported. |
| `AIStudioToAPI_fork` | Multi-compatibility wrapper reference. | Compatibility-surface reference only; no duplicate server is created. |
| `aistudio-gemini-mcp_fork` | MCP-facing local bridge reference. | Optional future integration reference; outside the initial CLI runtime. |

The shared AI Studio profile now contains ordered current and legacy selector candidates from the user-owned selector catalog. The generic Puppeteer runner requires candidates to be visible and, where needed, actionable before accepting them. A probe records only boolean capability outcomes and winning selector IDs; it never stores browser profile values or raw page/network data.

## Provider state model

```text
profile-absent → connect-required → probe-required → send-ready
                              │             │
                              ├→ login-needed ├→ selector-drift
                              └→ profile-error └→ template-pending
```

The hub refuses `send` unless the provider/account profile has an in-date ready probe. A profile that is unknown, WIP, or missing fixture evidence can be connected and probed but cannot be represented as working.

## Provider matrix

| ID | Current source evidence | Initial action state |
|---|---|---|
| `deepseek` | Stable wrapper, manual-login, diagnostics, and full runtime suite. | `probe-required` |
| `mistral` | Existing lightweight harvesters plus Chapito-style selector evidence. | `probe-required` |
| `ai_studio` | Chapito-style selector module plus user-owned AI Studio selector catalog. | `probe-required` |
| `perplexity` | Chapito-style selector module with inconsistent support evidence. | `probe-required` |
| `openai_web` | Chapito-style browser selector module. | `probe-required` |
| `liner` | No local selector profile identified. | `discovery-required` |
| `openrouter` | Separate repository compatibility/routing workstream. | `delegated` |

## Architecture

The runner is a generic `.mjs` command using data-only profiles. It receives a provider ID, account alias, profile root, and action. It uses ordered selector candidates, requiring visible/actionable readiness before a browser UI send/response extraction can proceed. The Python adapter launches the runner, reads a normalized JSON result, and preserves the existing `ChatBackend` interface. Tests use offline catalog/adapter fixtures; a user-owned browser profile is required for provider-page validation.

## Boundaries

The implementation must not modify any submodule; import or run ChapitoAI’s Selenium implementation; use Selenium/Playwright; invoke direct provider endpoints; collect browser cookies/tokens/session IDs; capture raw headers, bodies, or screenshots; bypass login/MFA/challenges; or duplicate the existing OpenRouter workstream.
