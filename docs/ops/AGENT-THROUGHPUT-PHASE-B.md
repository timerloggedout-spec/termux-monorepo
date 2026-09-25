# ATES Phase B — Runtime Evidence Emission

**Status:** implemented as an observer-only Phase B producer  
**Priority:** P0 telemetry / P2 presentation  
**Contract:** `docs/ops/AGENT-THROUGHPUT-EVENT.schema.json`

## Why this is the next compounding step

Phase A already provides the pure ATES/WTCV/TCV reducer and quality gate. The missing high-value boundary was runtime evidence: a schema without real run/attempt/SHA-linked events cannot support longitudinal measurement.

Phase B closes that gap without rewriting every agent workflow.

## Producer

`.github/workflows/agent-throughput-evidence.yml` observes completed runs for the explicitly admitted agent workflows:

- Gemini Dispatch
- Jules on Issues
- Agent review → auto Jules
- DeepSeek CI

It uses the GitHub `workflow_run` observer boundary and reads completed job timings through the Actions API. The producer checks out only its own trusted default-branch implementation; it never executes the triggering run's code.

The resulting evidence contains:

- `task_started`
- `active_window`
- `task_completed`
- run ID / attempt
- source SHA
- agent identity from the explicit workflow allowlist
- structural complexity when exactly one associated PR supplies additions/deletions/files-changed

Unknown or ambiguous evidence stays missing.

## ATES semantics

The emitted events are fed through the existing `she.metrics.agent_throughput.reduce_events` reducer. The observer does **not** invent a sequential baseline. Therefore `parallel_yield` and `ates` remain `null` until a declared baseline is supplied.

That is intentional: the system now measures actual agent execution while preserving the repository invariant that missing evidence is not a fabricated zero or inferred comparison.

### Next baseline increment

Create a bounded baseline cohort using the same task definition and explicit serial execution, then attach its measured wall-clock duration to the cohort record. The baseline must be task-comparable and independently attributable; it must not be inferred from the parallel run itself.

## Security / privacy

No prompts, completions, credentials, tool payloads, arbitrary comments, or repository contents enter the evidence artifact.

`workflow_run` is treated as a privileged observer boundary. The observer never checks out or executes the triggering SHA. The workflow remains read-only and treats all triggering-run data as untrusted metadata.

## Acceptance

- real completed agent runs produce JSONL events;
- every emitted event is bound to run/attempt/SHA;
- missing job timing does not manufacture duration;
- ambiguous PR associations do not manufacture complexity;
- artifacts contain sanitized JSONL + reducer output + receipt;
- ATES remains observational and cannot block merge;
- re-runs remain distinct via `run_attempt`;
- downstream consumers can deduplicate using the deterministic `event_id`.
