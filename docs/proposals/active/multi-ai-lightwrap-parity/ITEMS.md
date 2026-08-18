# ITEMS — multi-ai-lightwrap-parity

| ID | Priority | Status | Scope | Acceptance evidence |
|---|---|---|---|---|
| MLWP-1 | P1 | completed | Add a parent-owned generic Termux Chromium/Puppeteer `.mjs` runner with `connect`, `probe`, and `send` actions. | The runner reads only non-secret profile declarations; static boundary audit found no browser-state extraction, direct request, screenshot, or raw-payload access. |
| MLWP-2 | P1 | completed | Add static provider profiles for DeepSeek, Mistral, AI Studio, Perplexity, OpenAI web, Liner discovery, and delegated OpenRouter. | Profiles are data-only. AI Studio uses user-owned fork selector fallbacks; Liner accepts a local probe-gated selector profile; OpenRouter remains delegated. |
| MLWP-3 | P1 | completed | Add a Python `ChatBackend` adapter and dispatcher/CLI commands for connect, probe, capabilities, configure, and send. | Browser-wrapper providers route through the generic runner only; direct-endpoint legacy backends are not used for these providers. |
| MLWP-4 | P1 | validation-pending | Add offline contract/unit tests for profile-state gating, normalized output, redaction, and local-profile privacy. | Node contract test and five Python adapter tests pass. Browser fixture/provider-page validation awaits a user-owned Termux profile because this sandbox has neither the repository Puppeteer package nor the Termux Chromium binary. |
| MLWP-5 | P1 | completed | Document the full corpus reconciliation and avoid overlap with DeepTerm or the separate OpenRouter compatibility workstream. | Proposal source records the 44-script corpus, Chapito lineage, seven user-owned AI Studio reference forks, DeepTerm boundary, and delegated OpenRouter disposition. |

## Explicit exclusions

This work does not modify `deepseek-cli/deepterm`, import the ChapitoAI Selenium implementation, automate login/MFA/CAPTCHA/challenges, copy/export browser state, add direct provider endpoint clients, or create a duplicate OpenRouter-compatible server.

## Validation record

- Feature branch corrected to the required `origin/master-staging` base at `c3ac8f6`.
- JavaScript syntax, JSON catalog validation, Node contract test, and five Python adapter tests pass.
- `python3 scripts/ci/termux_smoke.py` passes on the corrected base.
- `python3 scripts/ci/repo_gate.py` fails on 15 pre-existing `master-staging` defects: three invalid Python files and twelve invalid JSON evaluation artifacts outside this proposal’s changed paths. This limitation is recorded for promotion review.
