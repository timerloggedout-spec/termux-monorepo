# Lag index disposition upgrade (cherry-pick for #178)

## Source of truth pair (PR #174)
- ACK (wait): https://github.com/timerloggedout-spec/termux-monorepo/pull/174#issuecomment-5260135328
- Premature Jules: https://github.com/timerloggedout-spec/termux-monorepo/pull/174#issuecomment-5260137282

## Disposition model
| Disposition | Meaning | Jules / continuous-ops |
|---|---|---|
| `summon` | opsSweep / auto-jules / @coderabbitai full review | Start wait clock |
| `ack_pending` | Bot promised work ("I will re-review") | **WAIT** — not actionable |
| `quota_cooldown` | Rate/review limit | **WAIT** until wait_sec |
| `real_review` | Findings / approve / changes | Address threads |
| `programmatic` | Commit after summon | Clear stale |

## Implement in `scripts/ci/calculate_lag_index.py`
Classify comments; emit per-PR: `open_disposition`, `jules_actionable`, `wait_sec`.
Schema v2 already on `docs/ops/response_time_lag_index.json`.

## Implement in `agent-review-auto-jules.yml` detect-bot-feedback
Before posting `@jules` Auto-resolve:
- if latest bot comment is ACK-only or quota/limit → **skip**
- if lag index `by_pr[N].jules_actionable === false` → **skip**

## Implement in continuous-ops
When loading lag index, if `open_disposition` in (`ack_pending`, `quota_cooldown`, `summon`):
`debounceMs = max(debounceMs, wait_sec * 1000)`

Quota/CoolDown/Limits comments (CodeRabbit limit, OpenRouter free-models-per-day, Codex usage) map to `quota_cooldown`.
