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

## Core loop (every `/continue` / BIUDL cycle)

1. **Pull live state**
   - `github___list_commits` master (latest 5–10)
   - `github___list_pull_requests` open, sort=updated desc
   - Key issues (`#175` priority matrix, `#522` backfill, `#265` Manus)
   - Critical path reads when needed

2. **Validate gates**
   - Candidate PRs: `get` + `get_check_runs`
   - Require dual-gate success before merge
   - Dirty / conflicted → **HOLD** or **extract** on fresh branch from master

3. **Triage**
   - Prefer: security/perf 1–5 file extracts, docs stubs, admission fixes
   - HOLD: mega-PRs (#523, #527, #142, …), staging-base, conflicted wholesale
   - Extract method: re-read master file → apply intent-only delta → new branch → dual-gate → squash

4. **Act**
   - Squash-merge only when dual-gate green + scope clean
   - Update this skill / inventory when process improves
   - Leave trail in commits and project memory

5. **Adaptive WAIT**
   - Align with `adaptive-feedback-cycle` + `production-reconciliation`
   - Stall classes: admission / queue / execution / effect / pagination / routing loop
   - Multi-pass: re-poll after disposition before closing cycle

6. **Feed forward**
   - Record durable facts in project memory
   - Update skill body when operator corrects or a new reusable rule appears

## Current production anchors (refresh on each cycle)

| Item | State (2026-09-15) |
|------|--------------------|
| Master HEAD | `39b35549` (#534) |
| Codespace agent lane | #530 + #531 MERGED |
| AGENTS→CLAUDE fold | #488 + #534; CLAUDE.md primary |
| Skills inventory | `docs/ops/SKILLS-INVENTORY.md` |
| Backfill admission | schedule `23 * * * *` on `context-relationship-backfill.yml`; default page **2** (stalled since 2026-08-19) |
| #526 audit | Landed; Tanka abandoned temporary quota — findings valid |
| HOLD mega | #523, #527, #142, #455 conflicted, staging #48 |
| Dual gates | `agentic termux smoke` + `hygiene + portability gate` |

## P0 classification

| Class | Signal | Action |
|-------|--------|--------|
| workflow-failure | high failure % × volume | rerun failed jobs / disposition |
| gate-failure | smoke/hygiene red | fix extract or hold |
| admission-stall | 0 runs on scheduled workflow | add schedule or dispatch (done for backfill) |
| comment-loop / self-trigger | bot↔bot issue_comment storms | observe; Tier-4 workflow fix |
| security | path traversal, Dependabot | extract fix + dual-gate |
| dirty-mega | 20+ files / thousands of lines | extract-only |

## Extract recipe (conflicted or dirty PR)

1. Do **not** force-update conflicted branch.
2. `create_branch` from current **master**.
3. `get_file_contents` of target path on **master**.
4. Apply **intent-only** delta (no catalog/generated churn).
5. Open PR → adaptive WAIT for dual-gate → squash-merge.
6. Leave original PR open as superseded-candidate.

## Manus / external

- Park until restore window. Newest Drive `.manustask` is operator-managed.
- Do not block monorepo extracts on external quota.

## Anti-patterns

- Wholesale merge of dirty/conflicted PRs
- Closing cycle without dual-gate evidence
- Treating `AGENTS.md` as primary entry
- Sleep-only WAIT with no concurrent useful work
- Acting on quota_cooldown / provider-control as if real_review
- Duplicating skill content only in chat — **always commit to master**

## Skill maintenance

When process improves: edit **both** canonical paths in one PR, merge to master, so every session (this chat, Codespaces, other Grok threads) loads the same skill from the repo.
