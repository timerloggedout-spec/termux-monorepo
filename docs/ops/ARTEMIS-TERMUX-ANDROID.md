# ARTEMIS on Termux Android nodes

⌖ scope: NL ⇒ Android UI automation (google/artemis fork) for `tmx-node-primary` ∧ `tmx-node-55619bd5`.
Pin: `refTemplates/smods/artemis_fork` @ `b8f6ef7` (branch `termux-adapter`). Inventory: `docs/submodules/fork-inventory.yaml`.
Identity rule: opaque ids only (#1477, `DEVICE-IDENTITY.md`); IPs, tailnet names, serials ∧ keys come from env ∨ secrets.

## Split

| layer | runs on | why |
|---|---|---|
| ARTEMIS agent ∧ MCP server ∧ web console | host: Hark VM ∨ Codespace ∨ Cloud Shell ∨ workstation | `opencv-python`, `scipy`, `langgraph` ⇒ Linux wheels |
| ADB endpoint | Termux node | `adb tcpip 5555` ∨ wireless debugging |
| Readiness probe | host ∨ node | `termux/doctor.sh` ⇒ one JSON line |

## Transports (fork `termux/connect.sh`, first answer wins)

| id | path | maps to DEVICE-ACCESS-DIRECTORY row | device typing |
|---|---|---|---|
| T1 | tailnet direct `adb connect <tailnet-host>:5555` | Tailscale (GitHub ∨ Google tailnet) | none, after `adb tcpip 5555` via BugJaeger |
| T2 | SSH `-p 8022 -L 15555:127.0.0.1:5555` ⇒ `adb connect 127.0.0.1:15555` | Pinggy TCP ∨ Tailscale ∧ `TERMUX_MCP_SSH_PRIVATE_KEY` | none |
| T3 | on-node `adb connect 127.0.0.1:<wireless-debug-port>` | ADB (wireless debugging) | pair code once ⇒ secondary node only |

Origin node (damaged screen) ⇒ T1 ∨ T2. `adb tcpip 5555` resets on reboot ⇒ re-arm from the secondary node via BugJaeger.

## Run

```bash
git submodule update --init refTemplates/smods/artemis_fork
cd refTemplates/smods/artemis_fork
cp termux/env.termux.example .env.termux && $EDITOR .env.termux   # values from secrets
set -a; . ./.env.termux; set +a
eval "$(termux/connect.sh)" && export ADB_DEVICE_SERIAL
termux/doctor.sh
uv sync && uv run artemis run "Open Settings, read battery level" --profile flash
```

`connect.sh` exit: 0 connected · 2 ∄ transport answered · 3 adb missing · 4 unauthorized.

## Guardrails

- DO route device actions through the same gate as `mcp-android-ssh_fork`: one control endpoint per node at a time (ARTEMIS `device_lock`).
- DEFAULT `ARTEMIS_HELPER_AUTO_INSTALL=false` on Termux nodes; install the accessibility helper APK deliberately.
- LLM keys: `GEMINI_API_KEY` ∨ `OPENAI_API_KEY` ∨ `OPEN_ROUTER_API_KEY` from Actions secrets ∨ vault; ¬ commit.
- Traces ∧ screenshots stay on the host; publish only redacted summaries.

## Status

⊢ fork adapter committed (`b8f6ef7`); `connect.sh` paths T1 ✓ ∧ ∄-transport rc2 ✓ ∧ adb-missing rc3 ✓ under a stub adb.
⊬ live device run: needs `adb tcpip 5555` armed on a node ∧ a reachable transport.
