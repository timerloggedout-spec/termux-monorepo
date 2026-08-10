# Agent evaluation matrix — programmatic base layer

**Status:** base layer for GHA scoring · advanced review-NLP layer later  
**Roster/Delphi:** [`ROLES-ROSTER.md`](ROLES-ROSTER.md) · [`DELPHI-WEIGHTING.md`](DELPHI-WEIGHTING.md)  
**Impact tools:** `oracle` → `workspace/llm_map/impact_oracle.py` · `archaeo` → `archaeologist.py` (aliases in shell / ArchWiz)

## Intent

Score **roles × sessions** from observable GitHub events — no human scoring loop. Empty commits, accepted/rejected review fixes, and Oracle impact signals feed adaptive points (Human Reinforcement Adaptivity Learning analogue for agents).

## Metrics (v0 — GHA-computable)

| Metric id | Event | Requester (author role) | Reviewer role |
|-----------|-------|-------------------------|---------------|
| `empty_commit` | Head commit `files:[]` or stats zero after claimed fix | **−P_empty** (default 3) | — |
| `review_fix_accepted` | Reviewer-requested change applied in non-empty commit; thread resolved | **−P_fix_credit** (default 1) *shared* | **+P_fix_credit** (default 2) |
| `review_fix_rejected` | Disposition rejects fix as wrong/unsafe; thread stays open or reopened | **+P_defend** (default 1) if evidence | **−P_bad_review** (default 2) |
| `security_bypass_caught` | Security/Sentinel finding accepted | — | **+P_sec** weighted by severity (M=3, H=5, C=8) |
| `security_bypass_missed` | Security issue merged without address | **−P_sec** severity | **−P_sec/2** if reviewer approved |
| `pr_landed` | PR merged | **+P_merge** scaled by complexity | soft prior only |
| `issue_accepted` | Issue closed as completed with acceptance | **+P_issue** | — |
| `issue_rejected` | Issue closed as not-planned / invalid after debate | **−P_issue/2** if author bot | — |

### Complexity scale for `pr_landed` (v0)

```text
complexity = log2(1 + files_changed) + log2(1 + additions + deletions)/2
P_merge = clamp(1, 10, round(complexity * band_mult))
band_mult: P0=1.5, High=1.2, Medium=1.0, Backlog=0.7
```

Optional Oracle hook (when `impact_oracle.py` runnable in CI on changed paths):

```text
impact_boost = mean(shockwave, nexus) / 100   # 0–1
P_merge *= (0.75 + 0.5 * impact_boost)
```

Archaeo lifecycle signals (churn / co-evolution) reserved for v1 — do not block v0.

## Empty commit as primary session quality signal

- Count per `context_key` / `session_id`.
- Threshold: `empty_commit_count >= 2` within 24h → soft-quarantine role session (no new task create; continue only with explicit non-empty requirement).
- Feeds MoneyBall / 3L0 priors (#131) as negative performance.

## Adaptive points store

```text
.path: docs/ops/eval/points.jsonl   # append-only audit (public demo OK)
or Actions cache key agent-eval-<role>-<day>
```

Each line:

```json
{"ts":"ISO","role":"jules|coderabbit|devin|...","context_key":"pr-N-ref","metric":"empty_commit","delta":-3,"pr":126,"sha":"...","note":""}
```

Delphi weight applies when rolling into matrix votes:

```text
effective = role_delphi_weight * sum(deltas)
```

## Workflows (base)

| Workflow | Job |
|----------|-----|
| `agent-eval-score.yml` | on `pull_request` synchronize + closed; score empty commits, merge complexity |
| `agent-review-auto-jules.yml` | on empty head after Jules push → metric + API continue |
| `agent-continuous-ops.yml` | YOLO approvePlan + FAILED sendMessage + eval deltas |

Script: `scripts/ci/agent_eval_score.py`

## Non-goals (v0)

- NLP quality of review prose (later layer).
- Silent DECISION-MATRIX rewrite from scores alone.
- Class 3/4 in eval store.

## Related

#145 · #148 · #129 · #131 · #120 · Oracle/Archaeo aliases · [`JULES-API-AUTOMATION.md`](JULES-API-AUTOMATION.md)

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-eval-matrix
