# Execution and Session Plane

**Origins:** Android/Termux device, hub_mcp capability boundary, CLI/TUI and agent session callers.

**Flow:** callers supply session identity and structured events → ArchWiz DispatchPipeline → Session SSOT and Codex index. The documented Linear route is a log-only sync hint.

**Consumers:** operator cockpit, session continuation, context retrieval and bounded task context.

**Findings:** caller → ArchWiz → Session SSOT/Codex is documented. Device/remote MCP reachability needs deployment evidence. Separate CLI families do not prove a shared session store. Linear hint does not prove a completed write.

**Sources:** [Termux Agentic Hub](../../architecture/termux-agentic-hub.md) · [Session SSOT](../../schemas/session-ssot.md) · [ICM platform cards](../../icm/objects/platform/CONTEXT.md)
