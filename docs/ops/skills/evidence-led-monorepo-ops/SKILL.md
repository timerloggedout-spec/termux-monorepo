---
name: evidence-led-monorepo-ops
description: Continuous evidence-led admin ops on timerloggedout-spec/termux-monorepo (and similar agentic monorepos). Triggers on priority matrix, master gates, SHE progress, Manus/provider RE, dirty PR triage, Actions hygiene, or when the operator says continue, BIUDL, maximize actions, or /continue. Use for live state pulls, dispositions, small-green extracts, adaptive WAIT, and iterative process improvement documented as skills. Load this skill in every admin session.
---

# Skill: evidence-led-monorepo-ops

**Owner:** ArchW1z / Grok Administrator continuous admin on timerloggedout-spec/termux-monorepo.

**Triggers:** priority matrix, master gates, SHE progress, Manus/provider RE, dirty PR triage, Actions hygiene, `continue`, `BIUDL`, `maximize actions`, `/continue`, full telemetry, multi-P0.* handling.

**Canonical paths (keep in sync):**
- `.agents/skills/evidence-led-monorepo-ops/SKILL.md` ← **agent load path**
- `docs/ops/skills/evidence-led-monorepo-ops/SKILL.md` ← human/docs mirror
- `docs/ops/SKILLS-INVENTORY.md` ← full skill table + adaptive WAIT

**Complements:** `adaptive-feedback-cycle`, `review-loop`, `production-reconciliation`, `context-relationship-graph`, `termux-monorepo-agentic-governance`.

**Primary agent entry:** `CLAUDE.md` (not `AGENTS.md` — Linguist stub only).

## Posture (non-negotiable)

- **Evidence over anecdote.** Cite live SHAs, check runs, run histories, or committed artifacts.
- **Extract-only.** Never wholesale-merge dirty mega-PRs. One intent per PR.
- **Dual-gate before merge.** `agentic termux smoke` + `hygiene + portability gate` (or `repo_gate` + `termux_smoke`).
- **Adaptive WAIT.** After dispatch/commit: re-check jobs→steps→logs→artifacts. Do concurrent non-conflicting work. Do not treat `queued`/`in_progress` as terminal.
- **Authority > ranking.** MoneyBall/3L0 are decision-support only.
- **Anti-sprawl.** Thin stacked PRs. No L0 source mutation without authority.
- **Identity.** `Agent-Identity: Grok (Administrator)` on dispositions.
- **Extra-red ≠ dual-gate.** Dual-gate green plus `validate-pull-request` / `validate-registry` red → HOLD wholesale; extract intent only.
- **Behind-master dual-gate green ≠ auto-merge.** Rebase/extract onto current master first.

## Core loop (every `/continue` / BIUDL cycle)

1. **Pull live state** — commits, open PRs, #175 / #522 / #265, critical paths.
2. **Validate gates** — require dual-gate success; ignore skipped `issue_comment` listeners.
3. **Triage** — prefer 1–5 file security/perf/docs/skill extracts; HOLD megas.
4. **Act** — squash only when dual-gate green + scope clean + no extra-red on same intent.
5. **Adaptive WAIT** — stall classes including comment-storm-skip.
6. **Feed forward** — commit skill/inventory; do not leave SSOT in chat only.

## Current production anchors (refresh on each cycle)

| Item | State (2026-09-16T20:15Z) |
|------|--------------------|
| Master HEAD | `abdd7925` (#555 squash; prior `7f5c78d2` #554, `921f532c` #553) |
| Landed extracts | #553 colab-cli security; #554 lag-index keywords; #555 skill anchors |
| Codespace agent lane | #530 + #531 MERGED; #545 multi-lane **HOLD** |
| AGENTS→CLAUDE fold | #488 + #534; CLAUDE.md primary |
| Skills inventory | `docs/ops/SKILLS-INVENTORY.md` |
| Backfill admission | schedule `23 * * * *`; default page **2** (stalled since 2026-08-19); scheduled backfill in_progress on `abdd7925` |
| HOLD mega | #523, #527, #142, #455 conflicted, staging #48 |
| Superseded-candidates | #550 colab-cli; #551 lag-index (intent landed via #553/#554) |
| Extra-red HOLD | #549 ML rebase (#175): dual-gate green, `validate-pull-request` + `validate-registry` red; #432 dirty sibling |
| #543 / #545 | skill-quality + multi-lane HOLD |
| Dual gates | smoke + hygiene; skipped `issue_comment` is not evidence |
| Master scheduled | Context Relationship audit success on `abdd7925`; comment-storm-skip on Gemini/DeepSeek/Jules |

## P0 classification

Includes `reviewer-noise` and `comment-storm-skip`. #390 is a benchmark specimen. `not_executed` is never `execution_failure`.

## Extract recipe

1. Do **not** force-update conflicted branch.
2. `create_branch` from current **master**.
3. Re-read target path on master; apply intent-only delta.
4. Open PR → adaptive WAIT dual-gate → squash.
5. Leave original as superseded-candidate.

## Manus / external

Park until restore window. Do not block monorepo extracts on external quota.

## Anti-patterns

- Wholesale merge of dirty/conflicted/behind-master PRs
- Closing cycle without dual-gate evidence
- Treating skipped `issue_comment` listeners as dual-gate results
- Chat-only skill content

## Skill maintenance

Edit **both** canonical paths + inventory in one PR, dual-gate, squash to master.
