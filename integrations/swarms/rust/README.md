# Swarms Rust → model hub

This optional worker carries the tested Rust-to-hub path into the monorepo without replacing its orchestrator or granting tools/device authority. It uses `The-Swarm-Corporation/swarms-rs` at `ee1e74cb6e2c94775db88dddb311f2235e3fe9e3` through a revision-pinned Git dependency and checked-in `Cargo.lock`. The Python Swarms SDK is not required. Implements **THUB-013**.

## Start offline

From the repository root:

```sh
python3 scripts/swarms/run-rust.py --task 'Analyze the supplied evidence'
```

This produces one JSON dry-run, without starting Cargo, locating a worker, importing an SDK, writing workflow state, or making network requests. A dry-run is not a completed agent task.

## Build the trusted worker

Use Rust **1.88 or newer**, edition 2024, on a supported build host. On the tested Linux host the upstream dependency graph also required native OpenSSL development tooling and `pkg-config`; Cargo's pinned dependency graph does not eliminate system build prerequisites. Android/Bionic has not been validated.

Keep build artifacts outside the repository:

```sh
export CARGO_TARGET_DIR="$HOME/.cache/termux-swarms-rs/target"
cargo build --locked --manifest-path integrations/swarms/rust/Cargo.toml
export SWARMS_RS_BINARY="$CARGO_TARGET_DIR/debug/termux-swarms-rs-worker"
```

Initial builds fetch the pinned source and locked dependencies. `--locked` prevents silent dependency resolution changes; this is not a vendored/offline build or a reproducible-binary guarantee. The adapter never builds, downloads, or updates a worker automatically. Use an executable that you trust; an arbitrary executable supplied through `--binary` is not sandboxed.

## Execute deliberately

Start/configure the existing hub separately and select one of its configured routes:

```sh
export LLM_API_HUB_BASE='https://your-authorized-hub.example/v1'
# Supply LLM_API_HUB_KEY through your existing secret-management mechanism.
python3 scripts/swarms/run-rust.py \
  --task 'Analyze the supplied evidence, then review the analysis: ...' \
  --model 'your-configured-hub-route' --execute
```

Both `--execute` and a nonblank `--model` are mandatory for inference. There is no paid-model default or provider fallback. The worker explicitly uses `OpenAI::from_url(...).set_model(...)`, not upstream automatic vendor inference. `LLM_API_HUB_BASE` defaults to `http://127.0.0.1:8787/v1`; `LLM_API_HUB_KEY` defaults to `local`, matching the existing hub client's development convention. Configure a real key when the hub requires it. No key is stored here or passed as a command-line argument. HTTPS is required except for loopback HTTP. URL-embedded credentials, query strings, and fragments are rejected. Remote service credentials and deployment remain your existing hub's responsibility.

Options:

- `--number-agents`: 1 or 2, default 2. Two-agent execution uses researcher/reviewer roles and upstream `SequentialWorkflow` handoff.
- `--max-loops`: 1–3 workflow passes, default 1. Agents are reconstructed each pass and receive the previous pass's entire conversation representation. This is an adapter pass loop, not an upstream workflow-loop setting.
- `--max-tokens`: positive per-request output-token limit, default 8192. It is not an aggregate token budget or an assertion of model support.
- `--timeout-seconds`: positive whole-workflow deadline in seconds, default 120. The parent terminates a worker that exceeds that deadline plus five seconds of shutdown grace.
- `--binary`: explicit installed executable, otherwise `SWARMS_RS_BINARY`.

Each agent has one loop and one SDK attempt. The built-in task-completion tool is explicitly disabled; no tools, MCP servers, planning, or agent autosave are configured. These settings do not guarantee a global HTTP-attempt count: the upstream HTTP client or hub/provider can implement retries. A client timeout does not cancel inference already accepted by a remote provider or guarantee zero charge. Do not automatically retry an uncertain production execution.

## Results and private state

Upstream quiet mode still prints diagnostics to stdout. The worker therefore reads its config from stdin and writes a separate `result.json` protocol file. The Python parent forwards **both** child diagnostic streams to stderr and emits exactly one JSON result on stdout. Errors produce JSON with `status: error` and exit code 2; no fallback provider is selected.

`output` preserves upstream behavior rather than pretending it is a plain final answer: direct single-agent output is a conversation-shaped string; sequential output is a structured conversation object with history. `passes` retains every pass's output, and `output` repeats the final pass. Conversation content includes timestamps and may include nested prior conversation text. Callers must not assume that the whole result is an assistant-only answer.

The parent runs the worker in a fresh temporary directory with temporary `HOME` and `TMPDIR`. Sequential-workflow metadata goes under `metadata/pass-N` there, even though agent autosave is off. Result and metadata files are removed on success, reported failure, and ordinary deadline termination. The parent's cwd and environment are not mutated. Abrupt parent termination can leave temporary files; deletion is not secure erasure. The trusted worker is not an OS security sandbox. Diagnostics and complete conversations may contain sensitive task text; do not commit them. Captured output is buffered in memory and this adapter is not a bounded-resource service for hostile inputs or workers.

## Verify without live inference

```sh
cargo test --locked --manifest-path integrations/swarms/rust/Cargo.toml
python3 -m pytest -q tests/test_swarms_rust_adapter.py
SWARMS_RS_TEST_BINARY="$SWARMS_RS_BINARY" \
  python3 -m pytest -q tests/test_swarms_rust_hub.py
```

The optional HTTP tests start the actual local hub on loopback and replace inference with deterministic stubs. They cover one agent, two-stage handoff, repeated passes, bad authorization without inference, timeout cleanup, and CLI JSON separation. They never build a worker automatically or use a real provider. Without `SWARMS_RS_TEST_BINARY`, those tests skip.

The tested environment is Linux x86_64/glibc. A remote Linux worker calling a remote hub is compatible with this interface, but no authenticated task service, public listener, remote deployment, native Android executable, performance gain, or task-quality gain is delivered by this slice. Termux can remain a client; local inference is not required. See the [validation record](../VALIDATION.md).
