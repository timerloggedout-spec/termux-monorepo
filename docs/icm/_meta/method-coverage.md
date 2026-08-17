# ICM Method Coverage — termux-monorepo

This record explains how the monorepo applies the ICM method **without refactoring application code**. The source tree remains authoritative; `docs/icm/` is the agent-readable routing and maintenance layer.

| ICM requirement | Implemented surface | Status |
|---|---|---|
| Small Layer-0 catalog | [`../CLAUDE.md`](../CLAUDE.md), with byte-identical `AGENTS.md` and `routing.md` | Implemented |
| Layer-1 routing contract | [`../CONTEXT.md`](../CONTEXT.md) | Implemented |
| Layer-2 folder contracts | `objects/*/CONTEXT.md`, [`processes/CONTEXT.md`](../processes/CONTEXT.md), and [`maintenance/*/CONTEXT.md`](../maintenance/CONTEXT.md) | Implemented |
| Stable factory separated from per-run product | [`../_shared/CONTEXT.md`](../_shared/CONTEXT.md) versus `maintenance/*/output/` | Implemented |
| Object, process, and first-order change-impact map | [`../objects/_index.md`](../objects/_index.md), [`../processes/`](../processes/), [`../effects/CONTEXT.md`](../effects/CONTEXT.md) | Implemented |
| Explicit human review point | [`../maintenance/02_design/CONTEXT.md`](../maintenance/02_design/CONTEXT.md) | Implemented |
| Source inventory before a map change | [`../maintenance/01_inventory/CONTEXT.md`](../maintenance/01_inventory/CONTEXT.md) | Implemented |
| Verification before promotion | [`../maintenance/03_verify/CONTEXT.md`](../maintenance/03_verify/CONTEXT.md) | Implemented |
| Master-staging validation before later master merge | [`../maintenance/04_promote/CONTEXT.md`](../maintenance/04_promote/CONTEXT.md) | Implemented |
| No committed run artifacts | [`../maintenance/.gitignore`](../maintenance/.gitignore) and stage `.gitkeep` files | Implemented |
| Canonical source and one-way-reference rules | [`../_shared/maintenance-rules.md`](../_shared/maintenance-rules.md) | Implemented |
| Compact form-selection and restructure method | [`../../../refTemplates/smods/icm-architect_fork/SKILL.md`](../../../refTemplates/smods/icm-architect_fork/SKILL.md) | Implemented through the pinned Architect reference |
| Full conventions, example workspaces, and workspace-builder | [`../../../refTemplates/smods/interpretable-context-methodology_fork/README.md`](../../../refTemplates/smods/interpretable-context-methodology_fork/README.md) | Implemented through the pinned methodology companion |
| Layered routing, canonical sources, and one-way dependencies | [`../../../refTemplates/smods/content-agent-routing-promptbase_fork/README.md`](../../../refTemplates/smods/content-agent-routing-promptbase_fork/README.md) | Applied in repository-native catalog/contracts; Promptbase remains a reference input |
| Optional file-backed visual stage mirror and human checkpoint | [`../../../refTemplates/smods/icm-cctv_fork/README.md`](../../../refTemplates/smods/icm-cctv_fork/README.md) | Routed as optional visual review; native Pipeline output remains canonical |
| BLU B160V and free-services envelope | [`../objects/platform/blu-b160v-free-services.md`](../objects/platform/blu-b160v-free-services.md) | Applied as an operator-declared, re-verifiable design constraint; no device access implied |
| Nested workspace artifact classification | [`../objects/knowledge/workspace-artifact-estate.md`](../objects/knowledge/workspace-artifact-estate.md) and [`../processes/workspace-artifact-triage.md`](../processes/workspace-artifact-triage.md) | Implemented without source-code refactoring |

## Form selection

The monorepo uses a composition of two ICM forms. The outer **System map** form makes an existing mixed code-and-documentation repository editable through verified nouns, real movements, and first-order effects. The nested **Pipeline** form governs only future ICM-map maintenance, where inventory, design, verification, and promotion are sequential and human-reviewed.

The other forms are intentionally not scaffolded: this repository is not a single recurring content run (**Pipeline** at the root), a portfolio of independent ICM production lines (**Umbrella**), a growing set of uniform records (**Record library**), a standalone body of domain knowledge (**Knowledge bundle**), or an organization chart (**Context map**). A setup questionnaire is likewise unnecessary because the map is derived from repository sources rather than a user-specific factory configuration. This restraint follows ICM’s “smallest structure that carries the work” rule.

## Selected sources

The System map form and its walk test come from the installed [ICM Architect skill](../../../refTemplates/smods/icm-architect_fork/SKILL.md) and its [`references/system-map.md`](../../../refTemplates/smods/icm-architect_fork/references/system-map.md). The full methodology companion adds the published conventions, example workspaces, and workspace-builder at [`refTemplates/smods/interpretable-context-methodology_fork`](../../../refTemplates/smods/interpretable-context-methodology_fork/). The layered catalog/contract/factory/product distinction is grounded in Architect’s [`references/core.md`](../../../refTemplates/smods/icm-architect_fork/references/core.md), and the maintenance pipeline follows the full methodology’s emphasis on stage contracts, human-editable handoffs, and canonical sources.[1] [2]

> **Deliberate boundary:** The ICM method structures the context and documentation supplied to editors. It does not supersede the monorepo’s runtime architecture, CI, GitHub review, or human authorization rules.

## References

[1]: https://github.com/RinDig/Interpretable-Context-Methodology "RinDig/Interpretable-Context-Methodology"
[2]: https://github.com/RinDig/icm-architect "RinDig/icm-architect"
[3]: https://github.com/RinDig/Content-Agent-Routing-Promptbase "RinDig/Content-Agent-Routing-Promptbase"
[4]: https://github.com/timerloggedout-spec/icm-cctv_fork "timerloggedout-spec/icm-cctv_fork"
