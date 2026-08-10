# DEBATE — Permissioned Access Levels & CAVEMAN Skill Spec

This document records the Socratic debate and security-performance trade-off evaluation regarding **Permissioned Access Levels for Hierarchical Management** in a Completely Automated Agentic Development Environment (CAADE) and the **CAVEMAN Skill Specification**.

---

## 🎭 The Socratic Interlocutors

- **Sentinel (Security-First Analyst)**: Prioritizes containment, local privilege restrictions, strict credential isolation, and preventing traversal hijacking.
- **Bolt (Performance and I/O Architect)**: Focuses on throughput, latency, incremental file updates, and low execution overhead.
- **Jules / Grok (Ecosystem Orchestrator)**: Integrates communication channels (MCP Agent Mail) and balances safety constraints with autonomous productivity.

---

## 🏛️ Socratic Debate & Consensus Analysis

### Q1: Why are local privilege restriction routines (0o700 / 0o600) strictly necessary on config directories and session databases?

*   **Sentinel**: In multi-user platforms and containerized sandboxes, sensitive tokens (e.g., `JULES_API_KEY`, DeepSeek proxy credentials, SQLite databases) are vulnerable to side-channel and local data harvesting. Restricting configuration directories to `0o700` and config/session files to `0o600` ensures that other local processes cannot read active credentials.
*   **Bolt**: While necessary, calling `chmod` recursively on every filesystem walk introduces massive I/O overhead. We must perform these checks once at startup or only on targeted active session operations.
*   **Consensus**: Standard local privilege permissions (`0o700` directories, `0o600` files) are enforced globally across `deepcli` and `termux-multi-agent`. Recursive checks must optimize performance by avoiding repetitive walks on cold data paths.

### Q2: How do recursive permission walkers protect against directory traversal hijacking without breaking symlinks?

*   **Sentinel**: Traversal hijacking vulnerabilities occur when malicious or untrusted packages create symbolic links pointing to root files (e.g., `/etc/shadow` or `~/.ssh/id_rsa`). When a recursive walker follows these symlinks, it inadvertently alters permissions or exposes contents. Walking algorithms must explicitly skip symlinks (`path.is_symlink()`).
*   **Bolt**: Skipping symlinks also saves redundant stat calls and avoids circular link loops, improving indexing speed.
*   **Consensus**: All local permission walkers strictly skip directories and files matching `path.is_symlink()`.

### Q3: What is the "CAVEMAN" skill specification, and why does it enforce standard-library-only execution on limited environments?

*   **Jules / Grok**: On constrained target hardware like mobile Android phones running Termux (e.g., BLU B160V), heavy runtimes (Node, Bun, Rust toolchains) consume extreme memory, causing thermal throttling or Out-Of-Memory (OOM) app crashes. The CAVEMAN spec defines:
    1.  **Lightweight Core**: Standard-library-only execution profiles (e.g., Python standard library, thin bash wrappers) for local, on-device operations.
    2.  **Cloud Offload**: Delegating compute-heavy or dependency-dense tasks (like full static analysis, compilation, or web-wrapping) to cloud-side workers.
*   **Sentinel**: This also decreases the local attack surface. Fewer dependency runtimes mean fewer supply-chain attack vectors on-device.
*   **Consensus**: Termux-level orchestration relies on standard libraries and sparse metadata, while Node and Rust execution is offloaded to remote execution layers (e.g. Render / GitHub Actions).

### Q4: How does MCP Agent Mail bridge local permissions and agent-to-agent coordination?

*   **Jules / Grok**: Using the Rust-based `mcp-agent-mail` server, agents declare advisory leases (reservations) on files in the workspace (e.g., `docs/mcp-multi-agent-access.md`) before editing. If another agent sees an active lease, it yields, preventing file state corruption.
*   **Sentinel**: All inbox database tables, state folders, and leases created by MCP Agent Mail must adhere to Sentinel's `0o700`/`0o600` permission rules.
*   **Consensus**: Composite action setups start the server within GHA job virtual networks securely, maintaining git-backed archives for full trace audibility.

---

## 🏺 Formalized CAVEMAN Skill Spec Contract

1.  **Dependency Profile**: Restrict local runtime dependencies to Python `stdlib` + shell command pipelines.
2.  **Symlink Guard**: Walking routines must invoke `not path.is_symlink()` prior to permission updates.
3.  **Permission Profile**:
    *   Configuration directories: `0o700` (read/write/execute for owner only).
    *   Credentials, SQLite, and Telemetry: `0o600` (read/write for owner only).
4.  **Advisory Leases**: All workspace file updates require registering an advisory lease via `mcp-agent-mail` to coordinate multi-agent branches.
