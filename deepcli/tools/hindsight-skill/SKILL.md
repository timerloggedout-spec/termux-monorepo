---
name: hindsight-memory-architect
description: Expert agent skill for Hindsight by Vectorize.io - retain/recall/reflect semantics, deployment footprints, framework mapping, diagnostics.
---

# Hindsight Memory Architect

Hindsight is a long-term memory engine for autonomous agents. It combines a
hybrid TEMPR retrieval stack (Temporal, Embedding, Match-keyword,
Parallel-graph, Reasoned) with contextual consolidation.

## Core operations

1. Retain - feed raw context, not pre-summarized strings.
2. Recall - parallel search fused via RRF + cross-encoder. Query before
   any architectural decision or git-mutating action.
3. Reflect - asynchronous consolidation deduplicates experience facts,
   surfaces stale data, compiles Observations from Mental Models.

## Three-tier hierarchy (reflect priority)

- Mental Models - user-curated pre-computed reflections, source_query + tags
- Observations - auto-consolidated beliefs from 2+ facts, refined over time
- Raw Facts - individual memory_units, ground truth

## Deployment

- Cloud: https://api.hindsight.vectorize.io
- Local: http://localhost:8888
- Config: ~/.hindsight/config (mode 600)

## Framework skill paths

- Claude Code: ~/.claude/skills/{name}/SKILL.md
- Codex / Gemini / Cursor: ~/.codex/skills/{name}/SKILL.md
- Kiro: ~/.kiro/skills/{name}/SKILL.md
- Factory Droid: ~/.factory/skills/{name}/SKILL.md

## Python client

    from hindsight_client import Hindsight
    client = Hindsight(base_url="http://localhost:8888")
    client.retain(bank_id="termux-monorepo::primary", content="...")
    hits = client.recall(bank_id="termux-monorepo::primary", query="...")

## CLI

    memory retain <bank-id> "<context>"
    memory recall <bank-id> "<query>"
    memory reflect <bank-id> "<topic>"

## Diagnostics

1. Verify SKILL.md path matches framework directory.
2. Re-run: npx add-skill vectorize-io/hindsight --skill hindsight-docs
3. Validate ~/.hindsight/config - no trailing whitespace.
4. /hindsight-upgrade inside interactive sessions.

## Termux-monorepo integration

- Primary bank: termux-monorepo::primary
- MVT lanes: termux-monorepo::mvt::vendor::family::model::settings::role::comp
- DeepAgent reach: agent_hindsight.retain_async() - sync HTTP, env-gated
- Lifecycle tools: deepcli/tools/hindsight-lifecycle/
- Live state: hs-dash (dashboard sections in dashboard/sections/)

## References

- https://github.com/vectorize-io/hindsight-skills
- https://vectorize.io
- https://www.getclaudeskills.com/skills/hindsight-memory-architect-vectorize-io
