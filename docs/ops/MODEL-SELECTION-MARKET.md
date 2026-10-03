# Model Selection Market — Ops Card

**Proposal SSOT:** `docs/proposals/active/model-selection-market/`  
**Registry id:** `model-selection-market`  
**Status:** executing (runtime on master via #959; SSOT #961 + this ops fix)

## Intent

Equal-weight free-model bootstrap → 3L0 evidence weights; series|parallel|concurrent selection; DSPy DoE consideration lane; observational bets + trading cards.

## Do / Do not

| Do | Do not |
|----|--------|
| Dual-gate every promote | Auto-merge without gates (YOLO) |
| Keep public leaderboards as features | Use public Elo as production weights |
| Append bounded ledger samples | Store raw PR/issue bodies |
| Free-only routes | Paid exhaustion paths |
| Explicit card trades | Silent cross-role weight copy |
| Observe weights until promote rule | Mutate weights from single sample |

## Landed

| ID | Item | PR |
|----|------|----|
| MSM-000 | Proposal packet | #959 |
| MSM-001 | Equal-weight bootstrap | #959 |
| MSM-002 | Performance ledger | #959 |
| MSM-003 | series\|parallel\|concurrent | #959 |
| MSM-004 | DSPy-DoE stub | #959 |
| MSM-005 | Cards + bets + graph | #959 |

```bash
python3 -m scripts.model_selection_market.cli all-demo
python3 -m unittest scripts.model_selection_market.test_msm -v
```

## Next (planned)

- **MSM-006** — Live catalog join (optional `--catalog` already on bootstrap; wire catalog-feed/latest when present; free-only filter)
- **MSM-007** — model_router / decision_engines peer hook (observe-mode only; no default weight promote)

## Related

- `docs/schemas/model-rotation.yaml`
- `docs/schemas/model-success-matrix.yaml`
- `docs/schemas/llm-leaderboard-matrix.yaml`
- `docs/ops/ROUTING-LOGIC-CHAIN.md`
- `docs/ops/DECISION-ENGINES.md`
- `docs/ops/APPROXINATION-LANE.md`
- `docs/schemas/provider-capabilities.md`

Agent-Identity: Grok (Administrator)
