# Swarms Rust: a viable remote-service candidate

**`swarms-rs` deserves a practical trial.** Rust is acceptable for this monorepo, and remote services are already part of the user’s architecture. There is no reason to force orchestration, inference, and model storage onto the phone or to require Python everywhere.

The reviewed source is [`The-Swarm-Corporation/swarms-rs` at `ee1e74cb6e2c94775db88dddb311f2235e3fe9e3`](https://github.com/The-Swarm-Corporation/swarms-rs/tree/ee1e74cb6e2c94775db88dddb311f2235e3fe9e3). It belongs to the organization namespace, separately from Kye Gomez’s 455-repository personal listing.

## What is implemented

The [workspace](https://github.com/The-Swarm-Corporation/swarms-rs/blob/ee1e74cb6e2c94775db88dddb311f2235e3fe9e3/Cargo.toml#L1-L3) contains the runtime library, procedural macros, and examples. The [crate manifest](https://github.com/The-Swarm-Corporation/swarms-rs/blob/ee1e74cb6e2c94775db88dddb311f2235e3fe9e3/swarms-rs/Cargo.toml#L1-L53) declares version **0.3.0**, edition **2024**, and minimum Rust **1.88**. Its dependencies include Tokio, reqwest, async-openai, and MCP support.

Actual [structure modules](https://github.com/The-Swarm-Corporation/swarms-rs/blob/ee1e74cb6e2c94775db88dddb311f2235e3fe9e3/swarms-rs/src/structs/mod.rs) implement agent construction, sequential/concurrent/graph workflows, routing, conversations, and related orchestration. The source tree includes tests and benchmarks. This is more than a catalog description, but source presence is not evidence that every architecture is reliable under production load. The README’s speed, scale, and “production-ready” claims were not benchmarked here.

## How it can use the existing model hub

The Rust provider exposes [`OpenAI::from_url(base_url, api_key)`](https://github.com/The-Swarm-Corporation/swarms-rs/blob/ee1e74cb6e2c94775db88dddb311f2235e3fe9e3/swarms-rs/src/llm/provider/openai.rs#L46-L66), which sets the OpenAI-compatible base URL and key. Its [`from_env()`](https://github.com/The-Swarm-Corporation/swarms-rs/blob/ee1e74cb6e2c94775db88dddb311f2235e3fe9e3/swarms-rs/src/llm/provider/openai.rs#L86-L95) reads `OPENAI_API_BASE` and `OPENAI_API_KEY`.

The existing [`llm_api_hub` client](../../llm_api_hub/clients/openai_compat.py) uses `LLM_API_HUB_BASE` (default `http://127.0.0.1:8787/v1`) and `LLM_API_HUB_KEY`, posting to `/chat/completions`. A deliberate wrapper can map those settings into the Rust client and explicitly select a configured hub route. This preserves hub ownership of provider routing instead of duplicating credentials/provider policies inside agents.

For hub model names such as `wrapper/...`, prefer explicit `OpenAI::from_url(...).set_model(...)` over automatic provider inference. [`AnyModel`](https://github.com/The-Swarm-Corporation/swarms-rs/blob/ee1e74cb6e2c94775db88dddb311f2235e3fe9e3/swarms-rs/src/llm/provider/any.rs#L119-L149) has its own vendor/model routing; do not assume arbitrary hub route identifiers will resolve to the hub.

The **THUB-013 continuation now verifies this path** with a built, revision-pinned Rust worker calling the actual local hub HTTP server and deterministic stub inference. Tests assert model and message forwarding, non-streaming requests, no tools, token settings, one/two-stage success, cross-pass handoff, authorization failure before inference, deadline cleanup, and valid CLI JSON. This is not live-provider or Android evidence. The [optional Rust adapter](../../integrations/swarms/rust/README.md) records the build and execution contract.

## Deployment choices

| Choice | What runs where | What still needs testing |
|---|---|---|
| Remote Rust orchestration | Rust agents/workflows and hub run on an authorized Linux service; Termux remains a client. | Service packaging, authentication, task/result contract, timeouts, isolation, and connectivity. |
| Termux Rust orchestration | Rust runtime runs on Android; model calls go through the remote hub. | Rust 1.88+ toolchain, Android/Bionic build, TLS/native roots, transitive dependencies, and actual device execution. |
| Local model execution | Model runtime and weights also run on the phone. | A separate resource/backend decision; **not required** by either option above. |

Installing the upstream library alone does not supply a remote service. This slice supplies a controlled executable wrapper, not an authenticated remote task API or a deployment. Keep device actions behind the existing `hub_mcp` capability envelopes. Do not give generic agent tools direct shell/device authority or publicly expose the phone.

## Implemented thin-adapter slice

The worker and stdlib Python CLI wrapper implement the **local hub fixture → one Rust agent → two-stage sequential workflow** path with explicit execution/model selection and isolated temporary state. Upstream's default task-completion tool must be disabled explicitly. Quiet mode still prints diagnostics, direct agent output contains the conversation rather than only the final answer, and sequential workflows write metadata even with agent autosave off. The adapter accounts for all four behaviors instead of relying on defaults.

The source-only assessment preceded this implementation; the current worker now builds and passes its four unit tests plus six actual-hub HTTP tests on Linux x86_64/glibc. The full upstream test suite, live provider requests, Android execution, remote deployment, and Python-versus-Rust performance/task-quality comparison remain unperformed. Rust’s language properties alone do not establish lower inference latency or better task outcomes. The [validation record](../../integrations/swarms/VALIDATION.md) separates these evidence classes.
