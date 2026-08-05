# MCP hosting — GitHub Actions vs Termux vs alternatives

**Agent: Grok** · Device lens: BLU B160V · Related: PR #7 `integrations/termux-mcp/`, `DEVICE_B160V.md`

## Can GitHub Actions host MCP?

### Short answer

**Not as a durable always-on MCP server.** Actions runners are **ephemeral jobs**: they start, run steps, then die. MCP clients (Jules, Devin, Claude, etc.) need a process or URL that answers **while the agent is working** — minutes to hours, often interactively.

| Use of Actions | MCP-relevant? |
|----------------|---------------|
| Run `jules-invoke` / dispatch Jules sessions | ✅ **Yes** — agent is Jules cloud, not your MCP |
| Call GitHub’s **hosted** MCP (`api.githubcopilot.com/mcp/`) | ✅ Client→GitHub; you don’t host |
| Start an MCP HTTP server in a workflow step | ❌ Dies when job ends; max job time still a hard wall |
| “Keep runner alive” hacks | ❌ Against product intent; flaky; burns minutes/credits |

So: **Actions is a great *client* trigger and CI plane**, not a **server plane** for Termux-control MCP or long-lived custom tools.

### What people confuse

1. **GitHub remote MCP** — GitHub hosts it. You point your agent at a URL. You are not “using Actions to host MCP.”
2. **MCP tools *about* Actions** — list workflows, trigger runs. Still not hosting your server on a runner.
3. **Workflow that *is* the work** — prefer this for coding tasks: Jules Action / Jules API session does the work in Jules VMs; phone stays offline-capable.

## Two different MCP problems

| Server | Needs device? | Prefer |
|--------|---------------|--------|
| **A. Jules cloud MCP** (create sessions, approve plans) | No | Host MCP, `npx @google/jules-mcp`, or **stdlib HTTP** (`skyhook/bridge/http_client.py`) — no always-on Termux |
| **B. Termux control MCP** (adb/Termux-API, local FS, on-device cmds) | **Yes** | Must touch the phone somehow — but need not be 24/7 public HTTP |

B160V cannot afford a permanent high-RAM MCP + tunnel for both. Split A off the phone entirely.

## Alternatives to “keep a service alive in Termux”

Ranked for solo B160V + agentic HOME:

### 1. Prefer no long-lived Termux service (best default)

- **Jules sessions / GH Action** for coding (cloud VM).
- **skyhook plan + HTTP client** for Jules API (no MCP daemon).
- **GitHub issues/PRs + Linear** as the control plane agents already use.
- On-device work = **batch scripts** when you open Termux, not a daemon.

### 2. On-demand MCP (phone awake only when needed)

| Pattern | How | Pros | Cons |
|---------|-----|------|------|
| **stdio over SSH** | Agent SSHs in, runs `serve.py` stdio | No public URL; PR #7 already has stdio-ssh template | Needs SSH reachable (Tailscale helps) |
| **cloudflared quick tunnel** | `tunnel.sh` when session starts | Fast public HTTPS | URL changes; phone must stay awake; battery |
| **ngrok / fixed tunnel** | Paid fixed domain | Stable URL | Cost; still needs process + awake device |
| **Tailscale Funnel / serve** | Mesh + optional funnel | Good private path | Setup; device online |

**B160V tip:** wake for a *session*, then kill MCP + tunnel. Do not aim for 24/7.

### 3. Move “always-on” off the phone

| Host | Good for | Notes |
|------|----------|--------|
| **Cloudflare Workers + Agents SDK (`McpAgent`)** | Remote MCP (Streamable HTTP), OAuth | Free tier; **cannot** run Termux/adb tools — only pure API tools |
| **Fly.io / Railway / small VPS** | Always-on custom MCP | Costs $; still no Termux hardware access |
| **Desktop / spare always-on box** | SSH jump + optional tunnel to phone | Classic dual-home |

Workers are excellent for **Jules-protocol proxies** or GitHub-token tools. They are **not** a substitute for Termux-control MCP.

### 4. Pull model (no inbound port on phone)

Phone periodically:

1. Polls Linear/GitHub for “operator tasks”
2. Runs local script
3. Posts results as PR comment / issue

No inbound MCP. Fits flaky cellular and sleep. Implement later as `skyhook` worker cron if needed.

### 5. What PR #7 already sketches

`integrations/termux-mcp/`:

- `serve.py` — transport from env (`stdio` / `sse` / streamable-http)
- `run.sh` — venv + pin
- `tunnel.sh` — cloudflared helper
- Devin custom MCP JSON templates (placeholders)

**Disposition:** sound for **on-demand** device control. Not a mandate to leave it running overnight on B160V.

## Recommended architecture (skyhook)

```
┌──────────── Jules / Grok / agents ────────────┐
│  GitHub MCP (hosted) · Jules API/MCP (host)   │
│  Actions: jules-invoke, CI, gates             │
└───────────────┬───────────────────────────────┘
                │ PRs / issues / Linear
┌───────────────▼───────────────────────────────┐
│  BLU B160V Termux                             │
│  deepcli · skyhook doctor · optional on-demand│
│  Termux MCP only when SSH/tunnel session live │
└───────────────────────────────────────────────┘
```

### Decision table

| Need | Solution |
|------|----------|
| Dispatch coding agents | Jules API / Action / MCP on **host** — not GHA-as-server |
| Read/write GitHub | GitHub hosted MCP or `gh` |
| Touch Termux device | On-demand stdio-SSH or short-lived tunnel |
| Always-on custom tools (no device) | Cloudflare Workers MCP |
| Always-on device tools | **Don’t** on B160V — pull model or wake-on-demand |

## Non-goals

- Burning Actions minutes to `sleep infinity` an MCP port
- Bun/Node MCP stacks as permanent Termux services
- Exposing unauthenticated public MCP to the internet
