# Items — repository-provisioner

## RPW-001 — Manual GitHub repository creation and initialization

**Priority:** P1  
**Status:** executing  
**Owner:** repository automation  
**Implements:** `.github/workflows/repository-provisioner.yml`

### Scope

- Expose a `workflow_dispatch` form for repository slug, description, and private/public visibility.
- Authenticate through the existing operator GitHub PAT secret chain.
- Resolve the authenticated account through `GET /user`; user-owned creation stays within `timerloggedout-spec`.
- Validate a lowercase, hyphen-safe repository slug and reject an existing repository before creation.
- Create through GitHub REST `POST /user/repos` with `auto_init=true`.
- Emit repository URL, ID, visibility, default branch, and initialization receipt in the Actions summary.
- Serialize requests per repository slug and keep credentials out of logs and artifacts.

### Acceptance

1. Valid private and public requests create the named repository under the authenticated personal account.
2. Invalid slugs fail before the create API call.
3. Existing repositories fail with a clear duplicate result.
4. Created repository metadata is checked against the requested owner/name.
5. GitHub auto-initializes the default branch with a README.
6. The run summary records repository URL, ID, visibility, default branch, and provisioning endpoint.
7. Secret values are absent from logs, summaries, and artifacts.
8. `repo-gate` and `termux-smoke` pass on the exact merge candidate SHA.

## RPW-002 — Free organization-owned repository provisioning

**Priority:** P0  
**Status:** implementing  
**Owner:** repository automation  
**Implements:** `.github/workflows/repository-provisioner.yml`

### Scope

- Add `owner_type=user|organization` and `target_owner` inputs.
- Preserve the existing personal-account route as the default.
- For organization targets, verify active administrator membership through `GET /user/memberships/orgs/{org}`.
- Verify the destination organization reports GitHub Free through `GET /orgs/{org}`.
- Require an exact confirmation string `CREATE owner/repository` for organization-owned creation.
- Create through GitHub REST `POST /orgs/{org}/repos`.
- Verify the created repository owner, name, ID, and default branch.
- Keep organization creation itself in the personal-account GitHub settings flow.

### Constraints

- Manual dispatch only; each successful create represents one explicit request.
- Organization-owned creation requires the configured operator PAT and active organization-owner membership.
- The destination organization must report GitHub Free.
- The workflow creates one repository per successful dispatch.
- Keep repository creation focused on one new repository per dispatch; route transfers, renames, secret configuration, collaborator changes, and branch protection through their dedicated workflows.

### Acceptance

1. The default user-owned path preserves existing behavior.
2. Organization preflight requires active admin membership and a Free plan.
3. Organization creation requires the exact owner/repository confirmation.
4. A repository name conflict fails before the create API call.
5. The created repository metadata matches the requested organization and name.
6. Secret values remain absent from logs, summaries, and artifacts.
7. `repo-gate` and `termux-smoke` pass on the exact merge candidate SHA.

## Evidence

- Prior successful personal-account creation: `timerloggedout-spec/appid-registrar`, repository ID `1444893519`, created 2026-11-03.
- Existing route: PAT REST `POST /user/repos` with `auto_init=true`.
- Organization route: PAT REST `POST /orgs/{org}/repos` after owner and Free-plan verification.
- Source: `source.md`.
