# Knowledge Objects

One job: route orientation, documentation, and index questions to the owning navigation or generated-map source.

## Inputs

- Object index: [`../_index.md`](../_index.md)
- Root navigation: [`../../../../README.md`](../../../../README.md)
- Map contract: [`../../CONTEXT.md`](../../CONTEXT.md)

## Process

1. Determine whether the request changes root routing, an authored index, or a generated map.
2. Read the Navigation and Indexes card.
3. Update only the source that owns the fact; link from other catalogs instead of copying payload.

## Outputs

- A targeted navigation or index change with its owning source identified.

## Human check

Confirm that no generated index has been hand-edited and that the new route points to a maintained source.
