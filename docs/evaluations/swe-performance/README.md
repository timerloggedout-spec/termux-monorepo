# Optional SWE Reference Evidence

**Implements:** THUB-007  
**Status:** Optional bounded reference adapter; repository-local development evidence remains primary.

The `swe-reference-evaluation.yml` workflow exists only to create a redacted, one-instance reference manifest from the pinned `mini-swe-agent_fork`. It is not a production agent runner, a routing authority, a benchmark leaderboard, or a path to automated merging.

## Invocation Boundary

The workflow is manual only. It executes an external reference run only when both controls are true:

| Control | Owner | Purpose |
|---|---|---|
| `run_external_reference=true` workflow-dispatch input | Operator | Makes the individual request explicit. |
| `SWE_REFERENCE_EVALUATION_ENABLED=true` repository variable | Repository administrator | Enables the controlled external-reference lane. |

If either control is absent, the workflow records safe non-execution. It neither clones the reference nor reads a provider credential.

## Credential and Output Boundary

`SWE_EVALUATION_API_KEY` is deliberately mapped **only** to the one bounded benchmark process. Checkout, cloning, dependency installation, package build hooks, manifest creation, artifact upload, and all disabled-path steps run without the provider credential. No provider key is job-scoped.

Each enabled run is restricted to one `0:1` instance and emits at most a redacted manifest. The workflow never uploads prompts, trajectories, source patches, prediction files, logs, raw review content, or credentials. A zero-exit reference run must have exactly one prediction record; otherwise manifest construction fails closed. `agent-run-complete` denotes only that the bounded agent produced evidence, not that SWE-bench resolved the task.

## Result Handling

Only audited redacted manifests may be committed below `docs/evaluations/swe-performance/results/`. GitHub Actions artifacts expire after fourteen days. No result may be used to override repository-local correctness, review-resolution, duplicate-avoidance, feedback-time, coordination, or resource-cost evidence.

## References

[1]: https://github.com/timerloggedout-spec/SWE-agent_fork "SWE-agent fork"
[2]: https://github.com/timerloggedout-spec/mini-swe-agent_fork "mini-SWE-agent fork"
