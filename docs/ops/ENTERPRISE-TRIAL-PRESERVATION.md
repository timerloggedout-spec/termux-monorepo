# GitHub Enterprise trial preservation runbook

**Priority:** P0  
**Deadline:** 2026-12-03  
**Enterprise:** `AdAstraNeoNexus`  
**Source organization:** `search-astute-ly`  
**Proposed Free destination:** `AsAstraNeoNexus`  
**Canonical hub:** `timerloggedout-spec/termux-monorepo`

## Decision

Preserve the assets owned by `search-astute-ly` before the Enterprise account and associated organization reach the December 3 deletion date.

The first decision gate is the Enterprise owner settings page. GitHub supports removing an organization from an enterprise, which makes it independent and downgrades it to GitHub Free. GitHub's trial documentation also describes organizations created during the trial that remain in a downgraded state and can move assets elsewhere. The owner settings page determines whether direct removal is available for this organization.

When GitHub permits direct removal, retain the existing `search-astute-ly` identity. When the trial-created organization removal restriction applies, create a separate Free organization and transfer all repositories.

## Verified source inventory

| Repository | Visibility | Default branch | Notes |
|---|---|---|---|
| `termux-monorepo_enterprise` | public | master | Historical monorepo snapshot |
| `termux-monorepo_enterprise_too` | public | master | Same size and HEAD as sibling snapshot |
| `manus-public-ui-research` | public | main | Separate research repository |

Both monorepo snapshots share HEAD `6567e175ef1b1abe808fb76ca333d2f6ceeaccd8`. The canonical `timerloggedout-spec/termux-monorepo` has advanced 29,833 commits beyond that ancestor. Preserve both snapshots as historical records and retain the personal-account monorepo as the active source.

The adjacent `Research-Astute` organization has five public repositories and is outside the organization named in the Enterprise deletion notice. The connected personal account is recorded as Free in the 2026-11-02 integration census.

## Path A — preserve the existing organization

1. Open [AdAstraNeoNexus Enterprise organization settings](https://github.com/enterprises/adastraneonexus/settings/organizations).
2. Open **Organizations** and locate `search-astute-ly`.
3. Inspect the row's **…** menu.
4. When **Remove organization** is available, review the warnings and complete the owner operation.
5. Run the verifier with `phase=verify`, `mode=detached`, and the baseline run ID.
6. Confirm the same organization ID, Free plan, and preserved asset inventory.

GitHub's removal documentation states that the organization becomes independent and moves to GitHub Free. Internal repositories convert to private. Protected-branch and ruleset configurations remain stored but cease to be enforced in private repositories. Secrets remain stored; private-repository access to them requires GitHub Team.

## Path B — transfer repositories to a new Free organization

### Create the destination

Create `AsAstraNeoNexus` from the personal GitHub account:

1. Open [GitHub organization settings](https://github.com/settings/organizations).
2. Select **New organization**.
3. Select **Choose GitHub Free**.
4. Enter `AsAstraNeoNexus` as the organization name.
5. Complete creation from personal-account settings, outside the Enterprise account.
6. Confirm the new organization appears under personal-account Organizations and reports the Free plan.

GitHub confirms name availability during creation. The proposed slug is `asastraneonexus`.

### Transfer repositories

1. Run the baseline workflow for `search-astute-ly` and retain the run ID.
2. Run `.github/workflows/enterprise-org-repository-transfer.yml` in `dry_run` mode.
3. Review the source repository count, destination owner, and collision checks.
4. Run in `apply` mode with the exact confirmation string displayed by the dry run.
5. Wait for each GitHub transfer to reach the destination and verify the original repository ID.
6. Run the preservation verifier with `mode=transferred` and the baseline run ID.
7. Recreate organization-level resources from the baseline inventory.

GitHub repository transfers preserve issues, pull requests, wikis, stars, watchers, settings, repository webhooks, services, secrets, deploy keys, and Git history. GitHub Pages site URLs do not redirect. Package associations depend on the registry. The original owner becomes a collaborator, and existing collaborators remain.

Organization-level teams, membership, secrets, variables, webhooks, GitHub App installations, projects, and package ownership require separate reconciliation. The baseline workflow records metadata and names; secret values remain write-only and require their original source or operator re-entry.

## Baseline and verification workflow

The read-only workflow is `.github/workflows/enterprise-org-detachment-verify.yml`.

1. Run with `phase=baseline` and `org_slug=search-astute-ly` before either preservation path.
2. Record the Actions run ID. The workflow publishes the metadata-only artifact `enterprise-org-state`.
3. For direct removal, verify `search-astute-ly` with `mode=detached`.
4. For repository transfer, verify `AsAstraNeoNexus` with `mode=transferred`.
5. Review missing assets and all unverified API surfaces.

The artifact records repository IDs, branches, tags, releases, Actions workflows, repository-level secret and variable names, repository hooks, environments, deployments, organization-level secret and variable names, organization webhooks, and GitHub App installations. Secret values, token values, webhook URLs, and private key material stay outside the report.

## Free-plan compliance

GitHub Free for organizations supports unlimited public repositories with the full public-repository feature set and unlimited private repositories with a limited feature set. The three inventoried source repositories are public. Keep them public unless a separate privacy decision requires private repositories and their associated feature review.

Source: https://docs.github.com/en/enterprise-cloud@latest/get-started/learning-about-github/githubs-plans

## Repository provisioning workflow

The existing `.github/workflows/repository-provisioner.yml` creates repositories under `timerloggedout-spec` through `POST /user/repos`. This proposal extends it with an organization target that requires owner membership and a Free-plan check, using `POST /orgs/{org}/repos`. Organization creation itself remains a personal-account settings operation.

Keep the Enterprise account available until the selected preservation path and its verification pass. Complete the work before 2026-12-03.
