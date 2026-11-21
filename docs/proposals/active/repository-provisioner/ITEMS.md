# Items — repository-provisioner

## RPW-001 — Manual GitHub repository creation and initialization

**Priority:** P1  
**Status:** executing  
**Owner:** repository automation  
**Implements:** `.github/workflows/repository-provisioner.yml`

### Scope

- Expose a `workflow_dispatch` form for repository slug, description, and private/public visibility.
- Authenticate through the existing `OPERATOR_GITHUB_TOKEN` secret.
- Resolve the authenticated account through `GET /user`; create only under that account.
- Validate a lowercase, hyphen-safe repository slug and reject an existing repository before creation.
- Create through GitHub REST `POST /user/repos` with `auto_init=true`.
- Seed `PROVISIONING.md` through the GitHub Contents API.
- Emit repository URL, ID, visibility, default branch, and seed receipt in the Actions summary.
- Serialize requests per repository slug and keep credentials out of logs and artifacts.

### Constraints

- Manual dispatch only; each run represents an explicit repository-creation request.
- Private visibility is the default.
- Scope is the authenticated account's own repositories.
- Repository creation is an irreversible external side effect; the workflow creates one repository per successful dispatch.
- The v1 workflow does not transfer, delete, rename, clone templates, configure secrets, add collaborators, or change branch protection.
- Jules and hosted agent handoff are outside this workflow.

### Acceptance

1. Valid private and public requests create the named repository under the authenticated account.
2. Invalid slugs fail before the create API call.
3. Existing repositories fail with a clear duplicate result.
4. Created repository metadata is checked against the requested owner/name.
5. The default branch exists and `PROVISIONING.md` is committed through the Contents API.
6. The run summary records the repository URL, ID, visibility, default branch, and seed path.
7. Secret values are absent from logs, summaries, and artifacts.
8. `repo-gate` and `termux-smoke` pass on the exact merge candidate SHA.

### Evidence

- Prior successful creation: `timerloggedout-spec/appid-registrar`, repository ID `1444893519`, created 2026-11-03.
- Recorded route: PAT REST `POST /user/repos` + Contents API seed.
- Source: `source.md`.
