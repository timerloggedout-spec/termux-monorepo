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
   - Dirty / conflicted / behind-master with extra failures → **HOLD** or **extract** on fresh branch from master
   - Ignore `issue_comment` skipped listeners when scoring gates

3. **Triage**
   - Prefer: security/perf 1–5 file extracts, docs stubs, admission fixes, skill-anchor refresh
   - HOLD: mega-PRs (#523, #527, #142, …), staging-base, conflicted wholesale
   - Extract method: re-read master file → apply intent-only delta → new branch → dual-gate → squash

4. **Act**
   - Squash-merge only when dual-gate green + scope clean
   - Update this skill / inventory when process improves
   - Leave trail in commits and project memory

5. **Adaptive WAIT**
   - Align with `adaptive-feedback-cycle` + `production-reconciliation`
   - Stall classes: admission / queue / execution / effect / pagination / routing loop / comment-storm-skip
   - Multi-pass: re-poll after disposition before closing cycle

6. **Feed forward**
   - Record durable facts in project memory
   - Update skill body when process improves or a new reusable rule appears

## Current production anchors (refresh on each cycle)

| Item | State (2026-09-16T06:08Z) |
|------|--------------------|
| Master HEAD | `6df9b66a` (#547 anchor refresh; prior `97c66653` #546, `5134b6a7` #542/#541/#524) |
| Codespace agent lane | #530 + #531 MERGED; #545 multi-lane **HOLD** (hygiene red, smoke green, base `5134b6a7`) |
| AGENTS→CLAUDE fold | #488 + #534; CLAUDE.md primary |
| Skills inventory | `docs/ops/SKILLS-INVENTORY.md` |
| Backfill admission | schedule `23 * * * *` on `context-relationship-backfill.yml`; default page **2** (stalled since 2026-08-19) |
| #526 audit | Landed; Tanka abandoned temporary quota — findings valid |
| HOLD mega | #523, #527, #142, #455 conflicted, staging #48 |
| Behind-master / extract | #543 skill-quality HOLD; #544 superseded by #546; #545 hygiene HOLD |
| Dual gates on `6df9b66a` | Prior extract dual-gate green on `954e2022` before squash; do not use skipped `issue_comment` runs as gate evidence |
| Immediate-fail / skip master runs | `swe-reference-evaluation`, `historical-evaluation-correlation`, `agent-jules-on-issues`, `actions-run-watcher` immediate-fail → `not_executed` until logs prove execution; Gemini/DeepSeek/ECC/Jules `issue_comment` **skipped** → `comment-storm-skip` |

## P0 classification

| Class | Signal | Action |
|-------|--------|--------|
| workflow-failure | high failure % × volume | rerun failed jobs / disposition |
| gate-failure | smoke/hygiene red | fix extract or hold |
| admission-stall | 0 runs on scheduled workflow | add schedule or dispatch (done for backfill) |
| comment-loop / self-trigger | bot↔bot issue_comment storms | observe; Tier-4 workflow fix |
| comment-storm-skip | many skipped listeners on master SHA | `not_executed` + `reviewer_noise`; do not merge or revert on that signal |
| reviewer-noise | quota/billing/availability/status chatter without a task failure | classify as provider-state telemetry; do not promote to code failure |
| security | path traversal, Dependabot | extract fix + dual-gate |
| dirty-mega | 20+ files / thousands of lines | extract-only |

## Retroactive benchmark and reviewer-noise rule

**#390 is a benchmark specimen, not a historical boundary.** Preserve it as the canonical regression case for comment-loop/self-trigger analysis while continuously evaluating later and earlier GitHub objects. #509 operationalized the lesson as a retroactive-review process; its merged change is part of the historical evidence corpus.

For every retrospective slice, classify automation-generated activity before interpreting volume as failure:

- `actionable_finding`: evidence-backed defect or process gap tied to a reproducible condition.
- `provider_state`: quota, billing, unavailable integration, permission, or rate-limit state.
- `reviewer_noise`: informational/status output that does not establish a repository defect or failed task.
- `execution_failure`: a task/run actually started and failed, with bound run/step evidence.
- `not_executed`: admission, availability, cooldown, quota, routing, or **skipped listener** prevented execution; **never relabel this as `execution_failure`**.
- `self_trigger_candidate`: a reactive listener plus a matching self-posting path; do not flag read-only listeners merely because they consume comments.

When evaluating #390-like behavior, correlate issue comments, review submissions/comments, workflow runs, jobs/steps, artifacts, commits, PRs, and actor/provider state by immutable IDs plus SHA/ref and timestamps. Detect causal loops without allowing reviewer/provider chatter to contaminate effectiveness metrics.

Retroactive review is **continuous**, with periodic sampling as a backstop; it must not wait for an overflow issue such as #507. New findings feed the historical correlation ledger, Context Relationship Graph, Effectiveness Ledger, and subsequent BIUDL/Scout evaluation rather than generating duplicate noise issues for already-classified provider state.

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
- Treating ECC-tools/Codex/Qodo status chatter as independent task failures without execution evidence
- Treating skipped `issue_comment` listener runs as dual-gate results
- Duplicating skill content only in chat — **always commit to master**

## Skill maintenance

When process improves: edit **both** canonical paths in one PR, merge to master, so every session (this chat, Codespaces, other Grok threads) loads the same skill from the repo.
