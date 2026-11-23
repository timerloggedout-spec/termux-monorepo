# refTemplates Continuous Evaluation

**Status:** P0–P7 spine on PR #688 (integrity scoped to smods after dense failure)  
**Laya:** IMPLEMENTATION phase — `refTemplates/16_Org_Phased/laya/IMPLEMENTATION.md`  
**Intercom:** `docs/ops/DENSE-FEEDBACK-INTERCOM.md`

## Scripts

| Script | Phase |
|--------|-------|
| `refTemplates_inventory.py` | P1 — inventories all categories; validates README + SOURCE for Tier-C `13_*` patterns and Tier-A `15_*` children |
| `submodule_integrity.py` (smods-scoped) | P2 |
| `refTemplates_score.py` | P3 — research-template cohort under `15_*`; Tier-C `13_*` patterns stay unscored |
| `refTemplates_deepwiki_batch.py` | P4 |
| `refTemplates_commit_slice.py` | P5 |
| `refTemplates_papers_seed.py` | P6 |
| `.github/workflows/refTemplates-eval.yml` | P7 |

Tier-C pattern references participate in metadata inventory and workflow visibility. They remain outside the Tier-A research-template score and the 12-silo Delphi participant registry.

## Validate → iterate → repeat

1. Push / schedule runs inventory `--strict` + score + papers seed  
2. Failures **name the path** (dense)  
3. Fix or hold; dual-gate still owns promote  
4. Adaptive-wait: stay busy on disjoint work while gates settle  

**Agent-Identity:** Grok (Administrator) CXO  
