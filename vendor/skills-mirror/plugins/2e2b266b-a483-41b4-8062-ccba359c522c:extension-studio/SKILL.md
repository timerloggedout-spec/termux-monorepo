---
description: Open the local interactive planning studio and turn its brief into an actionable extension build session.
argument-hint:
- project path or extension idea
---

Use the `chrome-extension-builder` skill for this request: $ARGUMENTS

Start the bundled local studio with `node "${CLAUDE_PLUGIN_ROOT}/skills/chrome-extension-builder/scripts/extension_builder.mjs" studio`. Inspect command help for optional project/port arguments before using them. In runtimes without Claude path substitution, resolve the installed plugin root and pass its absolute path instead. Keep the server on its default loopback address; do not expose it publicly for a local planning request.

Open the returned loopback URL in the available browser or Codex browser panel. The studio supports a visual brief and plan; explain which controls actually run locally and which hand off to the agent. Do not imply that a planning form creates an arbitrary extension, runs specialist agents, supplies a cloud backend, or publishes a Store listing by itself.

Help the user select local/cloud/hybrid mode, main surface, permissions/data expectations and project scope. Use progressive questions and preserve the draft. When the user requests a build, transfer the studio brief to the orchestrator's complete workflow and record evidence in the real project session. If opening a browser is unavailable, return the exact working URL and continue the conversational workflow.

Report the studio URL and the concrete next action. Stop the server only when requested or no longer needed; retain any saved/exported project brief.
