# Source Record — termux-agentic-hub

## Approved direction

The operator approved a Termux-first, free/trial-tier implementation that makes local Android the initial execution environment, uses GitHub for source control, review, CI, and durable coordination, and stores approved forked repositories under `refTemplates/smods/`. DeepSeek compatibility remains required, while all runtime control converges through `hub_mcp/` and one policy envelope.

## Integration decisions

The selected submodules are `termux-mcp-server_fork`, `mcp-android-ssh_fork`, and `term_mcp_deepseek_fork`. The Python Termux MCP server is the canonical device handler. The Rust SSH module and DeepSeek module are retained as adapters/templates and cannot bypass centralized capability checks.

The operator has extended this accepted integration scope to include `timerloggedout-spec/accessibility-agents_fork`, pinned at `a538edc9edfb98cdd8bae96d6b79542874b478f7`. It is a reference source for accessibility skills, specialist dispatch, findings contracts, and scanner guidance. The monorepo keeps its own CLAUDE entry point, proposal governance, workflow policy, and gates.

## Governance and external integrations

Adaptive Dynamic Awareness selects repository work from current priority, risk, dependencies, blockers, freshness, available capabilities, and verifiable impact. Linear remains an optional execution mirror; accepted repository proposal items and GitHub evidence continue to govern when Linear is degraded. Repository Jules automation is retired effective 2026-11-01; replacement agents are selected by verified capability.

## Non-negotiable safety boundaries

This repository work will not commit credentials, tokens, browser/session state, generated secret files, or phone-specific private data. It will not expose device SSH to the public internet. It will not install an unsupported Android self-hosted GitHub runner. Interactive account MFA and 2SV enrollment remain human actions; integrations use documented machine credentials rather than bypassing MFA or capturing second-factor secrets.

## Runtime progression

The first delivery uses a structured, GitHub-backed job/result protocol with local Termux validation and outbound HTTPS. Direct interactive MCP transport remains deferred until a free, authenticated transport route is available and separately reviewed.
