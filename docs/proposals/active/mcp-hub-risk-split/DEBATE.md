# Debate

## Operator decision (2026-09-10)
Presented four options for the mcp-hub / hub_mcp conflict: keep mcp-hub
only, switch to hub_mcp only, split by risk, or deep-dive first. Operator
selected **split by risk**, with the split criterion: mcp-hub for
non-device/stateless (status/read-only), hub_mcp for anything touching the
phone (run commands, adb, files).

This proposal draws that line per-tool (see ITEMS.md) rather than leaving
it abstract. No agent has yet implemented the `hub_mcp`-side capabilities
for the three tools being removed from the public surface — that is
flagged as explicitly out of scope for this proposal and left as an open
subtask so it gets its own reviewed PR.
