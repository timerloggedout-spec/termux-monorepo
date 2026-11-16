# n8n Free Community Edition Wiring

**Status:** optional, self-hosted, free-scope adapter  
**Canonical truth:** GitHub history + GitHub Actions evidence  
**n8n role:** visual composition / adapter / human-operated automation surface

## Why this lane is now wired

The repository already specified n8n as an optional visual/reference lane. The missing piece was an importable workflow and a reproducible free self-hosted runtime.

n8n's Community Edition is available as a standard self-hosted version. See the official pricing page for current Community Edition availability. urln8n pricing / Community Editionhttps://n8n.io/pricing/

For this repository:

- **GitHub Actions remains authoritative** for collection, validation, reducers, and evidence.
- **n8n is an optional adapter**, not a replacement scheduler or system of record.
- The committed compose file binds n8n to localhost by default.
- Credentials, public webhook endpoints, and tunnel URLs remain operator configuration.
- The n8n workflow emits a sanitized evidence receipt; it does not receive prompts, completions, secrets, arbitrary tool payloads, or repository credentials.

## Free deployment

The Community Edition can be self-hosted without n8n Cloud. n8n documents the Community Edition as a self-hosted option and provides a free Community Edition activation for additional features such as folders, debugging, and custom execution data. citeturn0search0turn0search3

### Start locally

    cd ops/n8n
    cp .env.example .env
    # replace N8N_ENCRYPTION_KEY with a stable random secret
    docker compose up -d

Open `http://localhost:5678`.

Do **not** expose the development instance directly to the public internet. If an operator later places it behind a reverse proxy or tunnel, set `N8N_WEBHOOK_URL` and `N8N_EDITOR_BASE_URL` to the externally reachable HTTPS origin and apply normal authentication/network controls.

The compose file is pinned to n8n `2.41.3`, the stable release shown by the upstream release feed during this integration pass. citeturn1search0

## Import the SHE workflow

Import:

`ops/n8n/workflows/she-github-workflow-run-intake.json`

Workflow:

    GitHub workflow_run
            │
            ▼
    optional n8n webhook
            │
            ▼
    sanitize + normalize
            │
            ▼
          receipt

The normalized envelope is deliberately small:

- schema version
- observation timestamp
- repository
- workflow
- run ID/number
- status/conclusion
- SHA/branch
- actor
- GitHub run URL

This matches the existing SHE observer boundary, where GitHub Actions/webhook payloads can be normalized into deterministic incident/evidence records without giving the receiver mutation authority.

## Optional GitHub → n8n bridge

`.github/workflows/n8n-she-bridge.yml` is deliberately inert until the repository secret `N8N_SHE_WEBHOOK_URL` is configured.

Once configured, every completed GitHub workflow run emits a **sanitized** receipt to n8n.

If the secret is absent, the job exits successfully after recording that the bridge is not configured. Canonical GitHub evidence is unaffected.

## Architecture boundary

    GITHUB TRUTH
         │
    Actions / evidence
         │
    ┌────┴────────┐
    ▼             ▼
    SHE reducers  n8n adapter
    deterministic visual / optional
         │             │
         ▼             ▼
    dashboard     operator flows

n8n must not become a hidden second evidence store.

## Security invariants

- Never commit `N8N_ENCRYPTION_KEY`.
- Never commit webhook URLs containing secrets.
- Keep the local compose binding on `127.0.0.1`.
- Treat a public webhook endpoint as a credential-equivalent secret.
- Send only allowlisted metadata.
- Do not pass GitHub tokens through n8n.
- Do not let an n8n workflow mutate GitHub unless a separately reviewed credentialed workflow is introduced.
- Keep the adapter versioned in GitHub so workflow changes are reviewable.

## Operational state vocabulary

`DESIGNED → IMPORTED → CONFIGURED → OBSERVED → VALIDATED → PROMOTED`

The repository should not claim `OBSERVED` until an actual n8n execution receipt exists.

## License / use boundary

n8n's current legal terms distinguish self-hosted software and third-party integrations. The free Community Edition is suitable for the intended internal/self-hosted adapter lane, but if the project later exposes n8n as a service to external customers or embeds it into a commercial offering, review n8n's current licensing terms before changing the deployment model. citeturn0search10
