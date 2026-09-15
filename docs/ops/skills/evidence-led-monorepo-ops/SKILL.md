# Skill: evidence-led-monorepo-ops

**Owner:** ArchW1z / Grok Administrator continuous admin on timerloggedout-spec/termux-monorepo.

**Triggers:** priority matrix, master gates, SHE progress, Manus/provider RE, dirty PR triage, Actions hygiene, `continue`, `BIUDL`, `maximize actions`, `/continue`, full telemetry, multi-P0.* handling.

**Canonical paths (keep in sync):**
- `.agents/skills/evidence-led-monorepo-ops/SKILL.md` ← **agent load path**
- `docs/ops/skills/evidence-led-monorepo-ops/SKILL.md` ← human/docs mirror
- `docs/ops/SKILLS-INVENTORY.md` ← full skill table + adaptive WAIT

**Complements:** `adaptive-feedback-cycle`, `review-loop`, `production-reconciliation`, `context-relationship-graph`, `termux-monorepo-agentic-governance`.

**Posture (non-negotiable):** evidence over anecdote; extract-only; dual-gate before merge; adaptive WAIT after dispatch/commit; authority > ranking; thin stacked PRs; `Agent-Identity: Grok (Administrator)` on dispositions.

## Core loop (every `/continue` / BIUDL cycle)

1. Pull live master commits, open PRs, key issues, and critical-path files.
2. Validate candidate PRs with checks; dirty/conflicted → HOLD or extract from fresh master.
3. Triage toward focused security/perf/docs/admission increments; avoid mega-PR wholesale merges.
4. Act only on the smallest evidence-backed intent; update skill/inventory when process improves.
5. **Adaptive WAIT:** re-check jobs → steps → logs → artifacts; do concurrent useful work; never treat `queued`/`in_progress` as terminal.
6. Feed forward durable facts and repeat the cycle.

## P0 classification

| Class | Signal | Action |
|-------|--------|--------|
| workflow-failure | high failure % × volume | rerun failed jobs / disposition |
| gate-failure | smoke/hygiene red | fix extract or hold |
| admission-stall | 0 runs on scheduled workflow | add schedule or dispatch |
| comment-loop / self-trigger | bot↔bot issue_comment storms | observe; Tier-4 workflow fix |
| reviewer-noise | quota/billing/availability/status chatter without task failure | classify as provider-state telemetry; do not promote to code failure |
| security | path traversal, Dependabot | extract fix + dual-gate |
| dirty-mega | 20+ files / thousands of lines | extract-only |

## Retroactive benchmark and reviewer-noise rule

**#390 is a benchmark specimen, not a historical boundary.** Preserve it as the canonical regression case for comment-loop/self-trigger analysis while continuously evaluating later and earlier GitHub objects. #509 operationalized the lesson as a retroactive-review process; its merged change is part of the historical evidence corpus.

For every retrospective slice, classify automation-generated activity before interpreting volume as failure:

- `actionable_finding`: evidence-backed defect or process gap tied to a reproducible condition.
- `provider_state`: quota, billing, unavailable integration, permission, or rate-limit state.
- `reviewer_noise`: informational/status output that does not establish a repository defect or failed task.
- `execution_failure`: a task/run actually started and failed, with bound run/step evidence.
- `not_executed`: admission, availability, cooldown, quota, or routing prevented execution; **never relabel this as `execution_failure`**.
- `self_trigger_candidate`: a reactive listener plus a matching self-posting path; do not flag read-only listeners merely because they consume comments.

When evaluating #390-like behavior, correlate issue comments, review submissions/comments, workflow runs, jobs/steps, artifacts, commits, PRs, and actor/provider state by immutable IDs plus SHA/ref and timestamps. Detect causal loops and repeated automation without allowing reviewer/provider chatter to contaminate effectiveness metrics.

Retroactive review is **continuous**, with periodic sampling as a backstop; it must not wait for an overflow issue such as #507. New findings feed the historical correlation ledger, Context Relationship Graph, Effectiveness Ledger, and subsequent BIUDL/Scout evaluation rather than generating duplicate noise issues for already-classified provider state.

## Extract recipe (conflicted or dirty PR)

1. Do not force-update conflicted branch.
2. Create a branch from current **master**.
3. Re-read target path on master.
4. Apply intent-only delta; no catalog/generated churn.
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
- Duplicating skill content only in chat — **always commit to master**

## Skill maintenance

When process improves: edit **both** canonical paths in one PR, merge to master, so every session loads the same skill from the repo.
