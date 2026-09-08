# ADE ↔ Kai-9000 — split & unified-interface provenance

> **Operator clarifications (2026-08-23, #48):**
> 1. **Product / unified-UI name lineage:** [SimonSchubert/Kai](https://github.com/SimonSchubert/Kai) ("Kai 9000") is primary for multi-platform assistant surface inspiration, with Haven, codex-termux, Hermes Agent Fork, Conduit, and further Operator-listed forks.
> 2. **Orchestrator skill/MCP template lineage remains valid:** [romanyukzhenya82-sketch/kai9000-orchestrator](https://github.com/romanyukzhenya82-sketch/kai9000-orchestrator) and local [timerloggedout-spec/kai9000-orchestrator_fork](https://github.com/timerloggedout-spec/kai9000-orchestrator_fork) are **correlated reference inspiration submodule templates** (skills, MCP configs, workflows, system-prompt layers) — not discarded.
>
> Goal: a **unified interface that includes everything**.

## Template / inspiration inventory (SSOT for agents)

### A. Unified UI / product surface

| Source | Role |
|--------|------|
| **[SimonSchubert/Kai](https://github.com/SimonSchubert/Kai)** | Primary **Kai 9000** multi-platform AI assistant template (Android/iOS/desktop/web, persistent memory, multi-provider) |
| **[GlassHaven/Haven](https://github.com/GlassHaven/Haven)** | Mobile workspace: terminal, remote desktop, files, on-device Linux, consent-gated agent/MCP bridge (F-Droid path) |
| **[DioNanos/codex-termux](https://github.com/DioNanos/codex-termux)** | Termux ↔ Codex integration patterns (and related termux forks Operator tracks) |
| **Hermes Agent Fork** (F-Droid) | Mobile UI agent surface Operator already runs |
| **Conduit** (+ additional Operator-listed forks) | Mesh / transport / companion surfaces |

### B. Orchestrator / skill-MCP submodule templates (correlated — still valid)

| Source | Role |
|--------|------|
| **[romanyukzhenya82-sketch/kai9000-orchestrator](https://github.com/romanyukzhenya82-sketch/kai9000-orchestrator)** | Upstream **submodule template** for multi-agent orchestrator skills, MCP layouts, workflows, Zero-Law-style prompt layers |
| **[timerloggedout-spec/kai9000-orchestrator_fork](https://github.com/timerloggedout-spec/kai9000-orchestrator_fork)** | Operator **correlated fork** of the above — preferred pin target for selective sparse / gitlink recipes |

Use B for **selective harvest** (skills, MCP templates, non-crypto workflows). Use A for **unified UI / product surface** patterns. Both tracks feed the same monorepo; neither replaces the other.

## Principle (unchanged)

| Slice | Where | What |
|-------|--------|------|
| **ADE (dev)** | Monorepo root / `ade-kai9000/` | Coding skills, MCP templates (github/filesystem/sqlite), system-prompt core (Zero Law, RED TEAM, non-crypto subagents), Linear/archwiz workflows — harvest from orchestrator_fork as needed |
| **Crypto / trading product** | `_1-Projects/a/kai9000-crypto/` | Hermes trading, portfolio monitors, exchange MCP, crypto-oracle prompt layers — **reference / sparse only** |
| **Unified UI / mobile** | Inspired by Kai + Haven + Hermes Agent + Conduit | Termux-first; model plane still routes through hub |

`_1-q_f/` is **not** used for this pointer. Use **`_1-Projects/a/`** for crypto sparse layout.

## ADE import set

**In** (dev) — prefer selective import from `kai9000-orchestrator_fork`:

- Skills: mcp-builder, skill-creator, agent-architect, product-builder-loop, doc skills if not already local
- System prompts stripped of mandatory crypto monitoring
- MCP templates: github, filesystem, sqlite (Termux-aware paths)
- Generic workflows → Linear / TER research issues

**Out** (crypto track only — sparse pointer):

- `integrations/hermes/**` trading agents
- crypto-portfolio-monitor skill
- binance/polymarket MCP entries
- morning_crypto_brief / tdd_crypto_loop as-is

## Crypto pointer layout

```
_1-Projects/a/kai9000-crypto/
  README.md          # how to clone/sparse + which upstream
  SOURCE.txt         # pinned URL + SHA (not full tree)
```

Do **not** full-recursive submodule entire external orchestrators into monorepo root. Prefer sparse depth-1, gitlink pins, or documented pointers (same pattern as `lego_fork` / `batteries_fork` inventory). **`kai9000-orchestrator_fork` is an approved correlated template** for those recipes.

## Model plane

All tracks call **`llm_api_hub` / `multi-ai-cli`**, not raw provider keys in ADE skill env.

## Status

- [x] Split documented
- [x] Unified-UI provenance: SimonSchubert/Kai + Haven + codex-termux + Hermes/Conduit
- [x] **Orchestrator fork restored as correlated submodule template** (Operator follow-up)
- [ ] `_1-Projects/a/kai9000-crypto/README.md` + SOURCE.txt refresh against chosen pins
- [ ] ADE skill import PR (selective from orchestrator_fork)
- [ ] Unified UI integration plan (Kai/Haven patterns → ArchWiz / Termux surface) — track under proposals, not silent sprawl
- [ ] NexusCLI / agents remain hub-retargeted (#240 mega on staging)

## Related

- PR #48 (HOLD — dirty; residue folds into #240)
- PR #240 hub + ML ingestion mega
- PR #330 provenance pass; this follow-up restores orchestrator correlation
- Trunk: `docs/ops/MINTLIFY.md`, Notation Sets `4520c2c`, archwiz-ui-protocol #329
