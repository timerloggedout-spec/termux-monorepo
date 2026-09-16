# Devin Wiki Access Reconciliation

**Status:** Implemented under `AR-13` as an autonomous, token-scoped control plane. The source of truth is [`.github/workflows/reconcile-devin-wiki-access.yml`](../../.github/workflows/reconcile-devin-wiki-access.yml); its reconciler is [`scripts/agentic/reconcile_devin_wiki_access.py`](../../scripts/agentic/reconcile_devin_wiki_access.py).

## Purpose

The repository-surface reconciler already discovers repositories reachable by the established operator-token lane and manages the local GitHub Wiki publisher. This companion controller uses the *same credential-scoped inventory* to reconcile **GitHub App access for the official `devin-ai-integration` App**. When that App is installed with **selected repositories**, a newly accessible repository can be assigned to the existing installation through GitHub’s documented API. When the App is installed with **all repositories**, future repositories are already covered by the provider configuration.[1] [2]

This controller does not grant provider permissions that the existing GitHub App did not request; it does not create a GitHub App, an App private key, an API key, a provider session, or a browser login. It relies exclusively on an existing operator PAT that GitHub accepts for the documented assignment endpoint.

## Multi-Wiki scope

| Surface | Automation responsibility | Freshness and authority boundary |
|---|---|---|
| In-repository `wiki/` Markdown | Normal pull-request review and managed GitHub Wiki publication. | Repository source and review evidence are canonical. |
| GitHub Wiki | Published from reviewed `wiki/` content by `Publish wiki`. | A change to `wiki/**` on the default branch triggers publication. |
| Devin Wiki | Provider-managed indexing becomes eligible after the existing Devin GitHub App covers a repository. Root `.devin/wiki.json` can steer page generation. | Provider output remains discovery material and requires source corroboration. |
| Public DeepWiki | Provider-managed public discovery surface for indexed repositories. | No documented indexing-write or refresh endpoint is invoked by this controller; indexed source refs and timestamps must be validated before use. |

The root README retains links to the GitHub Wiki, public DeepWiki, and Devin Wiki. The three destinations are intentionally complementary rather than mirrors of authority.

## Operating model

| Stage | Trigger | Credential lane | Result | Mutation boundary |
|---|---|---|---|---|
| Access discovery | Daily schedule at `05:41 UTC` or manual dispatch with `apply=false` | Existing operator-token precedence | Redacted counts for `current`, `missing`, `not_configured`, `excluded`, or `blocked` state. | Read-only |
| Selected-repository assignment | Daily schedule or manual dispatch with `apply=true` | Existing **classic PAT with `repo` scope** | Missing eligible repositories are assigned to the existing Devin App installation. | GitHub App repository-access list only |
| Devin Wiki generation | Provider-managed after access is available | Devin service | Provider-generated Wiki can read `.devin/wiki.json` during generation. | Provider-managed; not called directly |
| Public DeepWiki indexing and refresh | Provider-managed | DeepWiki service | Public indexed pages may become available according to provider behavior. | No undocumented endpoint or browser flow is used |

The scheduled controller is autonomous: it does not wait for a human comment, browser handoff, or provider UI checkbox. It only performs the documented GitHub App repository-assignment call, and it produces a redacted summary artifact. The detailed inventory is created only on the ephemeral runner and deleted before artifact upload.

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
