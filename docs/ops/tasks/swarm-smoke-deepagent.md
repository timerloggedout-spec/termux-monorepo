# SMOKE TASK — DeepAgent first-dispatch proof (bounded, read-only)

Proof dispatch under the provider-utilization fix (owner, 2026-11-01):
surface `deepagent-task.yml` has 0 runs ever; this file is its smoke input.

## Instruction to the agent (if reached)

Report ONLY: device hostname, current time, and `deepagent-dispatch` presence.
Modify nothing. Write no files. Run no other tools. This is a liveness
smoke, not a work task.

## Bounds

- Read-only. Any state change = out of scope.
- Dispatcher: optimizations-assurance lane; stamp on issue #2735.
