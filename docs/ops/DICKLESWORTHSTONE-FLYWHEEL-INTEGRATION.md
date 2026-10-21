# Dicklesworthstone Flywheel Stack — Integration and Upgrade Plan

**Status:** Active integration lane; reference metadata landed on feat/dicklesworthstone-flywheel-stack.  
**Upstream checked:** 2026-10-21.  
**Primary sources:** https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup and https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup/blob/main/docs/methodology/THE_FLYWHEEL_CORE_LOOP.md.

## Executive status

The upstream project is a maintained, broad bootstrap stack (currently documented as ACFS 0.7.0) for Ubuntu 22.04+ and Arch/Omarchy, not a drop-in Termux package. Its own methodology recommends starting with Agent Mail + Beads Rust (br) + Beads Viewer (bv) as the minimal operating loop, then adding supporting tools when they solve a demonstrated gap.

**Project status before this change:** refTemplates had continuous-evaluation scaffolding and several unrelated live smods pins, but no explicit ACFS/Flywheel source slot or integration contract. Search found no ACFS setup repository pin in .gitmodules.

**This change:** adds a source-tracked metadata slot and a project-specific adoption contract. It deliberately does not run upstream installers, create a broken gitlink to a nonexistent project fork, or claim that the full stack is deployed. A custom fork and live gitlink remain a separate gated step.

## Stack layers and disposition

| Layer | Upstream capability | Project disposition | Acceptance evidence before runtime adoption |
|---|---|---|---|
| 0 — Plan | Multi-model plan, written design, explicit acceptance criteria | Reuse repository proposal/ITEMS.md and PR contracts | Task has scope, owner, tests, rollback |
| 1 — Task graph | Beads Rust br | Evaluate as adapter to existing issue/PR/task tracking; do not create a competing canonical ledger | Export/import round-trip, dependency semantics, no duplicate source of truth |
| 1 — Triage | Beads Viewer bv | Evaluate as read-only prioritization over task graph | Deterministic input, explainable ranking, no mutation during triage |
| 1 — Coordination | MCP Agent Mail | Compare with existing Agent Mail composite/action and coordination contracts before adding another service | Identity/provenance, idempotent handoffs, lease expiry, conflict test |
| 2 — Safety | DCG + SLB | Map to existing destructive-command guard and permission/approval boundaries | Deny tests for destructive commands; explicit fail-closed behavior |
| 2 — Orchestration | NTM / tmux fleet | Optional interactive operator surface; not a replacement for GitHub Actions | Termux and Linux compatibility tests; no hidden background process |
| 2 — Memory/search | CASS + CASS Memory | Optional indexed evidence/search adapter | Privacy-safe indexing, deletion/retention contract, measured retrieval quality |
| 3 — Bootstrap | ACFS installer | Reference-only; never execute wholesale in Termux, CI, or a project workspace | Disposable container, pinned SHA/tag, reviewed install manifest and rollback |
| 3 — Extra tools | Other ACFS utilities | Adopt individually, only for a measured capability gap | Provenance, license, maintenance, security and footprint review |

## refTemplates/*smods* rule

The reference profile lives under refTemplates/15_Research_Repo_Templates/. Executable/customized pins belong under refTemplates/smods/<name>_fork/ only after the following are true:

1. A real timerloggedout-spec/<name>_fork repository exists; never write a speculative URL into .gitmodules.
2. The fork has a minimal, documented delta from upstream and an upstream remote/commit recorded.
3. Only source needed for the intended capability is retained; generated assets, caches, model weights, session histories, and build outputs are excluded unless a documented test needs them.
4. The gitlink is shallow and pinned to a reviewed commit. Mutable branch tracking is not an update policy.
5. Inventory, submodule integrity, security checks, repo gate, and Termux smoke pass. Platform-incompatible tools remain metadata-only or container-only.
6. An upgrade updates the fork first, records upstream-to-fork diff and compatibility evidence, then updates the gitlink in a separate attributable change.

## Recommended implementation order

1. **Now — inventory and mapping:** completed by this reference slot and integration contract.
2. **Next — capability overlap audit:** compare Agent Mail, task tracking, command safety, and orchestration with existing project components; nominate one source of truth per capability.
3. **Then — core-loop proof:** in a disposable Linux container, run a small task from plan → bead/dependencies → triage → coordinated agent claim → tests → recorded outcome.
4. **Then — selective fork:** fork only the component(s) with demonstrated net benefit; keep upstream updates reproducible.
5. **Then — runtime pin:** add the shallow gitlink under refTemplates/smods/, extend inventory/CI checks if needed, and prove dual gates plus task outcome.
6. **Finally — measured rollout:** collect integration time, collisions, retries, task acceptance, footprint, and operator interventions. Do not promote based on stars, tool count, or installer success alone.

## Security and compatibility guardrails

- Never run curl | bash as the integration test.
- Never run ACFS --mode vibe in project automation.
- Pin every external executable to a tag or immutable commit.
- Do not import secrets, shell profiles, agent auth files, private histories, or personal machine state.
- No automatic update of smods gitlinks without compatibility tests and the dual gate.
- Treat Ubuntu/Arch support as upstream claims; Termux/Android support requires its own observed tests.
- Keep task graph, coordination messages, telemetry, and source code as separate data planes; avoid duplicating existing ledgers.

## Verification checklist for this PR

- [ ] Source metadata slot contains README.md and SOURCE.txt.
- [ ] SOURCE-MAP.md and index point to the new slot.
- [ ] python3 scripts/ci/refTemplates_inventory.py --strict passes.
- [ ] python3 scripts/ci/repo_gate.py passes.
- [ ] python3 scripts/ci/termux_smoke.py passes.
- [ ] No upstream installer executed; no live gitlink added until a real customized fork exists.

**Truthful completion boundary:** documentation/reference integration is not equivalent to a deployed Flywheel stack. Runtime adoption is gated on the evidence above.
