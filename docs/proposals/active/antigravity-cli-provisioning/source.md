# Research provenance and corrections

Issue: [#1497](https://github.com/timerloggedout-spec/termux-monorepo/issues/1497).

[seed-research.md](seed-research.md) is the supplied “Awesome Google Antigravity CLI: setup, applications, agents, skills, and remote orchestration” attachment, copied unchanged. SHA-256: `94db6d0900cc31727466add4bee9ec8e748bcee3ab549b4e0b77ef0cad34e4bb`. It is user-provided research, not an independently validated specification. Its screenshot footnotes and reported connection/build observations are not fresh device evidence.

## Primary-source checks

The following official pages were fetched successfully during this issue's research. Source claims are not runtime verification of the user's host.

| Claim | Evidence and disposition |
|---|---|
| High verbosity | [CLI reference](https://antigravity.google/docs/cli/reference/) documents `verbosity`, default `high`; retain the user's high setting. |
| Auto-approve | The same reference lists `always-proceed` (never prompts), `proceed-in-sandbox`, `request-review` (default), and `strict`. The seed's conservative example is a recommendation, not the user's requested posture. Do not apply it. Preserve existing auto-approve without rewriting settings. |
| Remote operation is not MCP | [Remote Control](https://antigravity.google/docs/remote-control/) describes browser connections to desktop sessions/CLI instances. `/mcp` is separately listed in the CLI reference. Do not claim a native Cue agent registration, messaging API, or MCP integration merely from remote access. |
| Skills layout | [Skills documentation](https://antigravity.google/docs/skills/) confirms `SKILL.md`, `.agents/skills`, and backward compatibility with `.agent/skills`. Its fetched location table is specifically labeled App; the seed's CLI-global path is NOT independently confirmed here. Verify target build before templating global paths. |
| Termux compatibility and sandbox | Native Termux support and isolation are unverified in these fetched pages. A successful Linux smoke test is not Android or sandbox evidence. |
| Hooks, plugin schemas, command aliases, daemon lifecycle | Retained as seed leads only; do not install speculative schemas or assume every listed command exists in the target build. |

## Evidence boundary

No target host was contacted. No model prompt, installation, credential action, settings change, remote-control start/stop, or device operation was performed. Current host metadata belongs in validation evidence, not inferred from the attachment. The deployment proposal is [PROPOSAL.md](PROPOSAL.md).
