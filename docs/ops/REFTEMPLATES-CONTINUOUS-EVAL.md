# refTemplates Continuous Evaluation

**Status:** P0–P7 spine on PR #688 (integrity scoped to smods after dense failure)  
**Laya:** IMPLEMENTATION phase — `refTemplates/16_Org_Phased/laya/IMPLEMENTATION.md`  
**Intercom:** `docs/ops/DENSE-FEEDBACK-INTERCOM.md`

## Scripts

| Script | Phase |
|--------|-------|
| `refTemplates_inventory.py` | P1 |
| `submodule_integrity.py` (smods-scoped) | P2 |
| `refTemplates_score.py` | P3 |
| `refTemplates_deepwiki_batch.py` | P4 |
| `refTemplates_commit_slice.py` | P5 |
| `refTemplates_papers_seed.py` | P6 |
| `.github/workflows/refTemplates-eval.yml` | P7 |

## Validate → iterate → repeat

1. Push / schedule runs inventory `--strict` + score + papers seed  
2. Failures **name the path** (dense)  
3. Fix or hold; dual-gate still owns promote  
4. Adaptive-wait: stay busy on disjoint work while gates settle  

**Agent-Identity:** Grok (Administrator) CXO  
