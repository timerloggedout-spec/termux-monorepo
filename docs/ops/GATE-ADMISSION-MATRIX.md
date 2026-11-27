# Gate Admission Matrix

**Owner:** repository gate policy  
**Updated:** 2026-11-27  
**Design:** [Gate Admission Optimization](../superpowers/specs/2026-11-27-gate-admission-optimization.md)

## Admission policy

| Lane | Class | Admission condition | Evidence | Inapplicable / unavailable result |
|---|---|---|---|---|
| `repo-gate` | Required | Every pull request and integration push | Changed-file hygiene, portability, secrets, and debt ratchet | Required execution |
| Siglary validator | Promotion-required | Every promotion candidate | Exact-head mandate validation | Promotion remains pending |
| `termux-smoke` | Surface-conditional | Changed paths match the canonical Termux surface registry, or manual dispatch | Smoke regression tests, core smoke, optional agent-surface probes | `SKIPPED` with reason; diff uncertainty runs smoke |
| Dangle census | Reference-conditional | A supported reference source or target root changes | Existing baseline ratchet and JSON report | Outside supported roots: defer to scheduled/manual census |
| Bucket-headroom contracts | Quota-code-conditional | Bucket logic, watcher workflow, process contract, or its tests change | PyYAML/pytest contract suite | Path-scoped workflow stays idle |
| Vercel deploy | Project-conditional | Project-scoped source changes and quota/cooldown admission succeeds | `vercel_ignore_build.sh`, project config, batch-dispatch receipt | Skip unchanged projects; defer on quota/cooldown |
| Devin worker | Optional capacity lane | Task fit plus fresh no-cost API entitlement and quota evidence | Provider/account receipt, task output, tests, integration review | `BLOCKED` pending entitlement evidence or `SKIPPED_CAPACITY` |

## Canonical Termux surface

The stdlib classifier in `scripts/ci/gate_admission.py` owns the path decision. The workflow uses the same helper; the PR classifier consumes the same predicate.

- Exact files: `scripts/ci/repo_gate.py`, `scripts/ci/termux_smoke.py`, `scripts/ci/validate_sim_memory.py`, `scripts/agent_evolution/sim_memory.py`, `docs/ARCHW1Z-GATE.md`, `docs/TERMUX-SMOKE.md`, `docs/ops/SELF-IMPROVEMENT-MEMORY.schema.json`, `tests/test_termux_smoke.py`, `tests/test_sim_memory.py`, `tests/fixtures/sim-memory-smoke.jsonl`, `.github/workflows/termux-smoke.yml`.
- Prefixes: `scripts/ci/termux_smoke/`, `.github/connectors/`, `deepcli/`, `deepcli-tui/`, `multi-ai-cli/`, `bin/`, `archwiz/`, `termux-multi-agent/`, `integrations/ratatui-tokio-dashboard/`.

Manual workflow dispatch is an explicit request to run the smoke surface. An unavailable diff admits smoke as the safe default.

## Reference-aware dangle coverage

The dangle scanner continues to report findings from `.github/` and `apps/`. Its pull-request trigger also watches target roots: `docs/`, `scripts/`, `ops/`, `workspace/`, `archwiz/`, `.agents/`, `config/`, `tests/`, `integrations/`, `deepcli/`, `deepcli-tui/`, `multi-ai-cli/`, `bin/`, `termux-multi-agent/`, `mcp-hub/`, `demo-portal/`, plus root instruction/index files. The existing baseline remains the debt boundary; new findings remain the failure condition.

## Provider admission

### Vercel

The three checked-in project configurations use project-specific ignore commands. The helper skips unchanged project roots and continues a build for relevant changes or incomplete Git evidence. The batch deploy lane applies its quota reserve, observed-count reconciliation, and project cooldown.

Current evidence status: **configured and locally regression-tested; provider-side skip/build effect requires a deployment event receipt on an unrelated and a relevant SHA.**

### Devin

The operator reported free-tier availability and referral marketing replenishment on 2026-11-27. The current repository gate register still records Devin API access as paid-organization-only/card-blocked for the Free organization; the current referral programme index does not list Devin. Treat the operator report as a fresh lead and obtain a current account/entitlement receipt before admission.

Admission ledger fields:

- account/plan eligibility;
- API quota available and reset time;
- billing/card requirement;
- referral programme name and explicit Devin credit terms;
- task scope, expected output, and human integration cost;
- run ID, result, and accepted contribution.

Referral marketing rewards remain separate from API quota until the provider's terms explicitly connect them.

## Result semantics

- `PASS`: required execution passed on the candidate SHA.
- `FAIL`: required execution failed.
- `SKIPPED`: classifier established inapplicability and recorded a reason.
- `BLOCKED`: required admission evidence or authorization is pending.
- `PENDING`: admitted execution is awaiting a result.

Record gate applicability separately from execution status. Record provider capacity separately from code correctness.
