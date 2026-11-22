# Enterprise organization preservation — source record

## Primary account notices

GitHub Support email received **2026-11-03**:

- Subject: `[GitHub] Your GitHub Enterprise trial will be deleted in 30 days`
- Enterprise account: `AdAstraNeoNexus`
- Deletion date: **2026-12-03**
- Associated organization named in the notice: `search-astute-ly`

The 2026-10-04 60-day notice independently names the same Enterprise account, organization, and December 3 deletion date. A companion organization-trial notice identifies `search-astute-ly` as an affected organization.

## Live GitHub repository evidence

Organization `search-astute-ly` currently exposes three public repositories with administrator permissions for the connected owner identity:

| Repository | Visibility | Default branch | Size |
|---|---|---|---:|
| `search-astute-ly/termux-monorepo_enterprise` | public | master | 44,297 KB |
| `search-astute-ly/termux-monorepo_enterprise_too` | public | master | 44,297 KB |
| `search-astute-ly/manus-public-ui-research` | public | main | 3 KB |

Both `termux-monorepo_enterprise*` repositories report the same latest commit:

`6567e175ef1b1abe808fb76ca333d2f6ceeaccd8`

That commit was created 2026-08-05. The canonical `timerloggedout-spec/termux-monorepo` HEAD observed on 2026-11-22 is `2d84b7a74aed43d61b8069491014e530779ad869`. GitHub's compare response reports the canonical repository 29,833 commits ahead of the shared snapshot.

## Trial lifecycle evidence

GitHub's Enterprise trial documentation states:

- Organizations transferred into an Enterprise trial revert to their previous plans and settings when the trial expires.
- Organizations created during the trial remain accessible in a downgraded state after expiry, allowing owners to move assets elsewhere.
- Organizations created during an active trial have a removal restriction until Enterprise is purchased.
- Enterprise trial accounts are automatically deleted 90 days after trial expiry when they remain unpaid.

The deletion notice names both the Enterprise account and the associated organization. The preservation plan therefore prepares both direct organization removal, when GitHub exposes it, and repository transfer to a separate Free organization.

## Repository transfer semantics

GitHub documents that repository transfer retains issues, pull requests, wiki, stars, watchers, repository settings, repository webhooks, services, secrets, deploy keys, and Git history. GitHub Pages site URLs retain their original address and require a separate URL and DNS update. Package transfer depends on the package registry. Organization-level resources require separate reconciliation.

## Adjacent organization and personal-account scope

- The Enterprise deletion notice names `search-astute-ly`; the separate `Research-Astute` organization exposes five public repositories.
- `timerloggedout-spec` is the connected personal GitHub identity. The repository's 2026-11-02 integration census records the personal plan as Free and 711 public repositories.
- `AsAstraNeoNexus` is the proposed new organization name. The Enterprise account is `AdAstraNeoNexus`; these are distinct account concepts.

## GitHub documentation

- Enterprise trial lifecycle: https://docs.github.com/en/enterprise-cloud@latest/admin/overview/setting-up-a-trial-of-github-enterprise-cloud
- Removing organizations from an enterprise: https://docs.github.com/en/enterprise-cloud@latest/admin/managing-accounts-and-repositories/managing-organizations-in-your-enterprise/removing-organizations-from-your-enterprise
- Creating a new organization: https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/creating-a-new-organization-from-scratch
- Transferring repositories: https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository
- GitHub plans: https://docs.github.com/en/enterprise-cloud@latest/get-started/learning-about-github/githubs-plans

## Evidence boundary

The repository list, permissions, commit SHAs, and compare relationship are live GitHub evidence. The deletion date and Enterprise-to-organization association are sourced from GitHub Support notifications. The final Free-plan state and asset preservation remain pending until the owner operation and verification workflow complete.
