# Collaborating on the Ratatui + Tokio Terminal Dashboard

This guide is the maintainer and collaborator hand-off for
`integrations/ratatui-tokio-dashboard/`.

It is intentionally scoped to this integration. Repository-wide governance,
proposal registration, security rules, and merge policy remain authoritative in
`CLAUDE.md`, `CONTRIBUTING.md`, and `docs/proposals/PROCESS.md`.

## 1. What this integration is

The dashboard is a standalone Rust integration for Termux-oriented live
system/process and asynchronous-stream telemetry.

The implementation separates:

1. **Producers** — Tokio tasks for metrics, demo streams, and terminal input.
2. **Transport** — bounded Tokio channels that prevent unbounded event growth.
3. **Model** — `DashboardState` in `src/lib.rs`, which owns state transitions
   and history.
4. **Renderer** — Ratatui UI code in `src/main.rs`.
5. **Metric adapters** — platform observation code in `src/metrics.rs`.

The intended extension seam is the producer/adapter boundary: a real event
source can replace the deterministic stream simulator without requiring a
rewrite of the dashboard model or renderer.

## 2. Repository navigation

| Path | Purpose |
|---|---|
| `Cargo.toml` | Standalone crate metadata and dependency contract |
| `src/lib.rs` | State model, event reducer, bounded histories, unit tests |
| `src/main.rs` | Tokio runtime, terminal lifecycle, input, producers, rendering |
| `src/metrics.rs` | `/proc`-backed system/process observations and parsing tests |
| `README.md` | User-facing run/architecture/compatibility documentation |
| `COLLABORATING.md` | This contributor/maintainer hand-off |
| `.github/workflows/ratatui-tokio-dashboard.yml` | Path-scoped Rust validation lane |

The proposal source of truth is:

- `docs/proposals/active/ratatui-tokio-terminal-dashboard/`
- `docs/proposals/registry.yaml`

The originating issue is #934 and the implementation history is represented by
PRs #935, #938, and #940.

## 3. Normal development loop

For a repository change:

1. Read `CLAUDE.md` and `CONTRIBUTING.md`.
2. Check `docs/proposals/registry.yaml` and the active Ratatui proposal.
3. Work from the repository's current integration base using an isolated
   feature branch/worktree. For this already-promoted integration, base
   documentation-only maintenance on the current `master` implementation;
   follow repository promotion rules if the change is destined for staging.
4. Keep the integration standalone; do not add it to the monorepo's
   always-on Rust workspace unless the proposal explicitly changes scope.
5. Make the smallest coherent change.
6. Run formatting and the focused Rust tests where a Rust toolchain is
   available.
7. Run the repository gates required by the proposal.
8. Open a PR with the relevant proposal item IDs.
9. Treat GitHub Actions as execution evidence when local Cargo/Rust is not
   available.
10. Wait for checks to finish; do not treat queued/in-progress states as
    validation.
11. Re-fetch the final SHA and check results before promotion.

## 4. Development environments

### Termux

The target runtime is Termux. Launch with:

```sh
cd integrations/ratatui-tokio-dashboard
cargo run --release
```

The application restores the terminal on exit. `q`/Escape quits,
Up/`k` and Down/`j` navigate streams, and `r` requests a refresh.

### GitHub Codespaces

The repository provides a Rust-enabled `.devcontainer`. Use it as the
interactive cloud development/reproduction environment when a local
Termux/Rust toolchain is unavailable.

Codespaces is an interactive development surface; GitHub Actions remains the
repeatable CI execution surface. Do not add a provider-specific cloud
dependency merely to develop this integration.

### GitHub Actions

`.github/workflows/ratatui-tokio-dashboard.yml` is the authoritative
path-scoped Rust validation lane. It performs formatting, lockfile generation,
`cargo check`, and tests.

The workflow intentionally captures the generated `Cargo.lock` as an
artifact rather than committing a lockfile to this standalone integration.
That artifact is useful evidence of the dependency resolution used by the
validation run.

The Rust toolchain action is pinned to an immutable commit in the workflow.
Keep that pin stable and update it deliberately when the repository chooses a
new toolchain baseline.

## 5. Model invariants

### Bounded histories

CPU and throughput histories are capped by `HISTORY_LEN`. New samples evict
the oldest sample once the bound is reached.

### Throughput batch accounting

There are `STREAM_COUNT` logical streams. A throughput history sample is
recorded once per complete stream batch.

The model uses a bitmask rather than assuming that a particular stream ID
arrives last. Therefore event arrival order is not part of the correctness
contract.

