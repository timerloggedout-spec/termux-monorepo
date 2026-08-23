<!-- LinguistProjection: generated; source=docs/icm/objects/governance/CONTEXT.hum.md; mode=machine-grimoire-seed-v1; structural-exceptions=fenced-code,markdown-link-destinations -->

# Governance Objects

One job: route a planned tracked change to the controls that determine whether it may be committed, reviewed, and merged.

## Inputs

- Object index: [`../_index.md`](../_index.md)
- §19§ guidance: [`../../../../§02§.md`](../../../../AGENTS.md)
- Proposal §17§: [`../../../../docs/proposals/§17§.md`](../../../../docs/proposals/PROCESS.md)
- Active work registry: [`../../../../docs/proposals/registry.yaml`](../../../../docs/proposals/registry.yaml)

## §17§

1. Identify the active work item or register one before implementing new scope.
2. §04§ from `master-staging`, not raw `master`.
3. Keep the change focused and cite its item ID in the commit or pull request.
4. Run the required gates, then record any unrelated baseline failures rather than silently repairing outside scope.

## Outputs

- A reviewable feature §04§ with its work item, §1d§ evidence, and known blockers.

## §0e§ check

Confirm the §04§ base, item citation, gate evidence, and absence of destructive history operations before merge.
