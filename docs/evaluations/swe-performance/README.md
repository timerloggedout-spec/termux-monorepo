# SWE Reference Adapter

**Implements:** THUB-007  
**Suite position:** Optional reference adapter for the [Repository Development Performance Suite](../development-performance/SUITE.md).

The user-owned `SWE-agent_fork` and `mini-swe-agent_fork` are **reference implementations** that inform comparable agent-evaluation methodology. They are not the target of THUB-007 and their external SWE-bench scores do not measure `termux-monorepo` development performance by themselves.[1] [2]

> The suite’s primary subject is this repository’s development lifecycle: change delivery, validation health, review flow, automation response, and merge readiness. A SWE-reference result is an optional, separately labeled context signal.

## Adapter Boundary

| Property | Rule |
|---|---|
| Reference runtime | The first adapter pins `mini-swe-agent_fork` at `a83fcae82d2a08f0ee0c688f9d137b3566c097f8`. The larger SWE-agent fork remains a future adapter source. |
| Invocation | Manual dispatch only. No schedule, fan-out, or automatic issue/PR trigger can invoke a provider model. |
| Workload | Exactly one benchmark instance (`0:1`) with one worker; allowed suite aliases are `lite` and `verified`. |
| Credential | A human-managed `SWE_EVALUATION_API_KEY` secret is required at runtime. The workflow neither creates nor changes it. |
| Artifact | Only a redacted `manifest.json` is uploaded for 14 days. No prompt, trajectory, prediction patch, log, browser/session state, or credential is retained. |
| Score semantics | `agent-run-complete` records a completed adapter run; it is **not** a confirmed benchmark resolution. Resolution remains `null` until a separately reviewed scorer adapter exists. |

## Result Contract

The reference adapter uses `scripts/ci/swe_evaluation_contract.py`. Its manifest contains the fixed reference revision, bounded benchmark parameters, model identifier, timing, executor state, completed-instance count, and canonical SHA-256 digest. It rejects secret-shaped values, unknown fields, invalid state/count relationships, and unbounded slices.

If a reviewed reference result becomes a durable repository record, commit only its redacted manifest under `docs/evaluations/swe-performance/results/`. The deterministic suite contract workflow validates it. Do not commit downloaded artifacts, `preds.json`, trajectories, patches, or raw logs.

## Extension Rule

A new reference adapter must document its pin, workload cap, credential boundary, output schema, and relationship to repository-development signals before use. It cannot replace the deterministic `repository-pr-lifecycle` adapter or cause automatic repository actions.

## References

[1]: https://github.com/timerloggedout-spec/mini-swe-agent_fork "mini-SWE-agent fork"
[2]: https://github.com/timerloggedout-spec/SWE-agent_fork "SWE-agent fork"
