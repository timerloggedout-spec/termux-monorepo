# termux-monorepo

> GitHub Wiki mirror of the Devin DeepWiki for this monorepo.

**Live AI wiki (source of truth for generated docs):**

- Private Devin Wiki: [app.devin.ai …/termux-monorepo](https://app.devin.ai/org/timerloggedout-spec/wiki/timerloggedout-spec/termux-monorepo)
- Public DeepWiki (if indexed): [deepwiki.com/timerloggedout-spec/termux-monorepo](https://deepwiki.com/timerloggedout-spec/termux-monorepo)

This GitHub Wiki is kept in-repo under `wiki/` and published by `.github/workflows/publish-wiki.yml` on every push that touches `wiki/**`.

---

## TL;DR

Multi-agent build and operations monorepo for the Termux / Android ecosystem: a fleet of specialist GitHub App identities and AI collaborators works the repo under one governance entry, with an ICM system map for change impact, a provider plane for model access, and live programs for competitions and certifications.

- Start at the root `README.md` navigation ladder; the primary collaborator entry is root `CLAUDE.md`.
- Prefer the **ICM system map** (`docs/icm/`) for "what is this / what else moves" questions and **ArchWiz indices** for tool-level truth (see [Navigation](Navigation)).
- Core surfaces: `docs/icm/` (system map), `docs/ops/` (operations estate), `llm_api_hub/` (provider plane), `archwiz/` (cockpit + indices), `apps/`, `.github/workflows/` (dual-gate CI).

---

## Quick links

| Page | Purpose |
|------|---------|
| [Architecture](Architecture) | Ecosystem layout and main components |
| [Navigation](Navigation) | SSOT ladder + where to start for a task |
| [DeepWiki-Mirror](DeepWiki-Mirror) | How this mirror is maintained |

---

## Status

Refreshed 2026-11-01 from current master sources (root README ladder, `docs/icm/CONTEXT.md`, `archwiz/TOOL_INDEX.md`). Initial seed was 2026-08. Re-export pages from Devin DeepWiki into `wiki/*.md` and push to `master` to refresh further; when this wiki and the repository disagree, the repository source wins.
