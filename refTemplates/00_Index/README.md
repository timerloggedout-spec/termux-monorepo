# refTemplates — Index (SSOT)

**Narrow slice** of the full environment reconstruction. See RECOVERY.md.

| Path | Role |
|------|------|
| 00_Index/ | This navigator + recovery + SOURCE map |
| 01_Agent_Runtime/ … 14_* | Categorical metadata from skeleton |
| 15_Research_Repo_Templates/ | Consolidated research scaffolds, including the Dicklesworthstone Flywheel stack profile |
| 16_Org_Phased/ | Orgs + Enterprise phase gates |
| 17_Papers/ | Cited research + implementation sources |
| smods/ | **Live** custom-adapted gitlink lane |

## Continuous evaluation

- Policy: docs/ops/REFTEMPLATES-CONTINUOUS-EVAL.md (ELO layers, DeepWiki batch, commit slices)
- Integration lane: docs/ops/RESEARCH-INTEGRATION-LANE.md
- Flywheel stack integration: docs/ops/DICKLESWORTHSTONE-FLYWHEEL-INTEGRATION.md
- Inventory script: scripts/ci/refTemplates_inventory.py
- Workflow hooks: docs/ops/REFTEMPLATES-WORKFLOW-HOOKS.md

All slots are continuous repopulate / upgrade / score targets — not a one-shot dump. Live gitlinks require a real custom fork, immutable reviewed pin, compatibility evidence, and passing gates.

## Brain research references

- [Brain filename and agent-architecture dossier](../17_Papers/citations/brain-file-and-agent-architecture-survey.md) — user-supplied GitHub and academic references classified by responsibility, evidence relationship, transfer and limitation.
- [Monorepo Brain subsystem map](../../docs/architecture/TERMUX-MONOREPO-BRAIN-SUBSYSTEM-MAP.md) — target subsystem taxonomy and existing-owner boundaries.
- [qdesk.brain-rs RFP #5501](https://github.com/timerloggedout-spec/termux-monorepo/issues/5501) — formal Delphi intake; evaluation only, no runtime authority.
