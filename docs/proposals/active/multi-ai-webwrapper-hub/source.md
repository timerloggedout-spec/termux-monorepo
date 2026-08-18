# Source — Multi-AI Web-Wrapper Hub

## Decision

The provider hub is a **non-secret orchestration layer** above existing provider runtimes. Its first version adds selection, lifecycle state, and manual next-step guidance only. It does not replace the selected DeepCLI browser-session web-wrapper, reimplement its request mechanics, store browser state, or create another compatibility server.

> The selected baseline is the current DeepCLI lineage on `master`; it is the only candidate combining the web-wrapper session manager, WASM PoW flow, chat-session creation, streaming agent, account selection, and persistent session cache. The decision is to extend it in place. [1]

| Boundary | Decision | Evidence |
|---|---|---|
| DeepSeek runtime | Use the existing `deepcli.session_manager` lifecycle as the owner. | Current baseline decision [1]; PR #174 and PR #216. |
| Provider checklist | Store only provider/account alias, lifecycle state, timestamps, attempt count, and non-secret next-step text. | Session SSOT separates credentials from cross-provider session identity [2]. |
| Provider connection | Present provider-owned manual connection guidance; retain skip/retry/account-creation routing. | User requirement; current `multi-ai-cli` provider surface. |
| PR #6 provider tree | Treat as extract-only evidence, not a merge candidate. | PR #6 and TER-9 / TER-22. |
| Compatibility server | Do not duplicate `llm-api-hub`. | PR #48 and TER-71. |

## Catalog and lifecycle

The catalog begins with `deepseek`, `mistral`, `gemini`, `claude`, and `colab`. Each descriptor identifies its runtime owner, capability class, manual connection guidance, retry policy, and optional account-creation URL. Descriptors contain no secret-bearing fields.

```text
not_started → selected → connecting → connected
                 │             │
                 ├→ skipped ───┴→ selected (retry)
                 └→ needs_account → selected (after account creation)

connecting → failed → selected (retry)
```

The baseline state path is a restrictive local application directory. The hub’s state must never contain a credential, cookie, browser profile, provider session identifier, raw browser traffic, or raw provider response. The existing provider runtime remains the owner of any native session cache.

## Implementation boundary

The implementation is limited to a provider registry, a state store with atomic restrictive writes, a Click command group, unit tests, and inventory/handoff documentation. It deliberately excludes provider-endpoint work, browser automation, live login, capture/export of browser data, and changes to the selected DeepCLI session implementation.

## Integration-base note

The repository decision record states that `master-staging` predates the selected DeepCLI web-wrapper lineage. The feature branch therefore starts from the current `master` baseline and must be reconciled to the governed integration target before promotion. [1]

## References

[1] [Corrected DeepSeek Web-Wrapper Lineage and Integration Decision](../../DEEPSEEK-IMPLEMENTATION-REVIEW-2026-08-14.md)

[2] [Session SSOT Schema](../../schemas/session-ssot.md)

[3] [GitHub PR #6 — extract-only provider stores](https://github.com/timerloggedout-spec/termux-monorepo/pull/6)

[4] [GitHub PR #48 — llm-api-hub compatibility track](https://github.com/timerloggedout-spec/termux-monorepo/pull/48)

[5] [GitHub PR #216 — persistent web-wrapper session state](https://github.com/timerloggedout-spec/termux-monorepo/pull/216)
