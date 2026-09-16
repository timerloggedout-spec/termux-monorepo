# Source Record — termux-agentic-hub

## Approved direction

The operator approved a Termux-first, free/trial-tier implementation that makes local Android the initial execution environment, uses GitHub for source control, review, CI, and durable coordination, and stores the approved forked repositories under `refTemplates/smods/`. DeepSeek compatibility remains required, while all runtime control converges through `hub_mcp/` and one policy envelope.

## Integration decisions

The selected submodules are `termux-mcp-server_fork`, `mcp-android-ssh_fork`, and `term_mcp_deepseek_fork`. The Python Termux MCP server is the canonical device handler. The Rust SSH module and DeepSeek module are retained as adapters/templates and cannot bypass centralized capability checks.

## Non-negotiable safety boundaries

This repository work will not commit credentials, tokens, browser/session state, generated secret files, or phone-specific private data. It will not expose device SSH to the public internet. It will not install an unsupported Android self-hosted GitHub runner. Interactive account MFA and 2SV enrollment remain human actions; integrations use documented machine credentials rather than bypassing MFA or capturing second-factor secrets.

## Runtime progression

The first delivery uses a structured, GitHub-backed job/result protocol with local Termux validation and outbound HTTPS. Direct interactive MCP transport remains deferred until a free, authenticated transport route is available and separately reviewed.
