# ITEMS — cost-of-remembering-integration

| ID | Item | Status | Notes |
|----|------|--------|-------|
| COR-01 | Own fork `timerloggedout-spec/cost-of-remembering_fork` | **done** | HEAD `14c6f74a877a2f7b94b332c03395b4793158942e` |
| COR-02 | Knowledge card `docs/icm/objects/knowledge/cost-of-remembering.md` | **done** | Claim + boundary + citation |
| COR-03 | Method-coverage row | **done** | Filesystem memory evidence |
| COR-04 | `.gitmodules` entry | **done** | path/url/branch/shallow declared |
| COR-05 | Gitlink / `git submodule add` (mode 160000) | **blocked** | Requires local clone, collaborator, or Termux MCP — not writable via file-push API |
| COR-06 | template-candidates.yaml COST_OF_REMEMBERING | **done** | |
| COR-07 | objects/_index entry | **done** | |
| COR-08 | ICM-ARCHITECT-INTEGRATION reference table | **done** | |
| COR-09 | Content-Agent-Routing-Promptbase reinforcement | **done** | Already pinned |
| COR-10 | Dual gates | pending | After COR-05 |
| AE-01 | AuditEngine_fork owned | **done** | HEAD `4b8313fcd9198b0cdc266014ee002828ac79a7b2` |
| AE-02 | `.gitmodules` + knowledge card | **done** | |
| AE-03 | Gitlink mode 160000 | **blocked** | Same as COR-05 |

## Unblock recipe

See PR #485 comment (Agent-Identity: Grok Administrator). Scripts:

- `scripts/icm/init-cost-of-remembering-submodule.sh`
- `scripts/icm/init-auditengine-submodule.sh`
