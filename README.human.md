# README.human.md — Human-readable twin

This file is the **human** counterpart to the compressed agent surfaces (`AGENTS.md`, `CLAUDE.md`).

Agents should prefer the compressed forms. Humans use this document for orientation, rationale, and full prose.

## Naming convention

| Audience | File | Notes |
|----------|------|-------|
| Agents (compressed) | `AGENTS.md` | Always maintained compressed. Source of truth for agents. |
| Humans (readable) | `README.human.md` | Full prose. No forced compression. |
| Cheat_Code (all agents) | `CLAUDE.md` | Present even for non-Claude agents. Carries CAVEMAN-micro + dual-file policy. |

Locale later if needed: `README.human.en.md`.

## Why dual-file

Token cost on every agent session is real. Compressed instructions keep signal high. Humans still need the expanded story, history, and rationale without hunting through fragments.

## CAVEMAN

Compression identity stays **CAVEMAN** (embedded in paths, skills, Cheat_Codes).
Primary seed: [kuba-guzik/caveman-micro](https://github.com/kuba-guzik/caveman-micro) — 6 lines, 85 tokens, outperformed the longer original skill on Claude Sonnet and Opus while keeping 100% quality on structured coding tasks.

See `workspace/caveman/` and `CLAUDE.md` for the live prompt and inventory.

## Project orientation

See the main project README and `docs/` for architecture, Termux constraints, peer routing (OmniRoute ↔ OpenRouter), and proposal process. This twin does not replace those; it exists so human readers are not forced through agent-compressed text.
