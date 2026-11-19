---
description: Verify and package an exact Chrome extension build, prepare Store materials, and carry out the authorized distribution scope.
argument-hint:
- extension project path and distribution target
---

Handle release for: $ARGUMENTS

Read `chrome-extension-builder-release` and use the `release-manager` role with independent `security-reviewer` and `qa-engineer` evidence. Verify current Chrome Web Store requirements with primary documentation. Respect existing user authorization; obtain only consequential missing decisions after preparing concrete reviewable artifacts.

Confirm single purpose, minimal permissions and reasons, data disclosures, privacy/support details, local executable dependencies, real production endpoints, version/migrations, asset completeness and runtime tests on the exact release build. Inspect `check --help` and `package --help`, then use `node "${CLAUDE_PLUGIN_ROOT}/skills/chrome-extension-builder/scripts/extension_builder.mjs" check` and `package` with verified arguments. Keep the ZIP output outside its source and inspect the archive root/content/hash.

Prepare truthful listing text, screenshots/icons, reviewer instructions and release/rollback notes. Do not invent legal identity, privacy URLs, supported countries, test credentials or approval. Treat local package readiness, upload, review, publication and observed install as distinct states. If credentials/provider tooling are missing, retain the complete ready package and name the remaining gate; never imply a submission happened.

Return artifact links, observed checks, actual release state and next required action.
