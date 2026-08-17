# Operations Objects

One job: route a change touching monorepo operational tooling to the smallest canonical tool or procedure source.

## Inputs

- Object index: [`../_index.md`](../_index.md)
- Canonical tool catalog: [`../../../../archwiz/TOOL_INDEX.md`](../../../../archwiz/TOOL_INDEX.md)
- Change control: [`../governance/change-control.md`](../governance/change-control.md)

## Process

1. Read the ArchWiz card for tool-surface work, or the Optional Visual Review card for a proposed file-backed visual checkpoint.
2. Open the cited tool source or its governing procedure before editing.
3. Preserve the distinction between cockpit, forensic, autonomous, verification, knowledge, and optional visual-review work.

## Available operational objects

| Object | Open when… | Stop at |
|---|---|---|
| [`archwiz.md`](archwiz.md) | changing the cockpit, forensic, autonomous, verification, or knowledge tool surface | the named tool’s source and probe/test boundary |
| [`optional-visual-review.md`](optional-visual-review.md) | proposing a file-backed stage mirror or human visual checkpoint | the declared stage output and the human approval boundary |

## Outputs

- A scoped tool change plan with its direct validation surface.

## Human check

Confirm that the change stays in the requested tool category, retains a direct validation path, and does not turn an optional visual reference into a required runtime service.
