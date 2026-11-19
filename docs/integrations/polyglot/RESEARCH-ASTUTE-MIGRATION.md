# Research Astute organizational migration readiness

**State:** future intention; Termux Monorepo remains initial maintainer and source of truth.

## Migration gate

Transfer repositories after an explicit organizational decision and an approved rehearsal. This document records preparation work and establishes the readiness checklist; repository ownership remains with the current organization until the authorized cutover.

## Inventory checklist

- [ ] Confirm Research Astute organization ownership, governance and billing authority.
- [ ] Confirm repository names, visibility, licensing and canonical URL strategy.
- [ ] Inventory maintainers, teams, outside collaborators and least-privilege permissions.
- [ ] Recreate branch protections, rulesets, required checks and CODEOWNERS behavior.
- [ ] Inventory Actions secrets, variables, environments and OIDC trust relationships.
- [ ] Inventory GitHub Apps, webhooks, deploy keys, PAT use and external integrations.
- [ ] Inventory Pages, custom domains, deployment targets and package/container registries.
- [ ] Preserve issues, pull requests, discussions, releases, tags, wiki and project references.
- [ ] Verify contributor provenance, security policy, vulnerability reporting and license notices.
- [ ] Test cross-repository PolyGlot feeds, immutable revisions and digest validation after transfer.
- [ ] Update canonical repository references and consumer configuration.
- [ ] Prepare rollback, redirect and communication plans.

## Rehearsal acceptance

A rehearsal succeeds when CI, permissions, publication, external integrations, feed consumers and release workflows operate under the destination organization with recorded evidence. The source repository remains authoritative until the authorized cutover is complete.

## Cutover record

Record approver, date, source and destination repository IDs, transfer plan revision, validation results, unresolved exceptions and rollback owner.
