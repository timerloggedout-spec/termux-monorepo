# refTemplates — Index (SSOT)

**Narrow slice** of the full environment reconstruction. See `RECOVERY.md`.

| Path | Role |
|------|------|
| `00_Index/` | This navigator + recovery + SOURCE map |
| `01_Agent_Runtime/` … `14_*` | Categorical metadata from skeleton |
| `15_Research_Repo_Templates/` | Consolidated research scaffolds |
| `16_Org_Phased/` | Orgs + Enterprise phase gates |
| `17_Papers/` | Cited research + implementation sources |
| `smods/` | **Live** custom-adapted gitlink lane |

## Continuous evaluation

- Policy: `docs/ops/REFTEMPLATES-CONTINUOUS-EVAL.md` (ELO layers, DeepWiki batch, commit slices)
- Integration lane: `docs/ops/RESEARCH-INTEGRATION-LANE.md`
- Inventory script: `scripts/ci/refTemplates_inventory.py`
- Workflow hooks: `docs/ops/REFTEMPLATES-WORKFLOW-HOOKS.md`

All slots are continuous repopulate / upgrade / score targets — not a one-shot dump.
