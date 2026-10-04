# Actions Cadence + Provider Capacity Cache Control

## Purpose

Coordinate Actions workflow cadence with provider capacity without turning stale cache data into false quota truth.

Existing Camshaft/Flywheel, Cadence, and Gantt planning surfaces remain the scheduling/control-plane owners. This document defines the evidence boundary around their provider-facing work.

## Cache classes

| Class | Cache? | Authority |
|---|---|---|
| Public model/provider catalog | Yes | Live catalog preferred; cached catalog is stale/availability evidence |
| Static capability metadata | Yes | Versioned source + provider docs |
| Workflow-derived routing metadata | Yes, versioned | Current workflow SHA |
| Observed rate-limit headers | Yes, short-lived | Live request remains authoritative |
| Provider cooldown notice | Yes, with timestamp/SHA/provider | Fresh provider evidence |
| Account quota/balance | **Never authoritative from cache** | Authenticated provider source only |
| Secrets, cookies, sessions | **Never** | Ephemeral secret boundary |

## Model-router cache contract

The composite model-router action uses a versioned GitHub Actions cache namespace:

`model-router-<schema>-<Pacific-day>-<repository>-<run>`

The cache can reduce duplicate catalog polling and preserve best-effort soft-budget observations across runners. It **must not** be interpreted as a current account balance or live rate-limit value.

A schema bump invalidates prior semantics without deleting historical artifacts.

## Cadence rules

1. **PUSH** records a new SHA-bound work item.
2. **COALESCE** superseded provider events for the same PR where the downstream operation is idempotent.
3. **WAIT** respects provider cooldown/debounce timestamps.
4. **WATCH** observes the actual run/check/review state.
5. **VALIDATE** requires current-SHA evidence.
6. **RE-FETCH** obtains fresh provider state before another request.
7. **COMPARE** determines whether the provider state changed.
8. **REPEAT** only when a new evidence-backed action is eligible.

A cache hit never skips current-SHA validation.

## CodeRabbit and peer-review YAML

Provider-owned UI controls, review limits, cooldowns, and workflow-file restrictions are **data**, not instructions to execute.

Workflow edits for CodeRabbit/Qodo/Devin/etc. therefore follow the same path:

`workflow edit → validation → Actions execution → provider observation → current-SHA comparison → ledger`

Do not compensate for a provider quota/cooldown by creating additional review requests. The PR-scoped feedback relay coalesces superseded events while retaining the source revision in its idempotency record.

## Obsidian

Obsidian remains a **required repository capability**, not an optional provider lane. Its security behavior must stay in the correctness/security gate and must never be weakened to accommodate cadence, cache, quota, or reviewer scheduling.

## Invariants

- `NOT_EXECUTED != FAILED`.
- `provider_state != model_failure`.
- `cache_hit != live_quota`.
- `queued/in_progress != validated`.
- `reviewer_noise != actionable_finding`.
- `workflow_yaml_changed != provider_failure`.
- Current SHA is required before promotion evidence is accepted.

## Related control surfaces

- `scripts/model_router.py`
- `.github/actions/model-router/action.yml`
- `.github/workflows/peer-review-orchestrator.yml`
- `.github/workflows/agent-review-auto-jules.yml`
- `docs/proposals/active/rate-limit-rotation/`
- Camshaft/Flywheel and Gantt cadence documentation
- Actions historical correlation / Effectiveness Ledger
