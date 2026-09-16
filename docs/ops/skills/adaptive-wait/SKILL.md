---
name: adaptive-wait
description: Adaptive WAIT stage for agentic GitHub ops. After any dispatch, commit, rebase, or merge request — re-check jobs/steps/logs/artifacts, do concurrent non-conflicting work, classify stalls, and only promote when dual gates + task outcome are verified. Triggers when waiting on CI, after PR open/update, during /continue cycles, or when operator says wait adaptively. Cross-session SSOT — always load from master, never chat-only.
---

# Skill: adaptive-wait

**Owner:** ArchW1z / Grok Administrator  
**Complements:** `evidence-led-monorepo-ops`, `adaptive-feedback-cycle`, `production-reconciliation`, `review-loop`

**Canonical paths (keep in sync on every change):**
- `.agents/skills/adaptive-wait/SKILL.md` ← **agent load path**
- `docs/ops/skills/adaptive-wait/SKILL.md` ← human/docs mirror
- Listed in `docs/ops/SKILLS-INVENTORY.md`

**Anti-pattern:** skill content only in chat memory. **Always commit to master.**

## Purpose

WAIT is a **methodological stage**, not sleep-only idle time. After any action that triggers GitHub Actions or changes mergeability, the agent must observe runtime evidence before classifying success, failure, or next work.

## When to load

- After `create_pull_request`, `update_pull_request_branch`, `merge_pull_request`
- After `create_or_update_file` / push that will fire workflows
- During every `/continue` · `BIUDL` · evidence-led cycle when checks are in flight
- When operator says wait, poll, or adaptive wait

## Non-negotiable rules

1. **WAIT ≠ sleep-only.** Do concurrent non-conflicting useful work while a cohort is in flight (docs extract, disposition on another PR, inventory, skill maintenance on a disjoint path).
2. **Never classify terminal from `queued` or `in_progress`.** Those are runtime states, not outcomes.
3. **Inspect before decide:** jobs → steps → logs → artifacts → receipts → resulting SHA/status.
4. **Dual-gate before promote:** `agentic termux smoke` + `hygiene + portability gate` (or repo_gate + termux_smoke). Mergeable_state alone is insufficient.
5. **Preserve provenance.** Every attempt stays addressable by SHA. Promotion selects a successor; it does not erase failed attempts.
6. **Stall is a classification, not auto-retry permission.** Record stall class before any retry policy acts.

## Stall classes

| Class | Signal |
|-------|--------|
| **admission** | Expected schedule/dispatch produced **0 runs** (e.g. backfill stuck page 2 since 2026-08-19) |
| **queue** | `queued` beyond observation window with no job admission |
| **execution** | `in_progress` with no step/log/artifact progress across watches |
| **effect** | Workflow terminal success but expected effect (commit, artifact, page advance) missing |
| **pagination** | Continuation run completes but `next_start_page` does not advance |
| **routing loop** | Same SHA/input repeatedly cancels/fails without new diagnosis |

## Procedure (every wait cohort)

```text
1. CAPTURE admission — run_id, attempt, SHA, ref, started_at, expected effect
2. WAIT — do not declare success/failure yet
3. WORK — independent non-conflicting phase (optional but preferred)
4. WATCH — re-fetch check_runs / workflow run status
5. VALIDATE — dual-gate conclusions + actual outputs, not badge alone
6. CLASSIFY — PASS | FAIL | STALLED | UNKNOWN + stall class if any
7. ACT — merge | extract | hold | retry-with-new-identity | feed-forward
8. RECORD — brief evidence in disposition / memory / skill if process learned
```

### Practical poll pattern (this environment)

```text
bash sleep 25–45s   # adaptive, not fixed dogma
github___pull_request_read method=get_check_runs
# require agentic termux smoke success + hygiene + portability gate success
# then merge or hold
```

Extend wait if still `in_progress` and logs show progress. Cap only when platform timeout or documented stall threshold is exceeded — then CLASSIFY, do not infinite-loop silently.

## Active-wait rule

While one PR's checks run:

- Preserve that cohort's immutable IDs.
- Prefer work on a **disjoint** file/branch (another extract, skill inventory, disposition comment).
- Do **not** mutate the same branch in a way that invalidates in-flight checks.
- Re-check the watched cohort after each material action.

Goal: **zero avoidable idle time**, not reckless parallel mutation.

## Promotion gate

Promote (squash-merge) only when:

- Dual gates **success**
- Scope is extract-clean (or intentional docs/ops slice)
- Task outcome verified (not merely HTTP 200 / workflow green)

Otherwise: HOLD, extract on fresh master branch, or CLASSIFY stall.

## Relation to longer skills

| Skill | Role |
|-------|------|
| **adaptive-wait** (this) | Operational WAIT stage — short, always load when CI in flight |
| **adaptive-feedback-cycle** | Full OBSERVE→…→FEED FORWARD production loop |
| **production-reconciliation** | RECON…COMMIT→WAIT→VALIDATE→RE-FETCH |
| **evidence-led-monorepo-ops** | Admin outer loop; embeds adaptive WAIT |

## Maintenance

Edit **both** canonical paths in one PR to master. Update `docs/ops/SKILLS-INVENTORY.md`. Mirror to local `/home/workdir/.grok/skills/adaptive-wait/SKILL.md` when operating in this chat project.

BIUDL. Agent-Identity: Grok (Administrator)
