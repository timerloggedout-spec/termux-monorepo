# Agent Monikers (SSOT)

Creative **display** call-signs for high-performance agent orchestration.

**Critical:** Do **not** `@`-mention monikers that collide with real GitHub usernames.
Use backticks or plain text for display. Live triggers remain the original handles
(plus approved aliases registered in the matching workflow).

| Role | Display moniker | Live trigger (callable) | Notes |
|------|-----------------|-------------------------|-------|
| Jules (implementation) | `heyVern` | `@jules` | App only reacts to `@jules` |
| Gemini CLI (on-demand) | `sparkFlux` | `@gemini-cli` | Dispatch also accepts case-insensitive `@sparkFlux` as alias |
| DeepSeek CI (review/invoke) | `deepCore` | `@deepseek` / `@deepseek-ci` | Workflow also accepts case-insensitive `@deepCore`; labels `deepseek-ci`, `deepseek`, `deepCore` |
| CodeRabbit (review) | `codeHound` | `@coderabbitai` | Reviewer identity unchanged |
| Devin (review/fix) | `devinForge` | Devin app | |
| Continuous-ops sweep | `opsSweep` | (GHA) | Marker: `<!-- continuous-agent-ops -->` |
| OPERATOR / Grok | `archW1z` | human OWNER | Signing: `Signed-off-by: Grok (OPERATOR)` |
| Leet-Seek Admin / Full-scope Operator | `l337S33k` | (human / future profile role) | **Full admin across all repositories.** Parity with (and intended ≥) current OPERATOR/`archW1z`. Full-scope PAT + org/repo admin. Profile roles will be created under this moniker. Display only — do **not** `@`-mention. |
| Peer orchestrator | `peerGate` | (GHA) | |

## Rules

1. Automated comments: **display** moniker in backticks; **ping** only the live trigger (`@jules`, `@gemini-cli`, `@deepseek` / `@deepseek-ci`).
2. Workflows matching a live trigger **must** also accept the display moniker case-insensitively where registered above.
3. Never put secrets or Class 3/4 material in moniker docs.
4. If a moniker string is later registered as a GH username we do not control, keep it non-@ only.

## High-performance intent

Monikers reduce ambiguous role ownership under load without notifying strangers.
