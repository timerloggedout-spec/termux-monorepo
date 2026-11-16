# Dicklesworthstone Flywheel Stack — Integration and Upgrade Plan

**Status:** Reference integration merged in PR #1460; repository-native validation adapter merged in PR #1467. ACFS upstream runtime remains metadata-only pending component-specific adoption evidence.
**Upstream checked:** 2026-10-21.
**Primary sources:** https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup and https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup/blob/main/docs/methodology/THE_FLYWHEEL_CORE_LOOP.md.

## Executive status

The upstream project is a maintained, broad bootstrap stack (currently documented as ACFS 0.7.0) for Ubuntu 22.04+ and Arch/Omarchy, not a drop-in Termux package. Its own methodology recommends starting with Agent Mail + Beads Rust (br) + Beads Viewer (bv) as the minimal operating loop, then adding supporting tools when they solve a demonstrated gap.

**Project status before this change:** refTemplates had continuous-evaluation scaffolding and several unrelated live smods pins, but no explicit ACFS/Flywheel source slot or integration contract. Search found no ACFS setup repository pin in .gitmodules.

**PR #1460 (merged):** added a source-tracked metadata slot and a project-specific adoption contract. Its strict inventory, repository gate, and Termux smoke checks passed on the PR head. It deliberately does not run upstream installers, create a broken gitlink to a nonexistent project fork, or claim that the full stack is deployed. A custom fork and live gitlink remain a separate gated step.

**Executable follow-up (THUB-010, PR #1467 merged):** [`FLYWHEEL-RUNTIME.md`](FLYWHEEL-RUNTIME.md) documents `scripts/agentic/flywheel.py`: a repository-native dependency/triage/handoff/validation loop with versioned provenance receipts and CI coverage. This makes the local adoption lane executable while retaining all upstream adoption gates below. It does not install Agent Mail, br/bv or ACFS, post Delphi feedback, or deploy a live service.

## Repository-wide Flywheel audit (2026-10-21)

The repository search for `flywheel` surfaced two related but distinct systems. The ACFS reference stack must be integrated *with* these existing project control planes, not mistaken for them or allowed to replace them.

| Existing surface found | What already exists | Required integration treatment |
|---|---|---|
| `scripts/delphi/gate.py`, `ops/delphi/panel.json`, `tests/test_delphi_gate.py`, `.github/workflows/delphi-gate.yml` | A real outcome-feedback flywheel: confirmed/missed outcomes update role `gate_pass_rate` (EWMA alpha 0.2) and Elo (K=16) in the append-only Delphi panel weights ledger; changed weights re-score pending RFPs. | Preserve this as the authoritative **decision-quality feedback loop**. Add no parallel weights ledger. Any ACFS evaluation should publish evidence through an explicitly versioned adapter/event only after a real task outcome; never fabricate outcomes or panel votes. |
| `docs/ops/DELPHI-ORACLE-RFP-GATE.md` and `docs/ops/DELPHI-LANE-CONTRACT.md` | Event-driven RFP → oracle → blind rubric panel → shadow/parked decision → confirmed/miss feedback; HindSight misses and real-run outcomes can wake the gate. | Reuse the existing event and record contracts. An ACFS component evaluation is a candidate lane, not permission to bypass quota, cost veto, shadow traffic, or promotion rules. |
| `docs/ops/ACTIONS-CADENCE-CACHE-CONTROL.md` | Camshaft/Flywheel, Cadence, and Gantt are already named as scheduling/control-plane owners; WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE governs provider-facing work. | ACFS/NTM must not become a second scheduler or circumvent cooldowns, current-SHA evidence, or idempotency. Route any automation through existing cadence controls. |
| `.deepcli/session_store/*` search matches | Session snapshots contain historical terminal transcripts mentioning a local `~/refTemplates/flywheel_intel.txt` inventory and selective-recon instructions. These are session records, not an authoritative repository implementation or a safe source artifact. | Preserve the useful design intent—selective, footprint-aware reconnaissance—but do not import raw session stores, credentials, histories, generated inventories, or machine-specific paths into the reference stack. Recreate only validated, portable findings as reviewed documentation. |

**Key distinction:** Dicklesworthstone ACFS is the upstream bootstrap/composable-tool collection; the repository's Delphi flywheel is already an outcome-driven scoring loop. The integration target is a safe capability adapter between them, not a wholesale replacement or a second flywheel control plane.

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

- [x] Source metadata slot contains README.md and SOURCE.txt.
- [x] SOURCE-MAP.md and index point to the new slot.
- [x] `python3 scripts/ci/refTemplates_inventory.py --strict` passes on PR #1460.
- [x] `python3 scripts/ci/repo_gate.py` passes on PR #1460 and PR #1467.
- [x] `python3 scripts/ci/termux_smoke.py` passes on PR #1460 and PR #1467.
- [x] No upstream installer executed; no live gitlink added without a real customized fork. ACFS runtime remains not deployed.

**Truthful completion boundary:** documentation/reference integration is not equivalent to a deployed Flywheel stack. Runtime adoption is gated on the evidence above.


## Merge and validation ledger

- PR #1460 (reference profile + repository Flywheel audit): merged at `8156e5d03679e8dd8ce7d5dc88b1891d410ac36c`.
- PR #1467 (repository-native validation adapter): merged at `d3d3cef3bb109ce47f407d99acce8e3334e65d05`. The PR reported 11 adapter tests plus 28 planner/CLI/route regressions passing; Flywheel core-loop, hygiene/portability, and agentic Termux smoke checks all passed on its reviewed head.
- This evidence validates the **local adapter and CI path only**. It does not establish native Android device compatibility, a production task outcome, deployment, or installation of upstream ACFS components.
