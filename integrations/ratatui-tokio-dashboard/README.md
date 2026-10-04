# Ratatui + Tokio Terminal Dashboard

Termux-first responsive terminal dashboard for live system/process and async-stream telemetry.

## Why this exists

This is the first implementation slice of the requested Ratatui/Tokio dashboard concept:

- Tokio async producers feed bounded event channels.
- A pure dashboard model owns state transitions.
- Ratatui renders only after the model becomes dirty.
- Ratatui itself diffs frame buffers so unchanged terminal cells are not rewritten.
- /proc metrics are read without a privileged service.
- Unavailable metric sources degrade to safe empty/zero values instead of crashing the UI.

The visual layout covers the reference concepts: active streams, latency, throughput, CPU, memory, processes, and runtime/thread-pool state.

## Run on Termux

~~~sh
cd integrations/ratatui-tokio-dashboard
cargo run --release
~~~

Controls:

- q / Esc — quit
- Up / k — previous stream
- Down / j — next stream
- r — mark a refresh

Ratatui initialization enables raw mode and the alternate screen, and the application has an additional Drop guard for restoration.

## Architecture

~~~text
             Tokio async producers
              /        |        \
             /         |         \
       /proc sampler  stream sim  input reader
             \         |         /
              \        |        /
               bounded mpsc channel
                       |
                       v
                DashboardState
                 /           \
          dirty=false       dirty=true
               |               |
             wait          Ratatui draw
                               |
                         terminal diff
~~~

The stream producer is intentionally a deterministic in-process source for the first slice. A later adapter can replace it with a real event source without changing the dashboard model or renderer.

## Termux notes

This implementation treats /proc as an optional observation surface. Android/Termux kernels and permission policies can expose different process details. The dashboard therefore does not require every /proc file to exist.

Process RSS is parsed from `/proc/<pid>/status` via `VmRSS` in KiB. This avoids assuming a fixed kernel page size and is more portable across Linux/Android variants.

## Collaborating

See [`COLLABORATING.md`](COLLABORATING.md) for the maintainer hand-off, architecture invariants, extension points, portability guidance, Codespaces/CI workflow, and troubleshooting notes.

## Validation

~~~sh
cargo fmt --check
cargo check
cargo test
~~~

The crate is deliberately standalone: it does not add itself to the monorepo's existing Rust crates and does not expand the always-on repo gate.

## Provenance

Implements: TUI-RATATUI-001 through TUI-RATATUI-006.

Source concept: user-provided Ratatui/Tokio terminal-dashboard references, registered as issue #934.
