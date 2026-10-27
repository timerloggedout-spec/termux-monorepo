# Devin Wiki Access Reconciliation

**Status:** Implemented under `AR-13` as an autonomous, token-scoped control plane. The source of truth is [`.github/workflows/reconcile-devin-wiki-access.yml`](../../.github/workflows/reconcile-devin-wiki-access.yml); its reconciler is [`scripts/agentic/reconcile_devin_wiki_access.py`](../../scripts/agentic/reconcile_devin_wiki_access.py). Branch indexing for this repository is handled by the companion controller [`scripts/agentic/devin_wiki_indexing.py`](../../scripts/agentic/devin_wiki_indexing.py) in the same workflow (see "Branch indexing" below).

## Purpose

The repository-surface reconciler already discovers repositories reachable by the established operator-token lane and manages the local GitHub Wiki publisher. This companion controller uses the *same credential-scoped inventory* to reconcile **GitHub App access for the official `devin-ai-integration` App**. When that App is installed with **selected repositories**, a newly accessible repository can be assigned to the existing installation through GitHub’s documented API. When the App is installed with **all repositories**, future repositories are already covered by the provider configuration.[1] [2]

This controller does not grant provider permissions that the existing GitHub App did not request; it does not create a GitHub App, an App private key, an API key, a provider session, or a browser login. It relies exclusively on an existing operator PAT that GitHub accepts for the documented assignment endpoint.

## Multi-Wiki scope

| Surface | Automation responsibility | Freshness and authority boundary |
|---|---|---|
| In-repository `wiki/` Markdown | Normal pull-request review and managed GitHub Wiki publication. | Repository source and review evidence are canonical. |
| GitHub Wiki | Published from reviewed `wiki/` content by `Publish wiki`. | A change to `wiki/**` on the default branch triggers publication. |
| Devin Wiki | Provider-managed indexing becomes eligible after the existing Devin GitHub App covers a repository. Root `.devin/wiki.json` can steer page generation. For this repository, branch indexing is invoked explicitly through Devin's documented v3 indexing endpoint by the companion controller. | Provider output remains discovery material and requires source corroboration. |
| Public DeepWiki | Provider-managed public discovery surface for indexed repositories. | The public surface remains provider-managed and separate from the organization indexing endpoint; indexed source refs and timestamps must be validated before use. |

The root README retains links to the GitHub Wiki, public DeepWiki, and Devin Wiki. The three destinations are intentionally complementary rather than mirrors of authority.

## Operating model

| Stage | Trigger | Credential lane | Result | Mutation boundary |
|---|---|---|---|---|
| Access discovery | Daily schedule at `05:41 UTC` or manual dispatch with `apply=false` | Existing operator-token precedence | Redacted counts for `current`, `missing`, `not_configured`, `excluded`, or `blocked` state. | Read-only |
| Selected-repository assignment | Daily schedule or manual dispatch with `apply=true` | Existing **classic PAT with `repo` scope** | Missing eligible repositories are assigned to the existing Devin App installation. | GitHub App repository-access list only |
| Devin Wiki generation | Provider-managed after access is available | Devin service | Provider-generated Wiki can read `.devin/wiki.json` during generation. | Provider-managed |
| Branch indexing — active set | Daily schedule (`first-pass` scope, account-wide) and manual dispatch | Devin service-user token (see below) | For every accessible repository, the default branch + open PR head branches are (re-)indexed through the documented v3 endpoint; per-branch status is recorded from the response. | Devin organization indexing only; additive |
| Branch indexing — new branch | Branch-created (`create`) event, dedicated job | Devin service-user token | The created branch is indexed once. | Devin organization indexing only; additive |
| Branch indexing — bulk backfill | Manual dispatch only, `index=all` (this repo or account-wide) | Devin service-user token | Every current branch of every in-scope repository is indexed in chunks of 50 per repository. | Gated: refused at non-low effort without the per-run approval input |
| Public DeepWiki indexing and refresh | Provider-managed | DeepWiki service | Public indexed pages may become available according to provider behavior. | No undocumented endpoint or browser flow is used |

The scheduled controller is autonomous: it does not wait for a human comment, browser handoff, or provider UI checkbox. The access reconciler performs only the documented GitHub App repository-assignment call; the companion indexer performs only the documented Devin v3 indexing call, subject to the provisioning and cost gates above. Both produce redacted summary artifacts. Detailed inventories are created only on the ephemeral runner and deleted before artifact upload.

## Branch indexing (Devin v3 API)

The companion controller calls Devin's documented indexing endpoint — `PUT https://api.devin.ai/v3/organizations/{org_id}/repositories/{repository_path}/indexing` with body `{"branch_names": [...]}` — which is idempotent and returns `indexing_status.latest_indexes` (latest job status, commit, and job ID per branch). The run records those per-branch results in its detail report and uploads only a redacted summary (counts, scope, effort, projected ACUs). Indexing is additive only: no branch index is ever removed by this automation.

