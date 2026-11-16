# Change-Impact Index

One job: answer **which cards should I open before changing X**. This index is intentionally short; cards and their cited sources own the details.

| Planned change | Open first | Then verify |
|---|---|---|
| Android/Termux capability, adapter, job schema, or device boundary | [`../objects/platform/termux-agentic-hub.md`](../objects/platform/termux-agentic-hub.md) and [`../processes/structured-termux-job.md`](../processes/structured-termux-job.md) | capability tier, validation, redaction, and exclusion boundary |
| Device availability, service tier, or execution-host assumption | [`../objects/platform/blu-b160v-free-services.md`](../objects/platform/blu-b160v-free-services.md) | declared envelope and required re-verification; no device access is implied |
| ArchWiz cockpit, forensic, autonomous, verification, or knowledge tool | [`../objects/operations/archwiz.md`](../objects/operations/archwiz.md) | the named tool’s source and direct probe/test surface |
| Static root catalog aliases or index behavior | [`../objects/knowledge/navigation-and-indexes.md`](../objects/knowledge/navigation-and-indexes.md) | the owning authored source or generator; preserve static alias identity |
| Contextual source/GitHub-history reconstruction, relationship-index schema, collector, query, or publisher change | [`../objects/knowledge/context-relationship-index.md`](../objects/knowledge/context-relationship-index.md) and [`../processes/context-relationship-reconnaissance.md`](../processes/context-relationship-reconnaissance.md) | exact root, evidence/provenance, verified-versus-candidate boundary, exclusions, and trusted workflow scope |
| Nested provider-routing evidence, observation, or polling proposal | [`../objects/knowledge/provider-routing.md`](../objects/knowledge/provider-routing.md) and [`../routing.md`](../routing.md) | canonical runtime source, approved observation lifecycle, and the separate post-ICM code/workflow gate |
| Tracked code, document, submodule, or workflow change | [`../objects/governance/change-control.md`](../objects/governance/change-control.md) and [`../processes/change-and-validate.md`](../processes/change-and-validate.md) | work item, feature-branch base, required gates, and review status |
| ICM map card, route, template, or maintenance-rule change | [`../maintenance/CLAUDE.md`](../maintenance/CLAUDE.md) | the `02_design` human gate, then map-specific verification |
| ICM form selection, reference-workspace design, or methodology-fork update | [`../objects/knowledge/interpretable-context-methodology.md`](../objects/knowledge/interpretable-context-methodology.md) | the smallest form, reference rule, and custom-submodule review |
| Any pinned ICM reference selection or update | [`../objects/knowledge/reference-inputs.md`](../objects/knowledge/reference-inputs.md) | reference-only boundary and reviewed Gitlink update |
| Initiated CCTV card, visual stage mirror, human checkpoint, or mobile-static publication proposal | [`../objects/operations/optional-visual-review.md`](../objects/operations/optional-visual-review.md) and [`../_tv/README.md`](../_tv/README.md) | canonical source artifact, response cage, human approval, and the separate renderer/publication gate |
| Nested `workspace/` artifact, generated map, text index, or JSONL request | [`../processes/workspace-artifact-triage.md`](../processes/workspace-artifact-triage.md) | classification and a human decision before cleanup or promotion |

## Human check

Before expanding scope, verify that the cited object/process has a direct source-level connection to the planned change. If it does not, record the new relationship in a card rather than assuming a broad dependency.
