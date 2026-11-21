# Source record — repository-provisioner

## Confirmed repository precedent

The repository's AppID Registrar evaluation records a successful creation:

- Repository: `timerloggedout-spec/appid-registrar`
- Repository ID: `1444893519`
- Created: `2026-11-03T22:20:19Z`
- Visibility: private
- Default branch: `main`
- Recorded route: PAT API `POST /user/repos` followed by Contents API seeding.
- First branch: `migration/appid-migration/replay-v1`.

Sources:
- `ops/github-apps/PROCESS.json`
- `docs/proposals/active/master-splinter/EVALUATION.md` — “Addendum — name ISSUED + repo created”.

## Workflow design boundary

This implementation uses the authenticated-user endpoint and resolves the owner from `GET /user`. It creates one repository per manual dispatch, defaults to private visibility, initializes the default branch, then writes a provisioning receipt using the Contents API. The workflow does not create accounts, mint credentials, transfer repositories, or mutate repository security settings.

## Authority and security

- Repository hard rules: `CLAUDE.md`.
- Human-only credential/permission edges: `docs/proposals/AGENTIC-PERMISSIONS.md`.
- Dual-gate policy: `docs/ARCHW1Z-GATE.md`.
- The workflow consumes the pre-provisioned `OPERATOR_GITHUB_TOKEN` secret; it does not create, rotate, display, or export credentials.
