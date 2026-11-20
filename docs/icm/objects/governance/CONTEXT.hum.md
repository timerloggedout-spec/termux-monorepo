# Governance Objects

One job: route a planned tracked change to the controls that determine whether it may be committed, reviewed, and merged.

## Inputs

- Object index: [`../_index.md`](../_index.md)
- Repository guidance: [`../../../../AGENTS.md`](../../../../AGENTS.md)
- Proposal process: [`../../../../docs/proposals/PROCESS.md`](../../../../docs/proposals/PROCESS.md)
- Active work registry: [`../../../../docs/proposals/registry.yaml`](../../../../docs/proposals/registry.yaml)

## Process

1. Identify the active work item or register one before implementing new scope.
2. Branch from `master-staging`, not raw `master`.
3. Keep the change focused and cite its item ID in the commit or pull request.
4. Run the required gates, then record any unrelated baseline failures rather than silently repairing outside scope.

## Outputs

- A reviewable feature branch with its work item, validation evidence, and known blockers.

## Human check

Confirm the branch base, item citation, gate evidence, and absence of destructive history operations before merge.
