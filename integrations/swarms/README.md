# Optional Swarms sequential adapter

This integration adds an explicit sequential analysis/review workflow without replacing the monorepo's orchestrator, provider hub, or device policy. Implements **THUB-011**, **THUB-012**, and **THUB-013**, with corrected research provenance under **THUB-014**. The [research](../../docs/research/SWARMS-ECOSYSTEM.md) distinguishes Kye Gomez's 455-repository public listing from the historical 676-repository `timerloggedout-spec` inventory; neither is an all-code audit. The [architecture synthesis](../../docs/architecture/SWARMS-SYNTHESIS.md) explains local boundaries. Rust and remote services are valid alternatives; see the [pinned Swarms Rust assessment](../../docs/research/SWARMS-RUST.md).

**Rust path implemented under THUB-015:** the [optional pinned Rust worker](rust/README.md) has its own offline-first CLI, `python3 scripts/swarms/run-rust.py --task 'Analyze supplied evidence'`. It does not require the Python Swarms SDK. Its single-agent, handoff, auth-error, deadline, and cleanup behavior is tested against the actual local hub with stub inference. The Python-specific instructions below remain unchanged; neither backend establishes native Android support or a deployed remote task service.

## Try it offline

From the monorepo root:

```sh
python3 scripts/swarms/run.py --task 'Summarize the supplied evidence'
```

This prints a JSON dry-run. It does not import Swarms, create workspace files, install packages, or call the model hub. A dry-run is a plan, not generated research or a completed agent task.

## Install the optional SDK

The SDK requires Python 3.10 or newer. The core monorepo remains usable without it. Initialize only the selected source reference, then install in a dedicated environment outside the repository:

```sh
git submodule update --init --depth 1 -- refTemplates/smods/swarms
python3 -m venv "$HOME/.venvs/termux-swarms"
"$HOME/.venvs/termux-swarms/bin/python" -m pip install -r integrations/swarms/requirements.txt
```

The gitlink pins upstream source revision `8ec7948ce6e8ab28c4454d6c2c3187a735672067`, manifest version `16.0.2`, Apache-2.0. [`source-lock.json`](source-lock.json) records source-file hashes. It is **not** a transitive dependency lock. Most upstream dependencies are unconstrained, and successful installation on glibc Linux does not establish native Android/Termux support. The initial inspection found no separate pre-existing Swarms checkout to relocate; the shallow monorepo checkout itself was preserved.

## Execute deliberately

Start/configure the existing model hub separately, then choose a model route that it supports:

```sh
"$HOME/.venvs/termux-swarms/bin/python" scripts/swarms/run.py \
  --task 'Analyze this supplied evidence, then review the analysis: ...' \
  --model 'your-configured-hub-route' --execute
```

Both `--execute` and a nonblank model are required. There is no paid-model default. The custom `llm.run()` implementation delegates to `llm_api_hub.clients.openai_compat`, not Swarms' built-in provider route. The hub client reads `LLM_API_HUB_BASE` and `LLM_API_HUB_KEY` as documented in that existing component. No key is stored in this integration. This slice does not prove a particular provider is available, free, or authorized.

The workflow has researcher/reviewer roles (`--number-agents` selects 1 or 2). `--max-loops` selects 1–3 workflow passes; each Agent has one loop and one SDK attempt. These are conservative initial safety limits, not measured optimal settings. They do not promise a global HTTP or token budget: the hub/provider may implement additional retries or route-level behavior. No tools, shell commands, MCP servers, automatic Git changes, or filesystem inspection are supplied to agents.

## State and diagnostics

Upstream telemetry is on by default when `SWARMS_TELEMETRY_ON` is absent. Execution sets `SWARMS_TELEMETRY_ON=false` before the lazy import and creates a temporary workspace outside the repository before SDK initialization. Both agent and workflow autosave are disabled. Upstream still writes internal memory, so workspace/cwd isolation and cleanup are intentional, including on exceptions. The adapter restores its original cwd and the two environment settings afterward. Upstream imports may change other process-global settings, and cached loggers may keep file handles until the process exits; cleanup is not a secure-erasure guarantee.

Use the standalone CLI in a fresh process, not a concurrent embedded host: upstream uses process-global environment, working-directory, and logger state. Adapter executions are serialized, but other threads in a host are not controlled. Already-imported Swarms instances may have initialized telemetry before this adapter; the standalone CLI avoids that case. Environment loading occurs from the temporary cwd, not the repository's `.env`. Supply hub configuration through the environment.

Stdout is JSON; upstream diagnostic prints are redirected to stderr. Workflow output, diagnostics, and provider error bodies may include task-derived text. Treat both streams as sensitive and do not commit them. This adapter is not a security sandbox for an untrusted third-party SDK.

## What was verified

Offline contract tests check validation, explicit opt-in, constructor settings, hub delegation, cleanup, and CLI JSON. Source-reference tests check the canonical path, shallow configuration, gitlink, and source hashes without importing the SDK. The installed upstream SDK was also exercised twice with its real `Agent` and `SequentialWorkflow`, a deterministic hub stub, and socket connections forbidden: four stub requests completed and temporary workspaces were removed. This is genuine orchestration compatibility evidence, **not a live provider or hub HTTP integration test**.

Run the focused tests with:

```sh
python3 -m pytest -q tests/test_swarms_adapter.py tests/test_swarms_reference.py tests/test_swarms_sdk.py
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```

The optional SDK test skips when Swarms is not installed. Native Termux installation, live provider calls, production promotion, concurrency gains, and task-quality improvements remain unverified. See [`VALIDATION.md`](VALIDATION.md) for the recorded local results.

## Remote-first and research lanes

The Python pin is the Kye Gomez behavioral parity origin; Rust is a separate primary/parallel evaluation backend, not an assumption of API equivalence. [Remote validation and Workspace operation](REMOTE.md) keep Termux as the control surface. The [pinned research/wallet registry](research-lanes.json) and `python3 scripts/swarms/research-plan.py --lane research --task "Compare supplied evidence"` produce offline plans only: AdvancedResearch is not yet a live adapted research runtime. [Research and wallet findings](../../docs/research/SWARMS-RESEARCH-WALLETS.md) map to existing MSM-005 bids/wagers/cards rather than a second ledger.

## Current wiring and paper-wallet scope

See [Operating status](OPERATING-STATUS.md) for invocation, hub routing and the unconnected quota/3L0 boundaries. Research framework runtime integration remains open; the planner is not an implementation of AdvancedResearch. Wallet work means paper CSV accounting under MSM-005/MSM-012, not a chain adapter or swarm deployment.
