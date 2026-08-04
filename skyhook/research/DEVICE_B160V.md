# Device profile: BLU B160V (Termux ground station)

**Agent: Grok** — all skyhook on-device work targets this class of phone first.

## Hardware (order-of-magnitude)

| Spec | Value |
|------|--------|
| Marketing | BLU View 5 / B160V |
| SoC | MediaTek Helio A22 (MT6761), 4× Cortex-A53 @ ~2.0 GHz |
| RAM | ~3 GB (Geekbench reports ~2.75 GB available) |
| Storage | 64 GB eMMC + microSD expandable |
| GPU | PowerVR GE8300 (weak; not a compute path) |
| Battery | ~4000 mAh |
| OS | Android 13/14 |
| Geekbench 5 | ~160 single / ~550 multi — **entry-level** |

This is a **solo-device ADE ground station**, not a build farm. Cloud (Jules, CI) does heavy coding; Termux does orchestration, gates smoke, MCP serve, session hygiene.

## Operating rules (HARD on-device)

1. **Prefer stdlib Python + bash + existing HOME packages** (`deepcli`, `multi-ai-cli`, `archwiz`, `skyhook`).
2. **Do not require** Bun, Node large trees, Cargo compile, or Python 3.13-only stacks for doctor/smoke.
3. **Scavenge = protocol**, not install: depth-1 clone or README/SOURCE only under `refTemplates` / `skyhook/scavenge`.
4. **No full vendor** of Jules CLI into HOME unless rewritten thin.
5. **Storage:** monorepo already hit multi-GB pain (TER-17). No `node_modules`, no `target/`, no duplicate forks as submodules unless shallow + essential.
6. **RAM:** one agent loop at a time on-device; parallel fleet is Jules cloud, not local Bun workers.
7. **Network:** cellular + intermittent Wi‑Fi; poll with backoff; offline doctor must pass.

## Runtime critique matrix (templates → HOME)

| Template runtime | On B160V? | Verdict |
|------------------|-----------|---------|
| **Bun** (jules-dispatch-cli) | ❌ avoid | Fast on desktops; on 3 GB / A53 installs + JIT compete with Termux + editor. Steal **JSON CLI protocol + session state machine**, rewrite poll loop in **Python urllib** or shell + `jq`. |
| **Node / npm** large CLIs | ❌ avoid | Same class as Bun — disk + RAM. |
| **FastMCP + Python 3.13 + uv** (jules-mcp-server) | ⚠️ conditional | Protocol is gold. Full server better on a **host** or only if Termux already has matching Python. Prefer thin `create_session` HTTP client in skyhook without FastMCP dep. |
| **Rust SDK / cargo build** | ❌ on-device | Compile times and target sizes are hostile. Steal API types/docs; build binaries elsewhere if ever needed. |
| **Crystal (cjules)** | ❌ | Niche toolchain; protocol only. |
| **GitHub Action jules-invoke** | ✅ CI-only | Perfect: runs on GitHub runners, not the phone. Use `starting_branch: master-staging`. |
| **stdlib Python** skyhook bridge | ✅ default | Already the on-device path. |
| **deepcli / multi-ai-cli** | ✅ first-class | Local drivers already tuned for this HOME. |

### Bun specifically

Jules-dispatch is **excellent as a design document**: `--json`, poll states, PR bridge via `gh`. Requiring Bun on B160V would mean:

- Extra runtime install + upgrades on constrained storage
- Competing memory with Termux packages already present (Qt/X11 stacks have appeared in upgrade logs)
- Duplicate responsibility with MCP / official HTTP API

**Rewrite target:** `skyhook/bridge/` + optional `skyhook/bridge/http_client.py` (urllib) implementing create/get/list session. Keep dispatch-cli as **reference**, not dependency.

### MCP specifically

- **Jules cloud MCP** (sessions to Google Jules): host-side or optional on-device if deps already exist.
- **Termux control MCP** (PR #7): on-device by design — keep lean, pin MCP SDK carefully, stdio preferred over heavy tunnels when possible.

## Template policy (explicit)

> Forks under `timerloggedout-spec/*_fork` are **templates**: use **directly** only when the runtime is free on this device or runs off-device; otherwise **rewrite** into skyhook / deepcli / archwiz systems.

| Mode | When |
|------|------|
| Use directly | GH Actions, desktop host, cloud runner |
| Rewrite | Anything that must run in Termux on B160V |
| Metadata only | Ranked SOURCE.txt + research notes |

## Smoke checklist (on-device)

```bash
python3 skyhook/scripts/doctor.py          # offline, no Bun
free -h                                    # watch RAM before installing anything
df -h $PREFIX $HOME                        # refuse large clones if tight
# Never: bun install inside monorepo on-device as a gate dependency
```
