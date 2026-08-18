# ITEMS — multi-ai-webwrapper-hub

| ID | Priority | Status | Scope | Evidence / Acceptance |
|---|---|---|---|---|
| MAWH-1 | P1 | ready for review | Add a data-driven provider catalog and a non-secret, resumable provider connection checklist in `multi-ai-cli`. | The catalog covers the current `deepseek`, `mistral`, `gemini`, `claude`, and `colab` entries. The persisted state stores no credential, cookie, browser profile, provider-session identifier, or raw response. Focused tests pass. |
| MAWH-2 | P1 | ready for review | Add offline CLI commands for provider list, select, next, begin, complete, skip, retry, and status. | A user can select a subset, leave providers skipped, return to them, and see an account-creation/manual-connection next action without a network request. CLI smoke passes without provider networking. |
| MAWH-3 | P1 | ready for review | Preserve the DeepCLI browser-session web-wrapper as the DeepSeek runtime owner and document the integration seam. | No change is made to DeepCLI request construction, browser-session cache, WAF/session state, provider endpoints, PoW logic, or credential material. The proposal and README document the ownership boundary. |
| MAWH-4 | P1 | ready for review | Provide tests, an all-state GitHub/Linear inventory, and a handoff document. | Unit tests, Python compilation, proposal-registry validation, repository gate, CLI lifecycle smoke, and `git diff --check` pass. The documented Termux smoke script is absent from the selected baseline and remains an explicit promotion limitation. |

## Out of scope

This item does not merge PR #6 wholesale, implement or modify a compatibility server owned by `llm-api-hub`, automate provider logins, export browser state, alter DeepCLI web-wrapper request construction, or commit any secret-bearing artifact.
