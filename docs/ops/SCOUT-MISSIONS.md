# Scout Missions

Scout is a **population of scouts**, not a single provider roster script. Each scout produces evidence-backed proposals for a manager/control-plane policy. Scouts do not independently grant routing authority, merge authority, promotion, culling, or rewards.

## Parallel scout population

| Scout | Mission | Manager input |
|---|---|---|
| Provider Research | Discover providers/models, free/trial access, quota, capability and expiry | candidate roster |
| Code Recon | Mine commits, PRs, issues, reviews, templates, skills and history | reusable implementation evidence |
| Performance | Request reproducible correctness/performance experiments | MVT proposals/results |
| Oversight | Find Bug Bounty, Help Wanted, CTF, developer/security skills and performance-test targets | evaluation opportunities |
| Regression | Compare current state with known-good evidence and detect rollback/evidence loss | regression signal |

The implementation is `scripts/scout_missions.py`; it consumes the dynamic Scout roster and emits proposal-only mission records.

## Oversight is a performance laboratory

Issue #342 establishes the intended evaluation population: GitHub Help Wanted, bug bounties, CTF/OverTheWire-style challenges, curated challenge lists, developer interview skills, FreeCodeCamp certificates and additional evaluations. These should become **task families/cohorts**, not arbitrary labels attached to agents.

An oversight scout may propose a task. A manager selects the experiment. The result enters the same evidence pipeline as repository work:

`task → provider/model/manager → request/run → result → correctness → review → score → feed-forward`.

## Researching new free resources

Provider discovery and free-resource discovery are team research. A source must carry provenance and observation time. `free`, `trial`, `zero-price`, quota, and promotional availability are resource/capacity classifications—not quality scores and not permanent routing winners.

A discovered model follows the normal admission progression:

`DISCOVERED → CATALOG_VERIFIED → CREDENTIAL_AVAILABLE → REQUEST_PROBE → TASK_PROBE → REPEATED_SUCCESS → TEAM_ELIGIBLE → MONEYBALL_SCORED → ACTIVE`.

## Manager boundary

Scouts **propose**; managers **decide**. This preserves multiple competing scouting perspectives while preventing a scout from silently changing routing policy. Bilateral/adversarial critique can create another proposal or experiment; it does not replace measured evidence.

## Culling and agent-wallet future path

Culling must preserve the historical agent identity, evidence, and contribution lineage. The repository may later introduce agent wallets, community pots, continuing-agent bonuses, and contribution-weighted distributions. Those are accounting/governance mechanisms and must remain separate from performance scoring and admission authority until their accounting rules are explicitly specified and tested.

A culled agent therefore becomes a historical/learning entity, not a deleted record. Any future reward mechanism must operate from immutable contribution receipts rather than inferred ownership of a PAT-authored GitHub action.

## BIUDL

Broad team → focused scout/experiment lane → thin validated result → feed-forward synthesis → broaden. Every successful scout mission should improve the next population or evaluation cycle.

## Related SSOTs

- `docs/ops/SCOUT-ROSTER.md`
- `docs/ops/AGENT-TEAM-DEVELOPMENT-LANES.md`
- `docs/ops/AGENT-TEAM-ORCHESTRATION.md`
- `docs/ops/ACTIONS-METRICS-INTEGRATION.md`
- `docs/architecture/AGENT-TEAM-CONTROL-PLANE.mmd`
- `docs/ops/AGENT-EXPERIMENT-LINEAGE.md`
- `.agents/skills/evidence-led-monorepo-ops/SKILL.md`
- `.agents/skills/review-loop/SKILL.md`
- Issue #129 — Development Teams
- Issue #337 — Continuous Evaluation
- Issue #342 — Evaluations / LeaderBoards / 3L0
- Issue #357 — Agent attribution/provenance
