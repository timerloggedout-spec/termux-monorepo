# Repository-Surface Reconciliation

**Status:** Implemented as a governed, pull-request-only control plane under `AR-09`. The source of truth is `.github/workflows/publish-wiki.yml` in `timerloggedout-spec/termux-monorepo`. The controller uses the repository’s established `ARCHWIZ_GITHUB_TOKEN` → `OPERATOR_GITHUB_TOKEN` → `OPERATOR_TOKEN` → `github.token` precedence only for the duration of its job.

## Purpose and boundary

The repository surface is reconciled so that repositories reachable by the existing operator token are automatically **discovered** and assessed for the managed GitHub Wiki publisher. A daily scheduled run produces an immutable report artifact. A human may manually request an apply run; that run can create or update a dedicated `automation/wiki-publisher` branch and reviewable pull request in an eligible repository. It never pushes to a default branch, merges a pull request, overwrites a workflow lacking the managed marker, or interprets issue, pull-request, comment, or external-wiki content as an instruction.

> **DeepWiki boundary:** Devin/DeepWiki remains a discovery and generation aid. The official DeepWiki documentation supports generation steering with `.devin/wiki.json`, but it does not document a repository-wide private-wiki Markdown export endpoint. Therefore this control plane does **not** fetch private Devin Wiki content or treat it as evidence that authorizes a GitHub change. GitHub Wiki publication remains an in-repository, reviewable Markdown flow.

## Operating model

| Stage | Trigger | Credential lane | Result | Mutation boundary |
|---|---|---|---|---|
| Discovery | Daily scheduled run | Existing operator-token precedence, scoped to the job | JSON report of `current`, `missing`, `drifted`, `unmanaged`, `excluded`, or `blocked` repositories | Read-only |
| Reconciliation | Manually dispatched with `apply=true` | The same job-scoped operator token | One stable branch and PR per eligible repository | Branch and PR only |
| Publication | A merged target-repository change under `wiki/**` | Target repository `GITHUB_TOKEN` | GitHub Wiki receives the local `wiki/` Markdown projection | GitHub Wiki only |

The controller queries `GET /user/repos` using the selected operator token, with `owner`, organization-membership, and collaborator affiliations. This makes inventory explicitly credential-scoped: the report includes only repositories that the existing authorized token can access. It does not guess at enterprise-wide access or mint new credentials.[1]

## Credential lanes

The repository-surface lane uses the already established operator-token precedence in a job environment. The value is never logged, persisted, committed, or passed between jobs. Its scope is limited to GitHub API operations needed for read-only discovery or the explicitly requested reviewable PR updates.

The **GitHub App-token** work referenced in Issue #192 remains separate. Its Marketplace predecessor is deprecated, and the decision ledger already reserves the official successor for a dedicated, separately reviewed cross-repository or event-propagation implementation. This reconciler does not create an App registration, request a private key, or change that lane’s permissions.[2]

## Managed-file contract

Only `.github/workflows/publish-wiki.yml` containing this exact marker is eligible for replacement:

```yaml
# managed-by: timerloggedout-spec/repository-surface-reconciler
```

A missing workflow is eligible for a generated PR. A marker-bearing workflow whose contents differ from the control-plane source is eligible for a generated PR. An unmarked workflow is reported as `unmanaged` and left untouched. Archived repositories and the controller itself are excluded. This protects repository-local workflow ownership while still making drift visible.

The publisher is restricted to the repository default branch, uses immutable action SHAs, has a non-destructive manual dry-run mode, and checks out without persisting credentials. A non-default branch manual publish request fails explicitly; a dry run remains available on any ref. The controller is also pinned, reports its output as an artifact, and has no scheduled write path.

## Operator runbook

1. Merge the control-plane PR after the normal repository checks are green. No new secret or GitHub App setup is required for this lane.
2. Review the daily reconciliation artifact. It inventories only the user, organization, and collaboration repositories available to the existing operator token.
3. Repositories listed as `unmanaged` need an explicit local ownership decision; they will never be overwritten automatically.
4. When the report is acceptable, run **Reconcile repository surface** manually with `apply=true`. Review and merge each generated PR under its target repository’s normal protections.
5. Keep any future GitHub App-token design in its separate Issue #192 scope, with its own permissions, installation, event, and provenance review.

## Evidence and constraints

| Evidence | Verified conclusion | Design response |
|---|---|---|
| `.github/workflows/dependency-phase-dispatch.yml` and peer orchestration workflows | The repository has an established privileged-token precedence for controlled workflow operations. | Reuse precisely that precedence; do not create a parallel secret or credential mechanism. |
| `.github/workflows/publish-wiki.yml` | The publisher copies the in-repository `wiki/` directory to GitHub Wiki after source-repository pushes. | Preserve that relationship; harden the source workflow rather than introduce a direct Wiki writer. |
| `docs/agentic/deepwiki-validation.yaml` | Public DeepWiki was not indexed and DeepWiki/agent claims cannot authorize workflow execution or completion. | Do not add an unverified private DeepWiki importer. |
| `docs/proposals/active/actions-refinements/ACTION-DECISION-LEDGER.md` | GitHub App-token integration is an explicitly scoped separate candidate. | Keep App-token work in that lane; use existing operator-token authority for AR-09. |

## References

[1]: https://docs.github.com/en/rest/repos/repos#list-repositories-for-the-authenticated-user "List repositories for the authenticated user"
[2]: https://github.com/marketplace/actions/github-app-token "Deprecated GitHub App Token Marketplace action"
[3]: https://docs.devin.ai/work-with-devin/deepwiki "Devin DeepWiki"
