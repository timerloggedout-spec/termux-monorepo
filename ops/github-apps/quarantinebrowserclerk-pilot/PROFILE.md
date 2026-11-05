# Termux Fleet QuarantineBrowserClerk — AppID package

- **Provisioning state:** PREPARED ONLY — no GitHub App has been created; no App ID, client ID, installation ID, private key, or client secret is established.
- **Canonical name:** `Termux Fleet QuarantineBrowserClerk`
- **Expected slug:** `termux-fleet-quarantinebrowserclerk` (issued by the registry lane; verify at creation; if taken, return to the registry lane rather than inventing a suffix).
- **Moniker:** `Proctor · QuarantineBrowserClerk` (registry-issued; canonical Proctor, aspect the Session; Heimdall is a held alternative, not a fallback to apply unilaterally).
- **Role:** per-entry GitHub App actor for the D2 Vultr Agent Rush project, Quarantine Browser Clerk.
- **Home / sole installation target:** `timerloggedout-spec/quarantine-browser-clerk` (repository ID 1445293810). Do not install on `termux-monorepo` or any other repository.
- **Visibility:** public.
- **Permissions:** `contents: write`, `pull_requests: write`, `issues: write`, `metadata: read`. No Actions, Checks, webhook, or event permissions are requested; CI is triggered by ordinary PR/push events.
- **Events:** none.
- **Webhook:** none.
- **Manifest:** `manifest.json` in this package; non-secret and safe to review.
- **Creation route:** App Manifest flow, per `docs/ops/GITHUB-APP-PROCESS.md §1A` and `docs/ops/GITHUB-APP-ROUTES.md`. GitHub requires the owner's signed-in session for the single Create confirmation (and any sudo/2SV prompt); installation consent and repository selection are also owner-session steps.
- **Secret custody after conversion:** AppID lane only; expected connector home `custom.github-app-quarantinebrowserclerk`, files mode 0600 in a mode-0700 directory. Never commit or paste the PEM, client secret, webhook secret, or installation token.
- **Post-create verification:** GET /app, GET /app/installations, GET /installation/repositories (must return only `quarantine-browser-clerk`), GET /rate_limit using the installation token. Record the App ID, slug, client ID, installation ID, permission snapshot, bucket proof, and secret names only in the AppID lane's PROCESS.json/profile records.
- **Adoption is a separate gate:** provisioning alone does not prove any workflow uses the app token. Add runtime secret/vars by sealed-box custody flow and demonstrate one scoped workflow run before calling the identity adopted.

This package is a manifest preparation artifact only. It does not assert app creation, installation, credential custody, or workflow adoption.
