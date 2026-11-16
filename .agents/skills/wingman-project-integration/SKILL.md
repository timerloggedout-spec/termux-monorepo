---
name: wingman-project-integration
description: Use the pinned Wingman_fork submodule as a repository-native reference, customization source, and experimental agent runtime template. Apply the repository's evidence-first WAIT loop around any Wingman-derived change.
---

# Wingman Project Integration

Treat `refTemplates/smods/Wingman_fork` as a pinned reference dependency for direct inspection, controlled customization, reusable templates, and learnings integration. It is not an implicit production runtime.

Pinned source: `timerloggedout-spec/Wingman_fork` at `a6d5cea2d48009b5555e138c8d6b8f620388fb1b`.

## Safe use

1. Read `CLAUDE.md`, relevant skills, and the context-relationship graph before adapting Wingman.
2. Inspect the pinned revision before copying code or patterns.
3. Keep adaptations outside the submodule unless the fork itself is intentionally changed.
4. Record source commit, adapted paths, reason, and validation evidence.
5. Never copy credentials, local config, session stores, or generated state.
6. Keep experimental capability separate from governance and promotion gates.

## WAIT + loop invariant

```text
RECON → PLAN / MEASURE → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT
```

WAIT is active observation, not an assertion of completion. Re-check immutable SHA/ref, runs, jobs, steps, logs, artifacts, and resulting repository state before the next action. `QUEUED` and `IN_PROGRESS` are not success.

## Wingman adaptation loop

```text
PINNED REVISION
  ↓
RECON existing capability
  ↓
SELECT one bounded adaptation
  ↓
IMPLEMENT outside submodule
  ↓
TEST / VERIFY
  ↓
WAIT → WATCH runtime evidence
  ↓
RE-FETCH pinned revision + target SHA
  ↓
COMPARE delta
  ↓
CLASSIFY adopted | rejected | needs-follow-up
  ↓
RECORD provenance + learning
  ↺
```

Terminal states: `success`, `clean no-op`, `blocked`, `approval-required`, `exhausted`, `stagnated`.

## Integration boundary

Wingman may inform agent orchestration, semantic/LSP navigation, bounded verification gates, pilot/worktree patterns, provider-neutral interfaces, and memory/learning-loop experiments.

Wingman does not replace `CLAUDE.md` governance, `adaptive-wait`, `adaptive-feedback-cycle`, `production-reconciliation`, repository dual gates, or promotion authority.

## Closeout

A Wingman-derived change is complete only when source revision, changed paths, tests/checks, runtime observations, and resulting SHA are recorded. Preserve unsuccessful experiments as evidence.
