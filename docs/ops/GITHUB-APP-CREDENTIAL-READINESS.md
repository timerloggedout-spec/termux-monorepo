# GitHub App Credential Readiness

## Scope

This is the repository-side contract for the GitHub App capability path referenced by Issue #184 and the PR #800 Checks-publication failure.

Issue #184 is the credential inventory SSOT, but this repository stores **names and contracts only**. No private key, token, installation secret, or authorization header belongs in Git.

## Required Actions configuration

| Item | Storage | Purpose |
|---|---|---|
| APP_CLIENT_ID | repository variable | GitHub App Client ID |
| APP_PRIVATE_KEY | repository Actions secret | GitHub App private key |

The manual workflow `.github/workflows/github-app-capability-probe.yml` mints a short-lived installation token and reads the effective installation permissions.

## Required App permission

For the PR #800 failure mode, the decisive capability is **Checks: write**. The installed App must have the permission and the installation owner must approve any permission increase.

Other permissions should be added only for a demonstrated workflow need. For a read-only capability probe, repository Contents read is supplied by the workflow's GITHUB_TOKEN; the App token is used only for installation-permission inspection.

GitHub App installation tokens are short-lived. The official create-github-app-token action documents the normal one-hour lifetime and supports explicitly scoped repository access.

## Verification

Run the manual GitHub App Capability Probe. A successful run proves only that the configured installation currently exposes Checks: write and metadata access to the probe. It does **not** prove ECC Tools billing/quota, provider availability, branch protection, or application-level check publication.

If the probe fails with Checks: write missing:

1. open the GitHub App registration owned by the operator;
2. enable the minimum required Checks permission, at least write for the publication path;
3. approve the updated permission on the repository installation;
4. rerun the probe;
5. only then treat ECC Tools check-publication availability as eligible for another observation cycle.

## Security boundary

- Never paste the App private key or installation token into an issue, PR, comment, artifact, workflow log, or source file.
- Never create or rotate repository secrets from an autonomous workflow.
- Never grant broad organization permissions merely to repair one check-publication path.
- Keep the capability probe manual and read-only.
- Treat a missing credential as a blocked capability, not as permission to fall back to a broader secret.

## Upstream references

- GitHub App permissions: https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app
- GitHub App authentication in Actions: https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/making-authenticated-api-requests-with-a-github-app-in-a-github-actions-workflow
- Official create-github-app-token action: https://github.com/actions/create-github-app-token