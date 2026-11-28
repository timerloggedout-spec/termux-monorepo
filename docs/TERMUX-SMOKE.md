# Termux Smoke Gate — Agentic runtime surface

> **Branch:** `termux-smoke`  
> **Script:** `scripts/ci/termux_smoke.py`  
> **Workflow:** `.github/workflows/termux-smoke.yml`  
> **Admission:** `scripts/ci/gate_admission.py`

## Position in the gate spine

The repo gate is universal. Termux smoke validates slices that target the Termux execution surface.

The workflow check remains visible on every pull request and configured integration push. A fast stdlib admission step selects the smoke suite from exact base/head changed paths.

## Admission rules

| Event / evidence | Decision |
|---|---|
| Changed path matches an exact Termux file or prefix | REQUIRED |
| Manual `workflow_dispatch` | REQUIRED |
| Base/head SHA or Git diff evidence unavailable | REQUIRED |
| Complete changed-path list with no Termux match | SKIPPED — `Termux surface unchanged` |

The helper owns the canonical path registry. The PR lane classifier uses the same predicate and emits `termux_smoke_required`. A workflow skip records applicability; the classifier keeps execution evidence separate.

### Canonical exact paths

- `scripts/ci/repo_gate.py`
- `scripts/ci/gate_admission.py`
- `scripts/ci/termux_smoke.py`
- `scripts/ci/validate_sim_memory.py`
- `scripts/agent_evolution/sim_memory.py`
- `docs/ARCHW1Z-GATE.md`
- `docs/TERMUX-SMOKE.md`
- `docs/ops/SELF-IMPROVEMENT-MEMORY.schema.json`
- `tests/test_termux_smoke.py`
- `tests/test_sim_memory.py`
- `tests/fixtures/sim-memory-smoke.jsonl`
- `.github/workflows/termux-smoke.yml`

### Canonical prefixes

- `.github/connectors/`
- `scripts/ci/termux_smoke/`
- `deepcli/`
- `deepcli-tui/`
- `multi-ai-cli/`
- `bin/`
- `archwiz/`
- `termux-multi-agent/`
- `integrations/ratatui-tokio-dashboard/`

## Local execution

```bash
python3 scripts/ci/termux_smoke.py
python3 scripts/ci/termux_smoke.py --with-optional
python3 scripts/ci/termux_smoke.py --json --with-optional
python3 scripts/ci/gate_admission.py --event workflow_dispatch
```

## Runtime checks

| Check | Requirement |
|---|---|
| Python ≥ 3.9 | required |
| Repository layout and gate files | required |
| repo-gate compiles | required |
| smoke self-compiles | required |
| SIM-memory contract | required |
| git on PATH | required |
| bash on Termux | required |
| writable TMPDIR | required |
| connector smoke | required |
| deepcli / multi-ai compile | optional |
| archwiz sample modules compile | optional |
| termux-api presence | observation |

## Related test ownership

Bucket-headroom quota tests use PyYAML/pytest and run in `.github/workflows/bucket-headroom-contract.yml`, scoped to quota logic, watcher workflow, process contract, and tests. Termux smoke retains the stdlib runtime path.

## Result semantics

- `PASS`: required smoke execution passed on the candidate SHA.
- `FAIL`: required smoke execution failed.
- `SKIPPED`: the path classifier established an unrelated execution surface and recorded the reason.
- `BLOCKED`: admission evidence requires operator/provider input.
- `PENDING`: admitted smoke execution is awaiting a result.
