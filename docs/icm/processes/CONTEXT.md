# Processes — Monorepo Movements

One job: describe a real movement through the monorepo as explicit input, bounded steps, output, and human review.

## Inputs

- Catalog: [`../CLAUDE.md`](../CLAUDE.md)
- Object library: [`../objects/_index.md`](../objects/_index.md)
- Process template: [`../_templates/process.md`](../_templates/process.md)

## Process

1. Choose an existing documented movement, not an aspirational workflow.
2. Read the linked objects and the governing source before acting.
3. Follow the smallest listed steps; do not infer additional automation authority.
4. Record the human check and surface any gate or approval blocker.

## Available movements

| Movement | Open when… | Stop at |
|---|---|---|
| [`change-and-validate.md`](change-and-validate.md) | changing tracked code or documentation | the governing validation and human gate |
| [`structured-termux-job.md`](structured-termux-job.md) | running a declared Android/Termux job | the capability and approval boundary |
| [`workspace-artifact-triage.md`](workspace-artifact-triage.md) | classifying nested workspace Markdown, text, JSONL, generated maps, or leftovers | the human decision before cleanup or promotion |

## Outputs

- A scoped change plan, validation result, structured device-job outcome, or artifact-classification record.

## Human check

Confirm that the proposed movement is one that the repository actually documents and that any required approval tier is satisfied.
