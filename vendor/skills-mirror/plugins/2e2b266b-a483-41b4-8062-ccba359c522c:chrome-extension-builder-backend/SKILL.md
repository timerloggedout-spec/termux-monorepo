---
name: chrome-extension-builder-backend
description: Build optional secure Chrome extension cloud backends with APIs, SaaS accounts, OAuth, databases, AI proxies, server jobs, billing entitlements, deployment, and observability.
---

# Chrome Extension Builder: Backend

Before starting, read [shared policy boundaries](../chrome-extension-builder/references/policy-boundaries.md). Follow host safeguards, task-scoped inputs, synthetic fixtures, and the no-secrets/no-restricted-data boundary. Local tools and persistence are optional: check explicit environment access first; otherwise deliver the same role's useful sanitized findings, specification, code, or test plan in normal Markdown and mark execution unrun.

Use a backend for protected credentials, shared data, accounts, integrations, heavy jobs, or entitlements. Read [cloud-and-auth.md](../chrome-extension-builder/references/cloud-and-auth.md), live stack/provider docs, and architecture. Complete authorized local/staging work; identify materially new external actions needing authorization.

These are separately generated-product designs implemented with placeholders and synthetic fixtures. Real login, token/secret provisioning, protected account configuration, and live payments occur outside plugin input/artifact handling. Do not process supplied credentials or restricted records, create a plugin cloud connection, or sell/upsell plugin subscriptions.

Define `docs/backend-contract.md`: endpoints, schemas, authentication, per-object/tenant authorization, errors/timeouts, quotas, retry/idempotency, retention, env variable names, and deployment/rollback. Provide `.env.example` with placeholders. Private provider/service keys never enter extension/client bundles, frontend env prefixes, logs, or chat.

1. Validate requests, parameterize database queries, and use least-privilege identities. Enforce resource ownership server-side. CORS and public extension/client IDs are not authorization.
2. Use provider-supported authorization-code flow with PKCE and state verification. Bind transactions to initiating sessions, validate exact redirect and issuer/audience as appropriate, and test expiry/replay/cancel. Follow Chrome identity APIs' current contract. Keep access tokens minimal in trusted contexts; prefer server handling for confidential tokens.
3. Implement migrations/backups, account-state isolation, export/delete, logout/revocation, bounded jobs, timeouts, retries, and deduplication. Test ownership failures/duplicate requests.
4. Billing uses hosted checkout, verified webhook signatures, idempotent events, server entitlements, and test/live separation. Never trust client payment claims. New charges/subscriptions, production deployment, or billing configuration need scope authorization, not a magic phrase.
5. Add redacted metrics and actionable errors. Budget provider calls, rate-limit per account, support cancellation, and show accurate cloud status.

Deliver API/source, fixtures, negative contract tests, migration/run instructions, env placeholders, and authorized deployment evidence. Exit when an extension-to-backend canary proves flow/data boundaries. Missing provider credentials leave a clearly named live gate while local behavior is completed.

## Context and outcome handoff

Check that backend/accounts are justified by confirmed project need; do not infer them from an old provisional assumption. Preserve provider/account/data/cost boundaries; record interface changes and affected stale acceptance evidence in the canonical project state. Preserve the canonical report destination assigned by `references/team.json`; any overview is a dated view, not a competing authority.
