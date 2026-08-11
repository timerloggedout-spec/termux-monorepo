# Agent Monikers (SSOT)

Creative call-signs for high-performance agent orchestration.
Original handles remain **callable** where the underlying app/workflow still listens.

| Role | Primary moniker | Still callable | Notes |
|------|-----------------|----------------|-------|
| Jules (implementation) | **@heyVern** | `@jules` | Use `@heyVern` in continuous-ops & auto-resolve pings |
| Gemini CLI (on-demand) | **@sparkFlux** | `@gemini-cli` | Dispatch accepts both prefixes |
| CodeRabbit (review) | **@codeHound** | `@coderabbitai` | Reviewer identity unchanged |
| Devin (review/fix) | **@devinForge** | Devin app | |
| Continuous-ops sweep | **@opsSweep** | (GHA) | Marker: `<!-- continuous-agent-ops -->` |
| OPERATOR / Grok | **@archW1z** | human OWNER | Signing: `Signed-off-by: Grok (OPERATOR)` |
| Peer orchestrator | **@peerGate** | (GHA) | |

## Rules
1. Prefer moniker in **new** automated pings (less collision with literal bot usernames in chat).
2. Workflows that match `startsWith('@gemini-cli')` **must** also match `@sparkFlux`.
3. Jules GitHub App still reacts to `@jules`; dual-ping `@heyVern` + `@jules` is allowed when reliability > style.
4. Never put secrets or Class 3/4 material in moniker docs.

## High-performance intent
Monikers reduce ambiguous pings and make role ownership obvious under load.
