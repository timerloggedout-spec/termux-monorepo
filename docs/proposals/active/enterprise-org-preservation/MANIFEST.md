# Enterprise organization preservation — manifest

**ID:** enterprise-org-preservation  
**Status:** executing  
**Priority:** P0  
**Owner:** ChatGPT — migration verification and documentation  
**Operator authorization:** accepted for the preservation scope  
**Deadline:** 2026-12-03  
**Source organization:** `search-astute-ly`  
**Enterprise account:** `AdAstraNeoNexus`  
**Proposed Free destination:** `AsAstraNeoNexus`

## Objective

Preserve the repositories and associated operational assets owned by `search-astute-ly` before the `AdAstraNeoNexus` Enterprise trial deletion date.

The preferred outcome is to retain `search-astute-ly` as an independent Free organization if GitHub exposes the owner-level Remove organization operation. GitHub's trial documentation also describes trial-created organizations that remain in a downgraded state and can move assets elsewhere. The fallback destination is a new standalone GitHub Free organization named `AsAstraNeoNexus`, created from personal-account settings outside the expiring Enterprise account.

## Chosen preservation paths

1. **Detach path:** remove `search-astute-ly` from Enterprise when GitHub permits the operation; verify the same organization ID on GitHub Free.
2. **Transfer path:** create `AsAstraNeoNexus` on GitHub Free from personal-account settings; transfer every repository from `search-astute-ly`; recreate organization-level integrations and access controls; verify repository IDs and metadata in the destination.

The transfer path preserves repository contents, issues, pull requests, wikis, stars, watchers, settings, repository webhooks, secrets, deploy keys, and Git history. Package associations depend on the package registry. Organization-level teams, membership, secrets, variables, webhooks, and GitHub App installations require separate reconciliation.

## Scope

- Confirm the Enterprise deletion notice and affected organization.
- Capture a metadata-only baseline for `search-astute-ly`.
- Verify whether the Enterprise owner UI permits direct organization removal.
- Provide a safe, dry-run-first repository transfer workflow for the Free destination.
- Extend repository provisioning to create repositories under an authorized Free organization.
- Reconcile organization-level integrations and access controls.
- Preserve both historical `termux-monorepo_enterprise*` snapshots and `manus-public-ui-research`.
- Keep `Research-Astute` and the personal `timerloggedout-spec` account outside this migration scope.

## Human-only edges

- Create `AsAstraNeoNexus` from personal-account Settings → Organizations → New organization → Choose GitHub Free. Enterprise settings are excluded from this creation path.
- Confirm the organization slug is available and the new organization reports the Free plan.
- Complete any Enterprise settings operation that GitHub exposes to the Enterprise owner.

## Acceptance

- [x] GitHub Support notice identifies `AdAstraNeoNexus`, `search-astute-ly`, and 2026-12-03.
- [x] Live repository inventory identifies all three affected repositories.
- [x] The two enterprise monorepo snapshots are confirmed to share the same HEAD SHA.
- [x] A read-only baseline/verification workflow and regression tests are implemented.
- [x] A dry-run-first repository transfer workflow is implemented with exact apply confirmation.
- [x] Repository provisioning supports authorized GitHub Free organization owners.
- [ ] Confirm the available Enterprise organization-removal path.
- [ ] Establish an independent Free destination if transfer is required.
- [ ] Transfer all source repositories and verify stable repository IDs.
- [ ] Reconcile organization-level teams, membership, secrets, variables, webhooks, apps, projects, and packages.
- [ ] Verify the destination organization and repository feature posture on GitHub Free.
- [ ] Record final evidence before 2026-12-03.

## Review log

| Date | Actor | Event | Evidence |
|---|---|---|---|
| 2026-11-22 | ChatGPT | Confirmed deadline and affected organization | GitHub Support emails received 2026-11-03 and 2026-10-04 |
| 2026-11-22 | ChatGPT | Live repository inventory | GitHub repository search and commit comparison |
| 2026-11-22 | ChatGPT | Confirmed trial lifecycle and transfer semantics | GitHub Enterprise trial and repository transfer documentation |


## Implementation PRs

- PR #5873: organization-aware repository provisioning and Enterprise preservation workflows.
- PR #5874: remove tracked source session artifacts and add ignore rules; historical remediation remains a separate controlled step.
