# MCP Monorepo Integration & Multi-Agent Access Protocols

This guide documents the integration of `termux-mcp-server` and `phone-mcp-server` within the `termux-monorepo`, and establishes the **Multi-Agent Access Protocols** that allow multiple autonomous agents to share and control a single Android device simultaneously and securely.

---

## 🏗️ Architectural Overview

By combining these two powerful tools under a unified monorepo framework, we expose a highly robust operational surface to our autonomous agents:

```
                  ┌──────────────────────┐   ┌──────────────────────┐
                  │   Agent Alpha (PC)   │   │   Agent Beta (PC)    │
                  └──────────┬───────────┘   └──────────┬───────────┘
                             │   HTTP/SSE               │   HTTP/SSE
                             └───────────────┬──────────┘
                                             ▼
                              ┌─────────────────────────────┐
                              │    phone-mcp-server (Node)  │ (HTTP/SSE Server - Port 3000)
                              └──────────────┬──────────────┘
                                             │ Local API Call
                                             ▼
                             ┌──────────────────────────────┐
                             │    termux-mcp-server (Py)    │ (Python FastMCP stdio / ADB)
                             └──────────────┬──────────────┘
                                             │
                                   execFile("termux-*")
                                             │
                                             ▼
                              ┌─────────────────────────────┐
                              │      Termux:API (Android)   │
                              └─────────────────────────────┘
```

1. **`phone-mcp-server` (Node.js)**: Runs an Express server exposing **18 key phone tools** via Streamable HTTP/SSE transport (such as SMS list, sending text messages, contacts, location, camera photos, clipboard, call log, volume control).
2. **`termux-mcp-server` (Python)**: Uses FastMCP to expose **45+ advanced UI automation and system control tools** (such as screenshots, UI hierarchy dumping, screen tapping/swiping, text input, flashlight toggling, sensors, file browser, and command execution).

---

## 🚀 Installation & Setup

### 1. On-Device Setup (Android via Termux)

For native execution directly on the target device:

1. **Install Prerequisites**:
   Ensure both **Termux** and the **Termux:API** apps are installed from the **same source** (F-Droid is highly recommended to prevent signature mismatches).
   ```bash
   pkg update && pkg upgrade
   pkg install nodejs-lts python termux-api openssh android-tools
   ```

2. **Initialize Permissions**:
   Before launching, manually grant permission prompts by running each of the following:
   ```bash
   termux-setup-storage
   termux-sms-list
   termux-contact-list
   termux-location
   termux-camera-photo
   termux-call-log
   ```

3. **Install dependencies in Monorepo**:
   - **For Python FastMCP**:
     ```bash
     cd termux-mcp-server
     python3 -m venv .venv
     source .venv/bin/activate
     pip install -e .
     ```
   - **For Node HTTP/SSE**:
     ```bash
     cd phone-mcp-server
     pnpm install
     ```

4. **Launch SSH daemon for remote execution**:
   ```bash
   sshd -p 8022
   whoami && passwd && ifconfig
   ```

---

### 2. Docker Setup (Render / CI Environment)

For automated testing or headless environments, we provide a complete mock Docker environment. This bypasses the need for a physical Android device by stubbing the `termux-api` commands.

- **Start with Docker Compose**:
  ```bash
  docker-compose up --build
  ```

- **Stubbing mechanism (`termux-stub.py`)**:
  Both containers map `termux-*` commands to a Python script that returns realistic mock JSON data. This enables test suites to pass 100% cleanly without requiring any device permissions.

- **Render Automated Deployment**:
  To deploy the automated test environment on Render, link the repository and use the `Dockerfile` in `phone-mcp-server/Dockerfile` or configure the service as a Web Service.

---

## 🤝 Multi-Agent Access Protocols

When multiple autonomous agents (e.g., Devin, Jules, local runners) concurrently access a single Android device, race conditions and screen conflicts can occur. The following protocols guarantee collision-free operation.

### 1. Device Access Multiplexing (HTTP/SSE)
Unlike stdio-based transport which binds a server to a single client process, the **Streamable HTTP/SSE transport** of `phone-mcp-server` supports **unlimited concurrent connections**.
- All agents on the local network connect to: `http://<phone-ip>:3000/mcp`
- The server acts as a stateless multiplexer, dispatching requests sequentially to the underlying system.

### 2. Concurrency Control & Screen-Lock Gating
Because UI operations (e.g., `tap_screen`, `swipe_screen`, `input_text`) change the state of the active screen, interleaving taps from different agents will lead to catastrophic state corruption (e.g., clicking on wrong buttons).

We enforce an **Acquire-Act-Release Screen Lock Protocol**:

```
Agent A                      Device Screen Lock                    Agent B
   │                                 │                                │
   │ 1. Acquire Lock                 │                                │
   ├────────────────────────────────>│ (Locked by A)                  │
   │                                 │                                │
   │ 2. Perform UI Actions           │                                │
   │    (Screenshot -> Tap)          │                                │
   ├────────────────────────────────>│                                │
   │                                 │ 3. Attempt Acquire Lock        │
   │                                 │<───────────────────────────────┤
   │                                 │    (Refused: Busy)             │
   │ 4. Release Lock                 │                                │
   ├────────────────────────────────>│ (Unlocked)                     │
   │                                 │                                │
   │                                 │ 5. Acquire Lock                │
   │                                 │<───────────────────────────────┤
   │                                 │ (Locked by B)                  │
```

#### The Protocol Rules:
1. **Mandatory UI Gating**: Before executing any UI action (`tap_screen`, `swipe_screen`, `input_text`, `dump_ui`, `open_app`), an agent **MUST** call `set_clipboard` (or a dedicated lock utility if implemented) to write a lock token: `LOCK:<agent_id>:<expiry_timestamp>`.
2. **Lock Verification**:
   - Read the lock token using `get_clipboard`.
   - If the clipboard starts with `LOCK:` and has not expired, and does not belong to the requesting agent, the agent must back off for `1.5` seconds and retry.
   - If the lock is empty, expired, or belongs to the requesting agent, the agent overwrites it with their lock token and proceeds.
3. **Lock Release**: Once the sequence of steps is completed (e.g., sending a text or clicking a button), the agent must clear the lock by setting the clipboard to empty or `UNLOCKED`.

### 3. Session Tracking & Shared Telemetry
To prevent conflicting actions and audit all agent operations:
- All agents write their execution traces to the shared `agent_telemetry_stream.json` telemetry stream.
- Actions are indexed and searchable using the virtual `messages_fts` SQLite table in `local_repo.db` via:
  ```bash
  # Search all SMS sent across all agent sessions
  ./fts_search.sh "SMS"
  ```
- This guarantees fully traceable, multi-agent accountability across shared mobile devices.
