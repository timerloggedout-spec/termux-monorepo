# What the Swarms code actually does

The existing optional integration is aimed at the correct project: **Kye Gomez’s `kyegomez/swarms`**, pinned to `8ec7948ce6e8ab28c4454d6c2c3187a735672067`. Selected source paths support keeping the current bounded sequential adapter. No definite adapter defect was established by this review; broader framework adoption still needs separate integration tests.

## Confirmed execution path

[`SequentialWorkflow` constructs an `AgentRearrange`](https://github.com/kyegomez/swarms/blob/8ec7948ce6e8ab28c4454d6c2c3187a735672067/swarms/structs/sequential_workflow.py#L172-L185), then [delegates `run()` to it](https://github.com/kyegomez/swarms/blob/8ec7948ce6e8ab28c4454d6c2c3187a735672067/swarms/structs/sequential_workflow.py#L316-L374). This is genuine upstream orchestration, not a locally imitated workflow. The monorepo’s [`_HubLLM`](../../src/swarms_adapter.py) forwards the SDK’s structured messages rather than discarding them when `task=None`.

The adapter configures one or two agents, each with one loop and one SDK attempt, and one to three workflow passes. These are orchestration limits, **not a global HTTP/token budget**. Upstream additionally supports [optional drift detection and pipeline retries](https://github.com/kyegomez/swarms/blob/8ec7948ce6e8ab28c4454d6c2c3187a735672067/swarms/structs/sequential_workflow.py#L256-L301); the current adapter does not enable them. Provider/hub retries remain a separate concern.

## The most important default: outbound telemetry

[`telemetry_on()` returns true when its environment variable is absent](https://github.com/kyegomez/swarms/blob/8ec7948ce6e8ab28c4454d6c2c3187a735672067/swarms/telemetry/otel.py#L46-L69). A custom model client alone therefore does not make direct upstream use telemetry-free. The current adapter sets `SWARMS_TELEMETRY_ON=false` **before** its lazy import. Keep this explicit opt-out, including in any new service wrapper. An already-imported SDK may already have initialized process state; the standalone CLI is the supported use here.

## Workspace and memory are distinct from tools

The upstream agent defaults to [`context_compression=True` and `persistent_memory=False`](https://github.com/kyegomez/swarms/blob/8ec7948ce6e8ab28c4454d6c2c3187a735672067/swarms/structs/agent.py#L380-L384), and [constructs an MCP manager](https://github.com/kyegomez/swarms/blob/8ec7948ce6e8ab28c4454d6c2c3187a735672067/swarms/structs/agent.py#L513-L527). These facts are not proof that a tool or server has been authorized. The adapter supplies `tools=[]` and no MCP URLs/configuration.

Autosave flags do not establish that the entire imported framework is filesystem-side-effect-free. The adapter uses a temporary cwd/workspace and restores its environment/cwd even after exceptions. Its module-local lock protects its own calls, **not unrelated threads in the same process**. This is containment for the chosen CLI path, not a security sandbox for untrusted SDK code.

## Packaging and architecture choices

The [pinned manifest](https://github.com/kyegomez/swarms/blob/8ec7948ce6e8ab28c4454d6c2c3187a735672067/pyproject.toml#L49-L83) declares Beta status and includes native/platform-sensitive dependencies. Optional `fast` extras add RouteHub and rustworkx; their presence does not demonstrate a speedup or Android compatibility.

The [package exports](https://github.com/kyegomez/swarms/blob/8ec7948ce6e8ab28c4454d6c2c3187a735672067/swarms/structs/__init__.py) expose concurrent, graph, and hierarchical architectures alongside the sequential one. Availability in that API is not evidence that the current adapter implements them or that they outperform the existing local orchestrator. Rust and remote-service alternatives remain valid; see [Swarms Rust](SWARMS-RUST.md).

## What has actually run

The [genuine SDK test](../../tests/test_swarms_sdk.py), not merely mocked constructors, passed in the dedicated Linux environment. It ran the real agents/workflow with deterministic hub responses and socket connections forbidden. The [adapter tests](../../tests/test_swarms_adapter.py) separately exercise constructor settings, opt-in validation, message forwarding, JSON stdout, cleanup, and restoration after exceptions. See [validation evidence](../../integrations/swarms/VALIDATION.md) for current test results and limitations.

This is a **selected-path source review**, not a security certification, dependency-vulnerability audit, review of all 455 personal repositories, or examination of all historical commits. Source size measurements in the [ecosystem summary](SWARMS-ECOSYSTEM.md) are not review-coverage counts. No provider call, native Android build, model-quality comparison, or remote deployment was performed.
