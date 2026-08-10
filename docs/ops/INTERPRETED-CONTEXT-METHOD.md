# Interpreted Context Method — scaffold (MVP)

**Status:** stub → living scaffold. Needs template references from the monorepo and `refTemplates/`.

## Intent

Build **minimized, role-aware context bundles** for agent prompts so free-tier runs stay high-signal:

```text
raw sources → interpret/filter → role lens → mandatory phrases → task slice → prompt
```

## Current MVP (exists in tree)

| Piece | Location | Role |
|-------|----------|------|
| Agent contract | `AGENTS.md` | Global rules |
| Gemini contract | `GEMINI.md` | Triage/review residual |
| Role snippets | `docs/ops/prompts/*.md` | Per-roster initial context |
| Mandatory phrases | `docs/ops/MANDATORY-PHRASES.md` | Must-include seeds |
| Work-context key | Actions cache `.agent-context/` | PR continuity (#145) |
| AST skeleton collector | `termux-multi-agent` / provision paths | Dependent-file skeletons |
| refTemplates library | `refTemplates/` (01_Agent_Runtime, …) | External pattern mine |

Historical note: `07_Prompt_Context/Interpreted-Context-Methodology` appears in recon maps; treat as **seed name** — prefer this doc + `refTemplates` over resurrecting broken paths.

## Desired upgrade path

1. **Inventory** templates under `refTemplates/**` and any `Interpreted*` forks (#96 researcher track).
2. Define a single **bundle schema** (YAML/JSON) with sections: `role`, `phrases`, `context_key`, `disposition`, `files`, `task`.
3. Wire builders:
   - GHA: auto-jules / continuous-ops / gemini-invoke
   - Local: multi-agent orchestrator context_collector
4. Round-trip test: bundle → prompt → (optional compress Grimoire) → expand without loss of mandatory phrases.
5. Encrypt at rest only after #120 durable store; until then **viewable text** on public demo is policy.

## Anti-patterns

- Dumping full analysis-chain transcripts into the builder prompt
- Mixing Class 3/4 session material into bundles
- Letting continuous maintenance (#150) append unbounded “related projects” lists into every prompt

## Related

- [`ROLE-PROMPT-PIPELINE.md`](ROLE-PROMPT-PIPELINE.md)
- [`CODERABBIT-EXCERPT-POLICY.md`](CODERABBIT-EXCERPT-POLICY.md)
- #96 · #118 · #120 · #145 · #146

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-interpreted-context
