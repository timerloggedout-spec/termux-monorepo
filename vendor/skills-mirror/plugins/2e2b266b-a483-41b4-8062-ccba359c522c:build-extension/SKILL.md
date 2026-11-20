---
description: Build or continue a local, cloud-backed, or hybrid Chrome extension through the complete specialist workflow.
argument-hint:
- idea or existing project path
---

Use the `chrome-extension-builder` skill to handle the user's request: $ARGUMENTS

Resolve the installed plugin root from this command's location. In Claude Code, `${CLAUDE_PLUGIN_ROOT}` is substituted in the Markdown body; in other runtimes use the discovered absolute plugin path. Never assume it is a shell environment variable.

1. Inspect the existing project and current user authorization before asking questions. Establish single purpose, target users, local/cloud/hybrid mode, browser surfaces, data flows, permissions and acceptance journeys. Ask only consequential missing choices; offer a recommended default for reversible ones.
2. Read `${CLAUDE_PLUGIN_ROOT}/skills/chrome-extension-builder/references/team.json`. Follow its research → architecture → design/implementation → verification → release graph. Delegate exact file ownership to available specialist agents; otherwise execute the roles serially and report independence limits honestly.
3. Use the bundled CLI for deterministic work. Run `node "${CLAUDE_PLUGIN_ROOT}/skills/chrome-extension-builder/scripts/extension_builder.mjs" --help` and subcommand help before assembling arguments. Available actions include `session`, `scaffold`, `check`, `package`, and `studio`. Plugin-maintenance commands belong to the separate source checkout. `scaffold` makes a baseline requiring implementation; it does not build arbitrary requested product behavior.
4. Initialize or resume the project session, record real evidence and complete meaningful vertical slices. Preserve dirty changes and never overwrite an existing project to start anew. Invoke `chrome-extension-builder-backend` and `chrome-extension-builder-integrations` only when the architecture needs them.
5. Verify the actual extension build with security, behavioral/runtime, accessibility and performance evidence. Bound candidate improvement to three rounds, retain the strongest verified result, and expose remaining blockers.
6. Prepare concrete package/listing/privacy artifacts for the authorized distribution scope. Existing user intent governs external actions; packaging never proves Store publication.

Return a concise result with artifact paths, exact verified behavior, evidence limitations and any specific remaining user/provider gate. Do not stop at a plan when implementation is authorized.
