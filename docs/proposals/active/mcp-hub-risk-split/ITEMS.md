# Items

| Tool | Current location | Risk | Disposition |
|---|---|---|---|
| `termux_status` | mcp-hub | read-only | **Stays on mcp-hub** |
| `android_status` | mcp-hub | read-only | **Stays on mcp-hub** |
| `android_devices` | mcp-hub | read-only (device inventory) | **Stays on mcp-hub** |
| `termux_run` | mcp-hub | arbitrary command execution on device | **RS-1: move to hub_mcp** |
| `termux_pkg` | mcp-hub | mutates installed packages | **RS-2: move to hub_mcp** |
| `android_adb` | mcp-hub | full adb shell access to device | **RS-3: move to hub_mcp** |

## Subtasks
- [ ] RS-1/RS-2/RS-3: remove `termux_run`, `termux_pkg`, `android_adb` from
  the public `mcp-hub` router (`mcp-hub/api/mcp/[server].ts` +
  `termux-mcp/api/server.ts` / `android-mcp/api/server.ts`), re-expose them
  as `hub_mcp` job-envelope capabilities instead.
- [ ] Update `mcp-hub/catalog.json` `tools` arrays to reflect the reduced,
  read-only-only surface per host.
- [ ] Document the split in `docs/architecture/termux-agentic-hub.md` so
  the next agent doesn't reintroduce a device-mutating tool on the public
  path.
- [ ] Independent review per `docs/CONSENSUS.md` (Tier 3 — cross-cutting
  architecture/security surface).

## Not in scope here
Actually authoring the `hub_mcp` capability implementations for
`termux_run`/`termux_pkg`/`android_adb` — that's real code against a
tested subsystem and belongs in its own PR(s) once this split is agreed,
not bundled into the proposal.
