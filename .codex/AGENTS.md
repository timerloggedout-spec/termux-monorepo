# ECC for Codex CLI

This supplements the root `AGENTS.md` with a repo-local ECC baseline.

## Repo Skill

- Repo-generated Codex skill: `.agents/skills/termux-monorepo/SKILL.md`
- Claude-facing companion skill: `.claude/skills/termux-monorepo/SKILL.md`
- Keep user-specific credentials and private MCPs in `~/.codex/config.toml`, not in this repo.

## MCP Baseline

Treat `.codex/config.toml` as the default ECC-safe baseline for work in this repository.
The generated baseline enables GitHub, Context7, Exa, Memory, Playwright, and Sequential Thinking.

## Context7 research contract

- Resolve a library/product to its Context7 ID before querying unless a valid ID/version was supplied.
- Prefer official sources and the repository-pinned version; ask focused, concept-specific questions.
- Cross-check consequential security, migration, compatibility, and deployment claims against primary documentation and repository config.
- Adapt examples to local conventions and tests; do not treat retrieved snippets as implementation proof.
- Never send secrets, credentials, private source, personal data, or confidential prompts to documentation lookup.
- Record meaningful version/uncertainty details when technical guidance changes.

See `docs/ops/CONTEXT7-MINTLIFY-INTEGRATION.md` for the full shared workflow.

## Multi-Agent Support

- Explorer: read-only evidence gathering
- Reviewer: correctness, security, and regression review
- Docs researcher: API and release-note verification

## Workflow Files

- No dedicated workflow command files were generated for this repo.

Use these workflow files as reusable task scaffolds when the detected repository workflows recur.
