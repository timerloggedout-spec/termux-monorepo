# Source record — repository-provisioner

## Confirmed repository precedent

The repository's AppID Registrar evaluation records a successful creation:

- Repository: `timerloggedout-spec/appid-registrar`
- Repository ID: `1444893519`
- Created: `2026-11-03T22:20:19Z`
- Visibility: private
- Default branch: `main`
- Recorded route: PAT API `POST /user/repos` with `auto_init=true`.
- First branch: `migration/appid-migration/replay-v1`.

Sources:
- `ops/github-apps/PROCESS.json`
- `docs/proposals/active/master-splinter/EVALUATION.md` — “Addendum — name ISSUED + repo created”.

## Workflow design boundary

The provisioner supports two owner types:

- Personal account: resolve the authenticated owner from `GET /user` and create through `POST /user/repos`.
- Organization: verify active admin membership through `GET /user/memberships/orgs/{org}`, verify the organization plan is Free through `GET /orgs/{org}`, require an exact owner/repository confirmation, and create through `POST /orgs/{org}/repos`.

Both routes create one repository per manual dispatch, initialize the default branch with GitHub's `auto_init=true`, verify owner/name/ID/default branch, and publish a metadata-only receipt.

The workflow creates repositories inside an existing organization. Organization creation itself remains a personal-account settings operation. The workflow does not transfer, delete, rename, configure secrets, add collaborators, or change branch protection.

## Authority and security

- Repository hard rules: `CLAUDE.md`.
- Human-only credential/permission edges: `docs/proposals/AGENTIC-PERMISSIONS.md`.
- Dual-gate policy: `docs/ARCHW1Z-GATE.md`.
- The workflow consumes the pre-provisioned operator PAT secret chain; it does not create, rotate, display, or export credentials.
