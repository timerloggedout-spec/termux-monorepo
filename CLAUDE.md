# CLAUDE.md

This file supersedes `AGENTS.md` and provides project-wide instructions for AI agents.

## Build & Test Commands
- Install dependencies: `pnpm install`
- Run tests: `pnpm test`
- Lint: `pnpm lint`

## Guardrails
- Do NOT modify files inside `generated/`.
- Never commit `.env` files.
- Follow the Siglary policy: use DO‑STATEMENTS only.

## Quick Reference
- Use `scripts/dispatch_ai_studio.py` for AI Studio dispatch.
- CI will run the self‑repair workflow.
