# Source — master-staging reconciliation

## Operator direction

Reconcile `master-staging` with canonical `master`.

Scope `termux-smoke` to Termux-related operations.

## Implementation interpretation

The live refs have diverged substantially. Reconciliation uses selective extraction from the staging-only commit set and its open PRs. The canonical branch remains the integration target. Each candidate receives an independent current-master branch and a scoped validation set.

The Termux smoke lane validates Android/Termux runtime assumptions, Termux entrypoints, device-facing integrations, and Termux operational flows. General repository hygiene belongs to `repo-gate`. Bucket-headroom, provider, and other domain contracts run in their own workflows.

## Acceptance

- Preserve the staging branch and all open PR source branches.
- Keep `master` as canonical integration.
- Record exact source and destination SHAs for each extraction.
- Validate each extracted workstream against its own acceptance criteria.
- Apply `termux-smoke` only when the changed workstream is Termux-related.
