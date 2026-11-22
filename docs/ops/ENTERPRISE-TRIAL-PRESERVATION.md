# GitHub Enterprise trial preservation runbook

**Priority:** P0  
**Deadline:** 2026-12-03  
**Enterprise:** `AdAstraNeoNexus`  
**Organization:** `search-astute-ly`  
**Canonical hub:** `timerloggedout-spec/termux-monorepo`

## Decision

Preserve the existing `search-astute-ly` organization by removing it from the expiring Enterprise account. GitHub documents that removing an organization makes it stand alone and automatically downgrades it to GitHub Free.

This preserves the existing organization login and repository URLs. A separate `AsAstraNeoNexus` organization is optional and is not required for this preservation operation.

## Verified inventory

| Repository | Visibility | Default branch | Notes |
|---|---|---|---|
| `termux-monorepo_enterprise` | public | master | Historical monorepo snapshot |
| `termux-monorepo_enterprise_too` | public | master | Byte-size and HEAD-identical sibling snapshot |
| `manus-public-ui-research` | public | main | Separate research repository |

Both monorepo snapshots share HEAD `6567e175ef1b1abe808fb76ca333d2f6ceeaccd8`. The canonical personal-account repository has advanced 29,833 commits beyond that ancestor. Keep the snapshots as historical records and retain `timerloggedout-spec/termux-monorepo` as the active source.

The adjacent `Research-Astute` organization has five public repositories and is outside the organization named in the Enterprise deletion notice. The connected personal account is recorded as Free in the 2026-11-02 integration census.

## Owner operation

1. Sign in as an Enterprise owner.
2. Open [AdAstraNeoNexus Enterprise settings](https://github.com/enterprises/adastraneonexus/settings/organizations).
3. Open **Organizations**.
4. Locate `search-astute-ly`.
5. Open the row's **…** menu.
6. Select **Remove organization**.
7. Review GitHub's downgrade summary and confirm the removal.

GitHub documents that the organization becomes independent and moves to GitHub Free. Internal repositories convert to private. Protected-branch and ruleset settings remain stored but cease to be enforced on private repositories. Secrets remain stored and private-repository access to them requires GitHub Team.

The live inventory shows all three affected repositories as public, so the documented public-repository feature tier remains applicable.

## Baseline and verification

The read-only workflow is `.github/workflows/enterprise-org-detachment-verify.yml`.

1. Run the workflow with `phase=baseline` and `org_slug=search-astute-ly` before the owner operation.
2. Record the Actions run ID. The workflow publishes the metadata-only artifact `enterprise-org-state`.
3. Complete the owner operation.
4. Run the workflow with `phase=verify`, the same organization slug, and the baseline run ID.
5. Review the comparison and retain the final artifact.

The verifier checks:

- Organization ID and Free plan.
- Repository IDs, visibility, default branches, Pages flags, and archive state.
- Branch names, tag names, release IDs, and workflow IDs.
- Organization Actions secret names and variable names.
- Organization webhooks and GitHub App installation identities.
- Expected presence of all three repositories.

The artifact records metadata only. Secret values, token values, webhook URLs, and private key material stay outside the report. Unavailable API surfaces are classified as unverified and require owner review.

## Free-plan compliance

GitHub Free for organizations supports unlimited public repositories with the full public-repository feature set and unlimited private repositories with a limited feature set. Keep the three inventoried repositories public unless a separate privacy decision requires a private repository and its associated feature review.

Source: https://docs.github.com/en/enterprise-cloud@latest/get-started/learning-about-github/githubs-plans

## Enterprise trial constraints

GitHub's removal procedure is unavailable for Enterprise Managed Users and GitHub Enterprise Cloud with data residency. The connected owner identity is a standard GitHub.com personal account; confirm the Enterprise settings page exposes **Remove organization**. If the option is unavailable, route the case to GitHub Support before the deletion date.

Keep the Enterprise account available until the Free-plan verification and asset reconciliation pass. The Enterprise account can then complete its trial cleanup while the standalone organization remains.

## Repository provisioning workflow

The existing `.github/workflows/repository-provisioner.yml` creates repositories under `timerloggedout-spec` through `POST /user/repos` and verifies that owner identity. It does not create organizations. GitHub organization creation remains an owner settings operation. An organization-target repository-provisioning extension can follow after the destination organization decision; it is separate from the current preservation path.
