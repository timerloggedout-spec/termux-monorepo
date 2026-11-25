# Master-staging reconciliation ledger — 2026-11-24

## Canonical refs

| Ref | SHA | Observed |
|---|---|---|
| `master` | `63a59d105b3584e6fbd1b2bc9e659e22fdaf10de` | 2026-11-24 |
| `master-staging` | `23026f13d7ad08ac7703cef0639fd76efa874fe1` | 2026-11-23 |
| Merge base | `c3ea1e1c24a03b1b199e6c36521f4be9b367c733` | shared ancestor |
| `termux-smoke` | `521fa1a026ea60f92f35c7831816b407352a5018` | 2026-09-07 |

## Branch comparison

| Measure | master-staging against master |
|---|---:|
| Staging-only commits | 56 |
| Master-only commits | 31,715 |
| Status | diverged |
| Changed files surfaced by compare API | 300 |
| Added / modified / removed in surfaced set | 280 / 19 / 1 |

The GitHub compare response is capped at 300 changed-file records. The branch endpoint independently confirms the staging tip SHA. Treat the 56 staging-only commits as source material for extraction; the ancestry difference makes a wholesale branch merge unsuitable.

## Open PRs targeting master-staging

| PR | Workstream | Commits | Files | Current GitHub merge state | Disposition |
|---|---|---:|---:|---|---|
| [#5806](https://github.com/timerloggedout-spec/termux-monorepo/pull/5806) | DO-first communication law / repo-gate lint | 35 | 14 | mergeable / unstable | Extract enforcement and tests after current-master overlap review |
| [#5683](https://github.com/timerloggedout-spec/termux-monorepo/pull/5683) | Accessibility agents integration | 3 | 20 | mergeable / unstable | Review pinned dependency, Jules workflow retirement, and current adapter overlap |
| [#1569](https://github.com/timerloggedout-spec/termux-monorepo/pull/1569) | MVT / DoE validation protocol | 11 | 5 | mergeable / unstable | Extract the protocol as a focused documentation workstream |
| [#1514](https://github.com/timerloggedout-spec/termux-monorepo/pull/1514) | Antigravity operational pilot | 12 | 45 | mergeable / unstable | Keep isolated; review provisioning, permissions, and operational boundaries |
| [#1498](https://github.com/timerloggedout-spec/termux-monorepo/pull/1498) | Antigravity provisioning proposal | 4 | 14 | mergeable / unstable | Review with #1514; retain separate acceptance and scope |
| [#286](https://github.com/timerloggedout-spec/termux-monorepo/pull/286) | Autonomous staging progression | 1 | 8 | dirty | Extract only after conflict and current automation review |
| [#48](https://github.com/timerloggedout-spec/termux-monorepo/pull/48) | LLM API hub / ADE split | 19 | 73 | dirty | Split by component and revalidate on current master |

All seven PRs target staging commits older than the current staging tip. Their head branches remain independently addressable.

## Separate Termux lane

The `termux-smoke` branch is itself diverged from master: 6 commits ahead and 32,084 behind at the observed comparison. Its surfaced changes include Termux smoke behavior, Android/Termux environment documentation, Skyhook device profiles, and Termux bridge components.

Keep this lane separate from general staging reconciliation. Extract its Termux-specific changes only through the Termux workstream and its own tests.

## Scope defect found

The current master `.github/workflows/termux-smoke.yml` runs bucket-headroom tests and installs PyYAML/pytest. The staging copy runs the core smoke and optional agent-surface probes only. Bucket-headroom contracts belong to a dedicated workflow; Termux smoke owns Termux runtime validation.

## Reconciliation policy

1. Keep `master` canonical.
2. Preserve `master-staging`, `termux-smoke`, and all PR head refs.
3. Extract coherent, validated changes onto fresh `master`-based branches.
4. Record overlap, conflicts, source SHA, destination SHA, and validation evidence.
5. Apply `termux-smoke` only to Termux-related operations.
6. Keep quota, provider, repository-wide, and other domain checks in their owning workflows.

## Current state

- Inventory: COMPLETE
- Staging extraction: IN PROGRESS
- Termux gate scope correction: IN PROGRESS
- Bucket-headroom workflow separation: IN PROGRESS
- Staging branch promotion: PENDING per-workstream validation
