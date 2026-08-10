# MANIFEST — agent-mailbox

## Overview

This proposal integrates the `mcp-agent-mail` server as an orchestration, communication, and synchronization layer for multi-agent workflows (Gemini, Claude, Devin, Jules, local executors) in the `termux-monorepo` CI/CD environment.

### Architectural Benefits

1. **Persistent/Ephemeral Mailbox Services**:
   - Offers an in-workflow background service executing MCP Agent Mail.
   - Boosts multi-agent coordination without relying on high-latency GHA cache cycles.

2. **File Reservation & Safety Gating**:
   - Solves conflict hazards where multiple agents attempt to modify identical files concurrently on master-staging / termux-smoke branches.
   - Advisory leases are declared on active files via the server's CLI or MCP tool, ensuring other agents yield or await release.

3. **Human Oversight & Auditing**:
   - Commit and push agent mails back to a dedicated branch/repo path, creating human-auditable logs.
   - Run the server-rendered Web UI for real-time visualization of agent threads and decisions.

## Implementation Plan

1. **Action-Level Setup**:
   Create `.github/actions/mcp-agent-mail/action.yml` to curl and execute the binary locally in background server or Robot Mode.

2. **Coordinating Workflows**:
   Wire the action into peer review gates or agent invocation workflows.
