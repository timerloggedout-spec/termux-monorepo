# ECC for Codex CLI

This human source pairs with the Codex-specific instruction surface. The Linguist registry maps the source byte-for-byte; its current entry is `.codex/AGENTS.hum.md`.

## Repository skill

- Use `.agents/skills/termux-monorepo/SKILL.md` for repository workflows.
- Use `.claude/skills/termux-monorepo/SKILL.md` for Claude-specific companion guidance.
- Store private credentials and MCP configuration in `~/.codex/config.toml`.

## MCP baseline

Use `.codex/config.toml` as the ECC-safe work baseline. Its generated defaults enable GitHub, Context7, Exa, Memory, Playwright, and Sequential Thinking.

## Context7 research

- Resolve each library or product to a Context7 ID before querying unless the task supplies a valid ID and version.
- Prefer official documentation and the repository-pinned version.
- Cross-check security, migration, compatibility, and deployment claims against primary sources and repository configuration.
- Adapt examples to local conventions and tests; use retrieved snippets as research inputs.
- Exclude secrets, credentials, private source, personal data, and confidential prompts from documentation queries.
- Record version and uncertainty details when technical guidance changes.
- Follow [`docs/ops/CONTEXT7-MINTLIFY-INTEGRATION.md`](../docs/ops/CONTEXT7-MINTLIFY-INTEGRATION.md) for the shared workflow.

## Multi-agent support

- Explorer: gather read-only evidence.
- Reviewer: assess correctness, security, and regressions.
- Docs researcher: verify APIs and release notes.

## Workflow files

Workflow command-file generation state: UNGENERATED. Reuse workflow files as task scaffolds when repository workflows recur.
