# Swarms in the Termux monorepo

Swarms supplies an optional multi-agent coordination layer. The monorepo keeps ownership of provider routing, device permissions, validation, and Git operations. The first applied slice is a sequential analysis-and-review workflow, not a replacement for the existing development environment.

## Parity authority and remote-first operation

Kye Gomez’s pinned Python `kyegomez/swarms` is the intended behavioral parity origin. `The-Swarm-Corporation/swarms-rs` is the same Swarms ecosystem, not the same implementation or a blanket parity claim; its pinned worker may be a primary or parallel test backend as evidence develops. Custom modules and other upstreams remain valid candidates. Re-run the same task fixtures before claiming parity or promoting a replacement.

Termux is the control surface, not a requirement to compile every SDK on Android. Use remote Linux WorkSpaces/Codespaces or Actions for the orchestration and validation plane; see [remote execution](../../integrations/swarms/REMOTE.md). This PR adds remote validation, not a deployed research service. Research/wallet lanes reuse the existing market authority; see [research and wallets](../research/SWARMS-RESEARCH-WALLETS.md).

## Keep the existing boundaries

The root [`src/orchestrator.py`](../../src/orchestrator.py) implements a code-change/test/retry loop. It already sends model requests through [`llm_api_hub/clients/openai_compat.py`](../../llm_api_hub/clients/openai_compat.py). The new [`src/swarms_adapter.py`](../../src/swarms_adapter.py) is a separate entry point so importing or running the existing orchestrator does not suddenly import Swarms, install packages, or spawn agents.

The intended flow is: explicit task → Swarms sequential agents → existing API hub → configured provider → workflow result. The adapter does not inspect files or independently browse for evidence. Research supplied to a task remains input, not automatically verified knowledge. Review output is another model response, not an executable permission or a passed test.

[`hub_mcp`](../../hub_mcp/) remains the policy boundary for structured device jobs. No Swarms agent receives shell, filesystem mutation, MCP servers, or automatic Git capabilities in this slice. A future tool bridge must validate the same capability envelopes rather than pass arbitrary tool names or shell text through an agent.

[`multi-ai-cli`](../../multi-ai-cli/) owns provider backend and dispatcher concerns, while [`deepcli`](../../deepcli/) owns a conversational CLI surface. Neither needs to be rewritten to adopt this optional workflow. [`termux-multi-agent`](../../termux-multi-agent/) has its own workspace and orchestration modules; it is not silently rewired by this change.

[`commingle-swarm`](../../commingle-swarm/README.md) is a different project: a distributed PWA and headless Termux application with P2P/accounting concerns. Its name does not make it part of Kye Gomez's Swarms stack.

## Organize references separately from executable integration

The [upstream Swarms reference](https://github.com/kyegomez/swarms) is pinned as a shallow gitlink at `refTemplates/smods/swarms`. The category `refTemplates/08_Swarm_References/` is metadata/navigation, not a second copy of the runtime. The adapter, its install instructions, and its source hashes live under [`integrations/swarms/`](../../integrations/swarms/README.md).

The existing `/workspace/termux-monorepo` was already a shallow monorepo clone. Inspection found no separate pre-existing Swarms checkout within it. That monorepo was not moved, pulled, reset, or recreated. A new upstream Swarms reference was materialized at the canonical location instead; this is organization of a new reference, not a claimed relocation of a nonexistent checkout. Unrelated local changes remain untouched.

The gitlink and [`source-lock.json`](../../integrations/swarms/source-lock.json) identify revision `8ec7948ce6e8ab28c4454d6c2c3187a735672067` (manifest version `16.0.2`). This is an upstream source pin, not a user-owned fork, package dependency lock, or Android support certification. Upstream's manifest leaves most dependencies unconstrained, so an installation can resolve different transitive versions over time.

## What is deliberately not enabled

The broader ecosystem includes tool libraries, model wrappers, memory stores, Rust orchestration, and hosted API examples. Those are research candidates, not unconditional installation dependencies. In particular, the memory/model stacks introduce native and heavyweight dependencies that should not become a requirement for a phone-oriented offline CLI.

The pinned Swarms manifest requires Python 3.10 or newer. The monorepo's core smoke contract supports older interpreters; the optional integration does not raise that core minimum. Linux validation is not evidence that native dependencies build on Android/Bionic, and a Linux ARM64 container is not a native Termux environment.

No provider credential is embedded or copied into the repository. No hosted Swarms account is required by this integration. No paid model requests, live device actions, persistent automation, or public deployment are part of the initial validation.

## How to evaluate the next slice

Use the same task and configured hub route for the existing single-agent baseline and the sequential treatment. Record testable task success separately from the reviewer agent's verdict. Compare actual hub requests, errors, wall time, and token usage when those are observable; do not invent an improvement percentage from architectural claims. Only add concurrent or hierarchical execution after a concrete task shows a benefit and the existing provider quota and tool-permission boundaries remain intact.
