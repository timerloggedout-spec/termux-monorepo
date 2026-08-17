# Knowledge Objects

One job: route orientation, documentation, and index questions to the owning navigation or generated-map source.

## Inputs

- Object index: [`../_index.md`](../_index.md)
- Root navigation: [`../../../../README.md`](../../../../README.md)
- Map contract: [`../../CONTEXT.md`](../../CONTEXT.md)

## Process

1. Determine whether the request changes root routing, an authored index, a generated map, or mixed `workspace/` artifacts.
2. Read the Navigation and Indexes card for static catalog routing, the Provider Routing Governance card for the nested provider evidence resource, the ICM Reference Inputs card for a pinned external reference, the Interpretable Context Methodology Reference for recurring-workspace design, or the Workspace Artifact Estate card for a nested workspace request.
3. Classify workspace material before loading it: catalog/contract, factory, product, leftover, or excluded.
4. Keep external reference material in its pinned Gitlink; update repository-native ICM contracts instead of copying reference payload.
5. Update only the source that owns the fact; link from other catalogs instead of copying payload.

## Outputs

- A targeted navigation, nested routing-resource, or index change with its owning source identified.

## Human check

Confirm that no generated index has been hand-edited, no excluded runtime material has been loaded, and that the new route points to a maintained source.
