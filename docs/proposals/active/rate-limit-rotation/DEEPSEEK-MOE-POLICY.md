# RL-18 — DeepSeek priority routing & roundtable MoE (policy definition)

Status: **todo — unaccepted**. This document defines the item; it does not
authorize implementation. Any code change implementing "highest priority"
DeepSeek routing or a roundtable MoE method requires Tier 3 quorum (driver +
distinct second mind, or Operator) per `docs/CONSENSUS.md`, logged in this
proposal's MANIFEST Review log, before it lands on `master-staging`.

## Scope boundary

Public benchmark leaderboard results collected under
`docs/proposals/active/leaderboard-protocol/` **must never** be used as
routing labels or routing authority for this item. Only the internal success
matrix / ELO (3L0) in `docs/schemas/model-success-matrix.yaml` and the checks
below may drive routing decisions.

## 1. Exact DeepSeek provider and model IDs

- OpenRouter: `deepseek/deepseek-r1:free` — already registered in
  `docs/schemas/model-rotation.yaml` (`roles: [review]`, `soft_rpd: 20`,
  `priority: 22`, `status: preferred_fallback`) and
  `docs/schemas/routing-priority.yaml` (`soft_rpd_per_model`).
- Any additional DeepSeek id (e.g. a hypothetical `deepseek/deepseek-v3:free`)
  must be added explicitly to `model-rotation.yaml` and
  `routing-priority.yaml` with its own soft-budget row before this item can
  reference it. No inferred or undocumented DeepSeek ids.

## 2. Eligibility & availability checks

- Must pass the existing OpenRouter free-model availability poll
  (`fetch_openrouter_free_models_cached()` in `scripts/model_router.py`)
  before selection; a failed/empty poll falls back to the stale cache or the
  `LEGACY_MODELS` set exactly as RL-17 already implements — this item adds no
  new fail-open path.
- Must remain suffixed `:free`. Paid DeepSeek tiers are out of scope and
  forbidden by the existing free-tier-only guard.
- "Highest priority" means first in `role_peers` ranking order for the roles
  where DeepSeek is eligible (currently `review`); it must not bypass the
  soft-budget check or the `has_openrouter` gate.

## 3. Roundtable MoE: advisory or route-selecting?

- Initial mode: **advisory only**. A roundtable-MoE step may annotate or
  re-rank candidate peers, but must not itself pick the final provider/model
  without a separate, explicitly accepted follow-up item that upgrades it to
  route-selecting.
- Any upgrade to "can select a route" requires its own Tier 3 quorum entry
  logged in this proposal's Review log, distinct from this definition item.

## 4. Budget, latency, concurrency, failure limits

- **Budget**: reuse the existing soft-budget counters in
  `scripts/model_router.py` (`get_usage`/`increment_usage`); no new unmetered
  request path.
- **Latency**: bounded by the same network timeout already used for catalog
  polling (5s); a roundtable step must not add unbounded per-call latency and
  must not multiply the number of model calls per routed decision.
- **Concurrency**: a roundtable/MoE step must not issue more model calls per
  routing decision than the current single-call selection logic.
- **Failure limits**: any roundtable/MoE failure must fail open to the
  existing deterministic ELO + soft-budget selection — never to a hard
  failure of the calling GitHub Actions job.

## 5. Prompt-data handling & secret boundaries

- No API keys, tokens, or other secrets may appear in routing/roundtable
  diagnostics, logs, or `GITHUB_OUTPUT`.
- Prompt/diff content routed to DeepSeek remains subject to the same
  `max_prompt_chars` caps as other roles (`docs/schemas/model-rotation.yaml`).

## 6. Evaluation data & success criteria

- Success criteria are defined against the internal success matrix
  (`docs/schemas/model-success-matrix.yaml`), not public benchmark scores.
- Per the scope boundary above, no leaderboard-protocol observation may be
  used as a training/eval label for this item.

## 7. Rollback behavior

- Any change implementing DeepSeek "highest priority" or roundtable MoE must
  be revertible by reverting `role_peers` ordering in
  `scripts/model_router.py` alone — no coupled schema migration that blocks a
  straight revert.

## 8. Unit and workflow test requirements

- Unit tests in `tests/test_model_router.py` covering: DeepSeek priority
  ordering, roundtable advisory-mode fail-open behavior on error, and
  no-regression on existing `role_peers` scoring for other models.
- Workflow-level dry-run evidence attached to the implementing PR before
  merge, per `AGENTS.md` gate requirements (`repo_gate.py`, `termux_smoke.py`).

## Acceptance

Unaccepted. Requires Tier 3 quorum before any implementing PR opens. The
implementing PR must cite `Implements: RL-18`.