**Refresh model.** Devin's docs do not state that indexed branch contents refresh automatically on later pushes, and each indexing job is pinned to a commit. Freshness is therefore maintained by re-invoking the idempotent endpoint: the daily run re-indexes the active set, the branch-created job indexes each new branch once, and the bulk backfill is a manual dispatch. A per-push trigger was rejected: this repository's push volume would re-index far more often than branch heads materially change, and the daily pass bounds staleness to one day for active branches.

**Scopes.** `first-pass` = the default branch plus the head branches of open pull requests from the repository (the active set). `single` = one named branch of one repository. `all` = every branch currently in GitHub, including historical and `backup/*` branches, sent in chunks of 50 per repository.

**Account scope (owner policy: all branches, all repositories, full use of the free offerings).** With `--all-repos` (workflow input `index_repos=all-repos`; the daily schedule always runs account-wide), the target set is the access reconciler's credential-scoped inventory — every repository the operator token can reach (owner, organization-member, collaborator), archived repositories skipped. Branch selection runs for the whole account before the first Devin call, so the counted cost gate sees true totals; a failure in one repository is recorded and never stops the others. The account summary artifact carries counts only (repository names stay out, as the inventory can include private repositories). At the low effort level — the free offering — account-wide runs need no approval at any branch count. At medium/high, account-wide runs of any branch scope are refused without the per-run approval, with the projected ACU range printed. New branches in other repositories are picked up by the daily account pass or a backfill dispatch; the branch-created job exists only in this repository, because the workflow file lives here.

**Cost gate.** Wiki generation runs at an org effort level (configurable per org, overridable per repo, from the wiki page): low is free, medium is ~5–10 ACUs per wiki, high is ~20–40 ACUs per wiki. The indexer refuses to run until the observed level is recorded in the `DEVIN_WIKI_EFFORT` variable, and refuses a bulk `all` run — or any account-wide run — at medium/high unless the dispatch's `approve_nonlow_effort` input is set. Projections use the selected branch count: at the 2026-10-27 live count of 1,726 branches, a bulk run projects ~8,630–17,260 ACUs at medium and ~34,520–69,040 ACUs at high; the active set (82 branches that day) projects ~410–820 ACUs at medium.

**Provisioning (owner step, names only).** One Devin UI pass supplies everything: in Devin Settings → Devin API, create a service user and generate its API token with the org-level `IndexOrgRepositories` permission (or org `Read` plus `repo.use_read` and `repo.index` grants on this repository), and copy the Organization ID (also shown with a one-click copy button in Settings → General). Store the token as the Actions secret `DEVIN_INDEXING_API_KEY` and the `org-...` ID as the Actions variable `DEVIN_ORG_ID` — the org slug/name is not the API identifier and is rejected by the indexer with guidance. Then record the effort level seen on the org's DeepWiki page as the Actions variable `DEVIN_WIKI_EFFORT` (`low` | `medium` | `high`). Until these exist, every run logs a loud `not_provisioned` / `effort_unrecorded` state in its summary artifact and makes no Devin call. This token is a Devin API token, not a GitHub PAT; no new GitHub credential is created for indexing — the GitHub side reuses the workflow's existing operator-token precedence solely to list branches and open pull requests.

## Credential and provider prerequisites

The operator token must meet GitHub’s documented requirements for adding a repository to an App installation: it must be an existing **classic PAT with `repo` scope**, and it must have repository administration access.[1] The token must also be able to discover the existing `devin-ai-integration` installation through `GET /user/installations`.

A repository owner without a visible Devin installation is reported as `not_configured`; an inaccessible installation or rejected assignment is reported as `blocked`. Neither result causes a default-branch update, a workflow overwrite, a pull-request mutation, or an attempt to call a private Devin/DeepWiki endpoint.

> **Verification timestamp rule:** an indexed DeepWiki page may lag the latest commit. Whenever a claim is taken from public DeepWiki or Devin Wiki, record the page URL, the visible source ref or timestamp when available, and the corroborating repository commit, workflow, issue, or pull-request evidence.

## Linguist, AppliedSxi, and A2A machine-communication boundaries

Linguist currently owns compact internal prompt and pointer conventions; it has no separate Wiki schedule. The AppliedSxi `maxc` component has no registered Wiki ingestion contract. Agent-to-agent machine communication is therefore not an independent Wiki writer: any future page design for those domains must be added through a separately accepted scope, steered through `.devin/wiki.json` where appropriate, and validated against source after indexing. The separate `linguist-machine-parity` proposal remains the appropriate lane for a public README representation or badge enhancement.

## References

[1]: https://docs.github.com/en/rest/apps/installations#add-a-repository-to-an-app-installation "GitHub: Add a repository to an App installation"
[2]: https://docs.github.com/en/apps/using-github-apps/reviewing-and-modifying-installed-github-apps "GitHub: reviewing and modifying installed GitHub Apps"
[3]: https://docs.devin.ai/integrations/gh "Devin GitHub integration"
[4]: https://docs.devin.ai/work-with-devin/deepwiki "Devin DeepWiki"
[5]: https://docs.devin.ai/api-reference/v3/repositories/put-organizations-index-repository "Devin v3 API: Index a repository"
[6]: https://docs.devin.ai/onboard-devin/index-repo "Devin: Index a Repository"
