# Model Selection Market — Ops Card

**Proposal SSOT:** `docs/proposals/active/model-selection-market/`  
**Registry id:** `model-selection-market`  
**Status:** executing (MSM-000..007 landed; dual-gate before any weight promote)

## Intent

Equal-weight free-model bootstrap → 3L0 evidence weights; series|parallel|concurrent selection; DSPy DoE consideration lane; observational bets + trading cards; live catalog join; model_router peer hook (observe-only).

## Landed

| ID | Item | Status |
|----|------|--------|
| MSM-000 | Proposal packet | done (#959) |
| MSM-001 | Equal-weight bootstrap | done |
| MSM-002 | Append-only performance ledger | done |
| MSM-003 | series \| parallel \| concurrent selector | done |
| MSM-004 | DSPy-DoE consideration stub | done |
| MSM-005 | Cards + bets + graph stub | done |
| MSM-006 | Live catalog join (observe) | done (`catalog_join.py`) |
| MSM-007 | model_router peer hook | done (`router_peer.py`) — observe only |

## Do / Do not

| Do | Do not |
|----|--------|
| Dual-gate before promote | Auto-merge without gates (YOLO) |
| Keep public leaderboards as features | Use public Elo as production weights |
| Append bounded ledger samples | Store raw PR/issue bodies |
| Free-only routes | Paid exhaustion paths |
| Explicit card trades | Silent cross-role weight copy |
| Observe-mode weights until promote rule | Promote on single sample |

## Runtime smoke

```bash
python3 -m scripts.model_selection_market.cli all-demo
python3 -m scripts.model_selection_market.cli join
python3 -m scripts.model_selection_market.cli peers --role triage -k 5
python3 -m unittest scripts.model_selection_market.test_msm -v
```

## Related

- `docs/schemas/openrouter-free-catalog.json`
- `scripts/live_catalog_feed.py` / `scripts/model_router_bootstrap.py`
- `docs/ops/ROUTING-LOGIC-CHAIN.md`
- `docs/ops/DECISION-ENGINES.md`

Agent-Identity: Grok (Administrator)
