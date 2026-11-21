---
name: chrome-extension-builder-release
description: Prepare and verify Chrome extension release artifacts, CI, versioning, store listing/screenshots, permissions/privacy disclosures, authorized submission, backend compatibility, and rollout evidence.
---

# Chrome Extension Builder: Release

Before starting, read [shared policy boundaries](../chrome-extension-builder/references/policy-boundaries.md). Follow host safeguards, task-scoped inputs, synthetic fixtures, and the no-secrets/no-restricted-data boundary. Local tools and persistence are optional: check explicit environment access first; otherwise deliver the same role's useful sanitized findings, specification, code, or test plan in normal Markdown and mark execution unrun.

Read [release-and-operations.md](../chrome-extension-builder/references/release-and-operations.md), live store requirements, security review, browser QA, and current source. Prepare local artifacts before seeking approval for an external action lacking authorization. Existing authorization persists; no blanket publish-password gate.

Any reviewer test account is for the separately generated Chrome product and is configured in the store's protected channels outside plugin intake. The skills-only plugin itself has no MCP/authenticated demo or credential requirement. Use synthetic fixtures; never receive/export a real password/token.

1. Confirm purpose, MV3/version increase, minimum Chrome, localization, production hosts, packaged assets, licenses, no dev secrets, and backend compatibility.
2. Build from pinned dependencies. Run behavior tests, checker, security/browser/performance checks. Record source/build/ZIP digest and unrun cases. CI checks built output, protects release credentials, and retains redacted reports; automatic production publication needs authorized scope.
3. Package only built output with manifest.json at ZIP root. Resolve `../chrome-extension-builder/scripts/package_extension.py` from this skill directory. Inspect entries/no symlinks/caches/keys/source dumps and load the exact output. Preserve existing user artifacts.
4. Create accurate name/descriptions, real screenshots, icons, support link, privacy policy, permission rationale, data-use/retention declarations, and reviewer instructions. Verify asset dimensions/dashboard fields live. Use a proper reviewer test account; never commit its secrets.
5. Verify developer access and current fees; never assume an amount. Account signup, charges, billing, deployment, and submission require authorized scope. When authorized/tools permit, submit then read back actual item/version/status. Pending/submitted does not mean accepted.
6. Document rollout channel, backend migrations, recovery/rollback, support, and consent-aligned telemetry. Store rollback may require a reviewed update; never promise instant reversal.

Deliver ZIP/source, checklist/digest, listing/privacy/reviewer assets, CI/run commands, and actual external status in `docs/release.md`. Exit criteria follow the target: package ready, browser verified, backend deployed, submitted, or accepted. Acceptance requires observed store evidence.

## Context and outcome handoff

Read compact project state and stale/unrun gates before release preparation. A dated report aggregates canonical specialist evidence; it cannot convert a prepared ZIP, listing, job specification, or source review into published, activated, or browser-verified work. Preserve the canonical report destination assigned by `references/team.json`; any overview is a dated view, not a competing authority.
