# Change-Impact Index

One job: answer **which cards should I open before changing X**. This index is intentionally short; cards and their cited sources own the details.

| Planned change | Open first | Then verify |
|---|---|---|
| Android/Termux capability, adapter, job schema, or device boundary | [`../objects/platform/termux-agentic-hub.md`](../objects/platform/termux-agentic-hub.md) and [`../processes/structured-termux-job.md`](../processes/structured-termux-job.md) | capability tier, validation, redaction, and exclusion boundary |
| ArchWiz cockpit, forensic, autonomous, verification, or knowledge tool | [`../objects/operations/archwiz.md`](../objects/operations/archwiz.md) | the named tool’s source and direct probe/test surface |
| Root README, route, catalog, or index behavior | [`../objects/knowledge/navigation-and-indexes.md`](../objects/knowledge/navigation-and-indexes.md) | the owning authored source or generator; do not hand-edit generated maps |
| Tracked code, document, submodule, or workflow change | [`../objects/governance/change-control.md`](../objects/governance/change-control.md) and [`../processes/change-and-validate.md`](../processes/change-and-validate.md) | work item, feature-branch base, required gates, and review status |
| ICM map card, route, template, or maintenance-rule change | [`../maintenance/CLAUDE.md`](../maintenance/CLAUDE.md) | the `02_design` human gate, then map-specific verification |
| ICM form selection, reference-workspace design, or methodology-fork update | [`../objects/knowledge/interpretable-context-methodology.md`](../objects/knowledge/interpretable-context-methodology.md) | the smallest form, reference rule, and custom-submodule review |
| Nested `workspace/` artifact, generated map, text index, or JSONL request | [`../processes/workspace-artifact-triage.md`](../processes/workspace-artifact-triage.md) | classification and a human decision before cleanup or promotion |

## Human check

Before expanding scope, verify that the cited object/process has a direct source-level connection to the planned change. If it does not, record the new relationship in a card rather than assuming a broad dependency.