If the stream count changes, update the mask representation and its tests
together. Do not silently introduce a shift that exceeds the chosen mask type.

### Dirty-state rendering

The model marks the dashboard dirty only when an event changes observable
state (or explicitly requests a refresh/resize). The renderer consumes that
signal so unchanged state does not cause unnecessary full redraw work.

### Quit propagation

A quit input is terminal control state. If a quit event is already queued while
the main loop drains a batch, the loop must still terminate rather than merely
discarding the event.

### Graceful metric absence

`/proc` is an optional observation surface. Missing or unreadable files must
degrade to safe fallback values rather than crash the dashboard.

Process RSS is parsed from `/proc/<pid>/status` `VmRSS` in KiB. Do not
reintroduce assumptions about a fixed kernel page size.

## 6. Adding a real event source

Prefer this sequence:

```text
real source
   |
adapter / producer task
   |
bounded mpsc channel
   |
AppEvent
   |
DashboardState::apply
   |
Ratatui renderer
```

Keep provider-specific parsing and I/O outside `DashboardState`. The model
should receive normalized events and remain deterministic enough for unit
tests.

For a new event type:

1. Define the smallest normalized payload needed by the UI.
2. Add the event variant.
3. Update `DashboardState::apply`.
4. Add focused regression tests for ordering, bounds, and fallback behavior.
5. Keep the renderer dependent on model state rather than provider APIs.

## 7. Metrics portability

Do not assume that every Linux `/proc` file exists on every Android/Termux
device.

When adding a metric:

- isolate file parsing in a small function;
- test the parser with representative text fixtures;
- return a safe fallback when the source is unavailable;
- document platform assumptions;
- avoid privileged services;
- avoid exposing credentials, environment secrets, or user data in telemetry.

If a metric requires a platform-specific implementation, prefer an adapter or
capability check over spreading conditional filesystem logic through the UI.

## 8. Validation checklist

Before requesting review:

```sh
cargo fmt --check
cargo check
cargo test
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```

The exact commands can be delegated to the scoped GitHub Actions lane when
Cargo/Rust is unavailable locally.

For every change, also inspect:

```sh
git diff --check
git status --short
```

A successful workflow admission is not evidence of a successful test run.
Record actual completed job/check results.

## 9. Common failure modes

| Symptom | Likely cause | Correct response |
|---|---|---|
| Throughput history has too many points | Sampling per stream update | Restore complete-batch accounting and test shuffled arrival |
| RSS is unexpectedly wrong on Android | Fixed page-size assumption | Parse `VmRSS` from `/proc/<pid>/status` |
| App stays open after queued quit | Quit consumed while draining events | Propagate terminal quit state through the drain loop |
| Local Rust commands unavailable | Termux/Codespaces/toolchain not present | Use Codespaces or the scoped GitHub Actions lane |
| Workflow is queued | Execution has not completed | Wait, then inspect actual result |
| `/proc` field missing | Kernel/permission/platform variation | Use graceful fallback; do not crash |
| Renderer changes require provider changes | Coupled architecture | Normalize through `AppEvent` and the model layer |

## 10. Security and scope

This integration must remain free of:

- API keys or access tokens;
- browser/session stores;
- device-specific tunnel endpoints;
- private host keys;
- credentials in logs or artifacts;
- privileged runtime requirements.

Do not use this dashboard as a new orchestration control plane without a
separate proposal. It is an observation/UI integration, not a replacement for
the repository's ArchWiz cockpit or governance machinery.

## 11. Change ownership and hand-off

A collaborator taking over this integration should be able to reconstruct the
state from the repository without relying on chat history:

1. `CLAUDE.md` — repository governance and hard rules.
2. `CONTRIBUTING.md` — contributor and merge workflow.
3. `docs/proposals/registry.yaml` — proposal registration.
4. `docs/proposals/active/ratatui-tokio-terminal-dashboard/` — itemized scope
   and acceptance evidence.
5. `README.md` — user-facing operation.
6. This file — implementation invariants and maintenance guidance.
7. GitHub Actions — current execution evidence.

When the proposal becomes terminal, update its item state/evidence, record the
review outcome, and move it from `docs/proposals/active/` to
`docs/proposals/closed/` according to `docs/proposals/PROCESS.md`.

## 12. History and provenance

The dashboard originated as issue #934 and was implemented in PR #935.
Hardening followed in PR #938 and final stream-order-independent batching in
PR #940.

The final merged dashboard hardening commit was:

`c1698084bf59e19e56fce5989e2cf6c2a551bdb9`

The implementation was validated by the repository's GitHub Actions lanes;
no Fly/Sprites environment is required for the integration.
