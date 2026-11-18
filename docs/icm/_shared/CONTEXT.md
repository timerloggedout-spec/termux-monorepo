# ICM Map Maintenance References

One job: hold stable rules and blank starters used by the `maintenance/` pipeline. This shelf is the factory; it is not a stage output and should not accumulate per-update decisions.

## Inputs

- Root map contract: [`../CONTEXT.md`](../CONTEXT.md)
- Maintenance pipeline: [`../maintenance/CONTEXT.md`](../maintenance/CONTEXT.md)
- Repository operating contract: [`../../../../CLAUDE.md`](../../../../CLAUDE.md)

## Contents

| File | Use |
|---|---|
| [`maintenance-rules.md`](maintenance-rules.md) | Scope, canonical-source, one-way-reference, FA-ADE execution, and human-only permission boundaries. |
| [`source-inventory-template.md`](source-inventory-template.md) | Blank inventory copied into `01_inventory/output/` for each update. |
| [`verification-checklist.md`](verification-checklist.md) | Deterministic structure, source, scope, and repository-gate checks used in `03_verify`. |

## Maintenance

Edit this shelf only when a rule or blank template should apply to future maintenance runs. Put run-specific evidence and decisions in a stage `output/` file. Normal factory edits proceed through the authorized proposal and repository validation flow; no separate human approval ritual is added by ICM.
