# Model Selection Market — Ops Card

**Proposal SSOT:** `docs/proposals/active/model-selection-market/`
**Registry id:** `model-selection-market`
**Status:** posted (PR for review; dual-gate before promote)

## Intent

Equal-weight free-model bootstrap → 3L0 evidence weights; series|parallel|concurrent selection; DSPy DoE consideration lane; observational bets + trading cards.

## Do / Do not

| Do | Do not |
|----|--------|
| Review and dual-gate the proposal PR | Auto-merge without gates |
| Keep public leaderboards as features | Use public Elo as production weights |
| Append bounded ledger samples | Store raw PR/issue bodies |
| Free-only routes | Paid exhaustion paths |
| Explicit card trades | Silent cross-role weight copy |

## Related

- `docs/schemas/model-rotation.yaml`
- `docs/schemas/model-success-matrix.yaml`
- `docs/schemas/llm-leaderboard-matrix.yaml`
- `docs/ops/ROUTING-LOGIC-CHAIN.md`
- `docs/ops/DECISION-ENGINES.md`
- `docs/ops/APPROXINATION-LANE.md`

## Extract order

MSM-000 (docs) → MSM-001 seed loader → MSM-002 ledger → MSM-003 modes → MSM-004 DSPy lane → MSM-005 graph/bets

Agent-Identity: Grok (Administrator)
