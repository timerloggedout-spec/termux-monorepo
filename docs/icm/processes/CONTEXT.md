# Processes — Monorepo Movements

One job: describe a real movement through the monorepo as explicit input, bounded steps, output, and its actual automated or human-only approval boundary.

## Inputs

- Catalog: [`../CLAUDE.md`](../CLAUDE.md)
- Object library: [`../objects/_index.md`](../objects/_index.md)
- Process template: [`../_templates/process.md`](../_templates/process.md)

## Process

1. Choose an existing documented movement, not an aspirational workflow.
2. Read the linked objects and the governing source before acting.
3. Follow the smallest listed steps; do not infer additional automation authority.
4. Record the automated acceptance evidence and surface only a concrete gate or human-only permission blocker.

## Available movements

| Movement | Open when… | Stop at |
|---|---|---|
| [`change-and-validate.md`](change-and-validate.md) | changing tracked code or documentation | registered scope, automated dual-gate evidence, and explicit human-only permission boundaries |
| [`context-relationship-reconnaissance.md`](context-relationship-reconnaissance.md) | reconstructing related source, PR, issue, comment, label, or file-touch context before nontrivial work | verified evidence and separately marked candidate links |
| [`structured-termux-job.md`](structured-termux-job.md) | running a declared Android/Termux job | the capability and approval boundary |
| [`workspace-artifact-triage.md`](workspace-artifact-triage.md) | classifying nested workspace Markdown, text, JSONL, generated maps, or leftovers | the explicit human-only decision before destructive cleanup or promotion |

## Outputs

- A scoped change plan, validation result, structured device-job outcome, or artifact-classification record.

## Acceptance

Confirm that the movement matches a canonical repository workflow, that its automated checks are recorded, and that any genuinely human-only permission boundary is respected.
