# Workflow Orchestration Skill

## Purpose
Coordinate modular GitHub Actions without duplicating state machines or hiding failures.

## Architecture
Supervisor discovers attention-worthy work. Observers collect immutable evidence. Planners classify and propose. Mutators are isolated behind explicit review. MVT executes controlled comparisons.

## Rules
- Prefer reusable workflows/actions and stable contracts over monolithic workflows.
- Keep permissions least-privilege.
- Pin third-party actions where policy requires it.
- Retry only transient failures; surface permanent failures immediately.
- Use SHA-aware concurrency and stale-event rejection.
- Wait for terminal workflow/check state before classification.
- Re-fetch reviews, threads, commits, and checks after every material commit.
- Stop rather than auto-resolve conflicts.

## Canonical loop
RECON -> PLAN -> IMPLEMENT -> COMMIT -> WAIT -> VALIDATE -> RE-FETCH -> CLASSIFY -> REPEAT.
