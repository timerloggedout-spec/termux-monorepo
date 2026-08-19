# SWE Reference Performance Evaluation Automation

**Implements:** THUB-007  
**Status:** Bounded, manual GitHub Actions evaluation control plane.

This directory defines the repository’s first performance-evaluation lane based on the user-owned `SWE-agent_fork` and `mini-swe-agent_fork` references. The initial executor uses only the pinned mini-SWE-agent revision because its documented batch interface exposes explicit benchmark, split, slice, output, and worker controls. The larger SWE-agent fork remains a reference source for a later adapter; it is not imported or invoked by the initial workflow.[1] [2]

> **Scope boundary:** GitHub Actions owns orchestration and evidence collection. The BLU B160V is neither a required runner nor a manual control surface. A human-managed provider credential is required before the optional model-bearing workflow can run; the workflow never creates, rotates, logs, commits, or uploads that credential.

## Automation Surface

| Component | Trigger | Purpose | Cost-bearing behavior |
|---|---|---|---|
| `swe-evaluation-contract.yml` | Pull request, integration-branch push, or manual dispatch | Runs deterministic manifest-contract tests and audits any committed, redacted result manifests. | **None.** It does not call a model, download a benchmark, or provision a benchmark environment. |
| `swe-reference-evaluation.yml` | Manual dispatch only | Checks out the pinned mini-SWE-agent reference and runs one `0:1` benchmark slice. | **Opt-in only.** It requires the human-managed `SWE_EVALUATION_API_KEY` secret and has a 60-minute job limit. |
| `swe_evaluation_contract.py` | Called by both workflows | Creates and audits a machine-readable, redacted result manifest. | **None.** It accepts counts and metadata only; trajectories, patches, prompts, logs, prediction payloads, and credentials are excluded. |

## Bounded Run Contract

The manual runner permits only the `lite` or `verified` benchmark aliases, the `dev` or `test` splits, and exactly one benchmark instance (`--slice 0:1`, one worker). The input model identifier must match a constrained identifier format and is rejected if it resembles a credential. The reference revision is fixed to `a83fcae82d2a08f0ee0c688f9d137b3566c097f8` for reproducibility.

The workflow writes and uploads only `manifest.json`. Each manifest has a SHA-256 digest over canonical metadata and records the pinned reference revision, benchmark parameters, model identifier, timing, executor exit code, completed-instance count, and evaluation state. It deliberately leaves `benchmark_resolved_instances` as `null` until a separately designed SWE-bench scoring integration is approved. This prevents an agent-run completion from being misrepresented as benchmark resolution.[1]

| Rejected data class | Reason |
|---|---|
| Provider keys, tokens, browser/session state | Human-managed credentials and sensitive state must not enter source control, logs, or artifacts. |
| Trajectories, prompts, shell transcripts, and patches | They can contain unreviewed code or model/provider context and are unnecessary for the first-run performance record. |
| Unbounded benchmark slices, scheduled runs, or fan-out workers | They create uncontrolled spend and capacity consumption. |
| Automatic issue, PR, or device actions | Performance evaluation must produce validated evidence before it can drive a development action. |

## Result Lifecycle

The manual runner produces an immutable GitHub Actions artifact retained for 14 days. If a reviewed result needs to become a repository record, commit **only** its redacted manifest under `docs/evaluations/swe-performance/results/`; the deterministic contract workflow will audit it. Do not commit downloaded artifacts, raw `preds.json`, trajectories, patches, or logs.

The next adapter must introduce a separate evaluator that converts a compatible prediction artifact into a confirmed resolution score. It must retain the same reference pinning, redaction, digest verification, explicit workload cap, and manual-start policy before any scheduled comparative runs are considered.

## References

[1]: https://github.com/timerloggedout-spec/mini-swe-agent_fork "mini-SWE-agent fork"
[2]: https://github.com/timerloggedout-spec/SWE-agent_fork "SWE-agent fork"
