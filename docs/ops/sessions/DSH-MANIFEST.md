# dsh scope-in manifest

Reference: github.com/deepseek-ai/deepseek-harness. Node + pnpm + Cordis.
BLU cannot run it. We port contracts, skip runtime.

## Scope-in matrix

| Subsystem | On BLU? | Verdict |
|---|---|---|
| Cordis framework | no | Skip runtime. Port typed-export + inject. |
| Sandbox local (Landlock/bwrap/koffi) | no | Skip. Replaced by allowlist + `_is_protected`. |
| Sandbox policy (3 modes) | marginal | Port shape. Env `AGENT_SANDBOX_MODE`. |
| MCP client | no | Port contract. `/v1/agent` + Composio already speak it. |
| LLM adapter interface | marginal | Port. `core.py` + `_v1_tools.py` already do. |
| Tool pipeline | marginal | Port stages. `execute()` is subset. |
| Session log suffix upload | marginal | Adopt via `logs_sync` delta. |
| Wire extensions | no | Target is api.deepseek.com; we use web. |
| Web UI :3080 | no | Headless. TUI + Agora are surfaces. |
| read/write file contracts | yes | Already ported. |
| Per-workspace memory | concept | Converged: `session_store` task-hash. |

## Divergence

| Dimension | dsh | ours | why |
|---|---|---|---|
| Runtime | Node 26 + pnpm | Python 3.14 | no pnpm budget |
| Plugin host | Cordis fibers | DISPATCH + TOOLS | 10x simpler |
| Sandbox | kernel | allowlist | not exposed on Termux |
| Model | api.deepseek.com | chat.deepseek.com | zero cost |
| Tool reg | defineTool | TOOLS dict | same shape |
| Memory | RuntimeCore cache | session_store | converged |

## Adopt

1. One process, many workspaces
2. Contiguous suffix session log
3. Tool pipeline as waterfalls
4. Provider-neutral LLM interface

## Skip

Cordis runtime, koffi, node-pty, sandbox binaries, Web UI, wire extensions,
approval UX.

## Consolidation

- `AGENT_SANDBOX_MODE` env → single allowlist switch
- Extract tool defs to `_tools.py` → `register(build_*)` pattern
- Session log: `last_sent_seq` → upload deltas
