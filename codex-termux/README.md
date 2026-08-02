# Codex Termux bridge

This directory is the scaffold for making the `codex-termux_fork` Rust Codex
agent the base of a future native build. It is not yet a full deepcli/Codex
integration.

## Architecture

```text
deepcli session_store
        ⇄ (reconcile / future dispatch integration)
codex_bridge (Python)
        ⇄
codex-termux_fork (Rust codex-cli)
        ⇄
archwiz / synthegration codex_index.json
```

`deepcli` currently writes JSON sessions under
`~/.deepcli/session_store/{account}/{sid}.json`. The bridge conservatively
mirrors those sessions as `{sid, ch}` pointers in
`~/cli-synthegration/codex/codex_index.json`; `ch` is the SHA-256 of the
session file bytes when no content hash is otherwise available. Existing
pointers are preserved by `sid`. `DEEPCLI_STORE`, `SYNTHEGRATION_DIR`, and
`TERMUX_CODEX_BIN` can override the default paths.

## Reconcile & connect locally (Termux)

Run these commands from the repository's `codex-termux/` directory:

```bash
make init          # git submodule update --init --depth 1 (from repo root)
make build
cd bridge
python -m codex_bridge doctor
python -m codex_bridge reconcile
python -m codex_bridge run --help
```

The direct Python commands are equivalent when `codex-termux/bridge` is the
current directory:

```bash
cd codex-termux/bridge
python -m codex_bridge doctor
python -m codex_bridge reconcile
python -m codex_bridge run --help
```

`make build` invokes `(cd codex-termux/codex-termux_fork/codex-rs && cargo
build -p codex-cli)`. The resulting binary is normally under
`codex-rs/target/release/codex` (or `target/debug/codex` when built that way).

## Connect the MCP

The sibling `integrations/termux-mcp/` directory is not present on this
branch. The equivalent integration is available in
[PR #7](https://github.com/timerloggedout-spec/termux-monorepo/pull/7).
After bringing that directory onto the phone, run:

```bash
cd integrations/termux-mcp
python3 -m venv .venv
. .venv/bin/activate
python -m pip install "mcp[cli]>=1.2.0,<2"
TERMUX_MCP_TRANSPORT=sse ./run.sh
```

For the SSH/stdio option, use `TERMUX_MCP_TRANSPORT=stdio ./run.sh` after
starting `sshd` in Termux. For the HTTP/SSE option, run the integration's
`tunnel.sh` and use the printed `/sse` URL. In Devin, add the custom MCP
configuration equivalent to the PR's `devin-custom-mcp.http.json` (or
`devin-custom-mcp.stdio-ssh.json`), replacing the phone host or tunnel URL
and Termux directory placeholders.

## Refactor roadmap

Scaffolded now:

- a prerequisite-checking `codex_bridge doctor`;
- a Cargo build and resolved-binary runner;
- an idempotent, conservative deepcli-session-to-index reconciliation;
- path overrides and Termux runbooks.

The deepcli↔Codex wiring is **scaffolding only**: `run` does not yet translate
deepcli turns into a Codex protocol, and `reconcile` is not a live dispatch
pipeline. The eventual direction is a native Rust/MoonBit/Cangjie layer around
the fork, with explicit session/thread protocols, durable content-addressed
blobs, and archwiz/synthegration synchronization.
