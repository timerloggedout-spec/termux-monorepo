# Enterprise organization preservation — manifest

**ID:** enterprise-org-preservation  
**Status:** executing  
**Priority:** P0  
**Owner:** ChatGPT — migration verification and documentation  
**Operator authorization:** accepted for the preservation scope  
**Deadline:** 2026-12-03  
**Affected organization:** `search-astute-ly`  
**Enterprise account:** `AdAstraNeoNexus`

## Objective

Preserve the existing `search-astute-ly` organization as an independent GitHub Free organization before the `AdAstraNeoNexus` Enterprise trial deletion date. Preserve its organization identity, repository IDs, Git refs, releases, Actions surfaces, secrets metadata, variables metadata, webhooks, and GitHub App installations.

## Chosen preservation path

Use GitHub's **Remove organization** operation from Enterprise settings. GitHub documents that this operation makes the organization stand alone and downgrades it to GitHub Free. The operation preserves repositories and settings while changing Enterprise-governed policy and billing.

The current repository inventory contains three public repositories. Their public visibility keeps them within the full-featured public-repository tier of GitHub Free for organizations.

## Scope

- Confirm the Enterprise deletion notice and affected organization.
- Capture a metadata-only baseline for `search-astute-ly`.
- Provide a read-only Actions workflow for baseline capture and post-detachment comparison.
- Document the owner-only Enterprise settings operation.
- Verify the organization plan is Free and its baseline assets remain present.
- Keep `Research-Astute` and the personal `timerloggedout-spec` account outside this migration scope.
- Preserve both historical `termux-monorepo_enterprise*` snapshots.

## Human-only edge

An Enterprise owner performs the **Remove organization** action in GitHub Enterprise settings. The current GitHub connector exposes repository and organization-repository administration, while Enterprise organization removal is a GitHub settings operation. The verifier records evidence after the owner action.

## Acceptance

- [x] GitHub Support notice identifies `AdAstraNeoNexus`, `search-astute-ly`, and 2026-12-03.
- [x] Live repository inventory identifies all three affected repositories.
- [x] The two enterprise monorepo snapshots are confirmed to share the same HEAD SHA.
- [x] A read-only baseline/verification workflow and regression tests are implemented.
- [ ] Owner removes `search-astute-ly` from the Enterprise account.
- [ ] Post-detachment workflow reports `plan=free`.
- [ ] Organization ID, repository IDs, branches, tags, releases, workflows, secret names, variable names, webhooks, and app installations reconcile against the baseline.
- [ ] Final evidence is recorded and the proposal is closed.

## Review log

| Date | Actor | Event | Evidence |
|---|---|---|---|
| 2026-11-22 | ChatGPT | Confirmed deadline and affected organization | GitHub Support email received 2026-11-03; companion runbook |
| 2026-11-22 | ChatGPT | Live repository inventory | GitHub repository search and commit comparison |
