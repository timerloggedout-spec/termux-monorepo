# RECON — Feed, Gantt, QUE, Quota and Marketing Systems Census

**Recon date:** 2026-11-10/11 UTC  
**Scope:** existing repository and published Tribute surfaces; evidence-led inventory, not a claim that every feed is fresh or every control path is healthy.  
**Purpose:** establish the actual architecture QDesk should orchestrate before adding any new scheduler, dashboard, feed, memory store or quota registry.

## Executive findings

1. Agentic dependency-phase planning predates the recent quota/mesh contract. PR #248 (2026-08-19) landed the repository-native lifecycle engine; PR #717 (2026-09-21/23) added the project-management/Gantt projection layer. PR #5147 is a later API admission / resilient-compute contract, not the origin of Gantt planning.
2. The existing canonical Gantt plan is `docs/agentic/dependency-phases.json`. Mermaid, Markdown, Project state and Gantt renderings are derived evidence views; they do not replace the plan or approval evidence.
3. The repository already has a functioning QUE producer plane for the Desk: `scripts/que/que_feed_collect.py`, `que-feed-collect.yml`, canonical `ops/que/feeds/*`, event records and byte-identical dashboard mirrors. It is distinct from the older dependency-phase lifecycle and from the Quota Dispatch Tree.
4. Quota planning is already a layered system: owner-set Pool × Focus × % allocations, a provider entitlement/readings registry, a deterministic allocation planner, quota usage packs, usage-series attribution and public dashboard projections.
5. Marketing Gantt is a real feed-backed maintenance plane, not a mock calendar. Its feed is derived from the referral registry/census and shows account maintenance cadences over a rolling 12-week horizon.
6. Tribute exposes many projections. The current `apps/tribute-dashboard/data/` directory contains 48 JSON/JSONL artifacts, but these are not 48 independent sources of truth: some are mirrors, some are derived views, some are snapshots, and some are append-only series.
7. Freshness is uneven. The QUE queue is refreshed on a 10-minute cadence and dispatch state is refreshed separately, while several quota, telemetry, challenge and opportunity surfaces were last generated between 2026-11-02 and 2026-11-04. A fresh page shell does not prove every embedded evidence block is fresh.
8. A concrete Quota Usage renderer defect was found: seven of ten quota service-state snapshots omit `states`, while the page dereferences `sn.states[svc]` unguarded. This produces a page-level `PACK ERROR`. Tracked as #5148.

## 1. Gantt and dependency-planning lineage

| Date | PR | Verified contribution | Architectural consequence |
|---|---:|---|---|
| 2026-08-19 | [#248](https://github.com/timerloggedout-spec/termux-monorepo/pull/248) | Canonical dependency-phase lifecycle, deterministic DAG validation/evaluation, idempotency, Mermaid/Markdown, GitHub Project adapter and controlled dispatch | Original repository-native dependency-phase engine |
| 2026-08-19 | [#260](https://github.com/timerloggedout-spec/termux-monorepo/pull/260) | Lifecycle/reconciliation consolidation and readable canonical issue contracts | Hardens the lifecycle around one canonical plan |
| 2026-09-21/23 | [#717](https://github.com/timerloggedout-spec/termux-monorepo/pull/717) | Project-management/Gantt adapters, stable phase IDs, dependency-derived waves, optional date anchoring/durations, advisory critical path, JSON and Mermaid | Significant Gantt projection milestone |
| 2026-09-23 | [#774](https://github.com/timerloggedout-spec/termux-monorepo/pull/774) | Post-merge report SHA and Mermaid verification correction | Demonstrates post-merge verification requirement |
| 2026-09-25 | [#828](https://github.com/timerloggedout-spec/termux-monorepo/pull/828) | RECON consolidation; live status and navigation aligned to implementation | Historical design marked implemented; live paths made explicit |
| 2026-10-21 | [#1361](https://github.com/timerloggedout-spec/termux-monorepo/pull/1361) | Rebased dependency-phase/Gantt performance improvement | Optimizes existing engine; does not replace it |
| 2026-10-21 | [#1464](https://github.com/timerloggedout-spec/termux-monorepo/pull/1464) | Disjoint DAG waves by longest prerequisite depth | Prevents duplicate nodes across concurrent waves |
| 2026-10-21 | [#1465](https://github.com/timerloggedout-spec/termux-monorepo/pull/1465) | Literal-boolean approval checks | Prevents fail-open phase approval |
| 2026-10-24/27 | [#1620](https://github.com/timerloggedout-spec/termux-monorepo/pull/1620) | Offline Delphi Oracle MVP with evidence receipts and a Gantt joining RFP, DoE/MVT/TLM, verification, MoneyBall and quota gates | Gantt already spans multiple operational domains |
| 2026-10-28 | [#1887](https://github.com/timerloggedout-spec/termux-monorepo/pull/1887) | Quota allocations: pool × focus × percentage; Gantt plan-vs-actual rows | Resource allocation is already a Gantt input |
| 2026-10-28 | [#1946](https://github.com/timerloggedout-spec/termux-monorepo/pull/1946) | Countdown Gantt and state swimlanes from recorded instants | Deadline Gantt is a separate feed projection |
| 2026-10-28 | [#1974](https://github.com/timerloggedout-spec/termux-monorepo/pull/1974) | Markov/Bayesian/Kahn/Gantt component registry; Gantt compiler delegates DAG ordering to Kahn | Gantt is an individually evaluable DoE component |
| 2026-10-28 | [#2129](https://github.com/timerloggedout-spec/termux-monorepo/pull/2129) | PT-midnight, DST-safe Gantt axis | Calendar geometry must respect America/Los_Angeles |
| 2026-10-28 | [#2134](https://github.com/timerloggedout-spec/termux-monorepo/pull/2134) | Frappe Gantt research verdict: reference-only, rejected as replacement | Keep the existing renderer's instant/milestone semantics |
| 2026-10-30 | [#2361](https://github.com/timerloggedout-spec/termux-monorepo/pull/2361) | Revision-adaptive quota planner and Termux Fleet Collector App pilot | Planning and credential buckets already have dedicated machinery |
| 2026-10-30 | [#2383](https://github.com/timerloggedout-spec/termux-monorepo/pull/2383) | Quota burn-down flow line and gearbox design concept | Replenishment pacing is modeled, with mock controls clearly marked |
| 2026-10-30 | [#2394](https://github.com/timerloggedout-spec/termux-monorepo/pull/2394) | Per-consumer STOP/PAUSE/throttle design amendment | Controls remain design-only until per-consumer metering exists |
| 2026-11-01 | [#3172](https://github.com/timerloggedout-spec/termux-monorepo/pull/3172) | Automated quota analysis workflow and regression gate | Quota changes receive GitHub-side validation |
| 2026-11-04 | [#4831](https://github.com/timerloggedout-spec/termux-monorepo/pull/4831), [#4832](https://github.com/timerloggedout-spec/termux-monorepo/pull/4832) | Referral census and `marketing-gantt/1` feed | Marketing maintenance is a feed-backed planning surface |
| 2026-11-04 | [#4890](https://github.com/timerloggedout-spec/termux-monorepo/pull/4890), [#4899](https://github.com/timerloggedout-spec/termux-monorepo/pull/4899) | Marketing Gantt page, navigation and title fix | Published dashboard projection |

**Lineage ruling:** #248 is the original dependency-phase automation foundation; #717 is the major Gantt adapter milestone. #5147 is later and additive. It must not be used as the origin story or as a reason to create a new Gantt engine.

## 2. Authority and source-of-truth map

| Domain | Canonical authority | Derived views / consumers | Rule |
|---|---|---|---|
| Dependency phases | `docs/agentic/dependency-phases.json` + `phase-approvals.json` + current PR/check evidence | `DEPENDENCY_PHASES.md`, Mermaid, GitHub Project, Gantt adapters | Every Gantt view is derived; Project status alone cannot complete a phase |
| DAG ordering | `she/orchestration/dag.py` (`kahn-reference-v2`) | Dependency engine and `scripts/temporal/gantt_compile.py` | One Kahn implementation; compiler validates filed plans, not a second scheduler |
| Challenge dates | `ops/challenge/coordinator.json`, `ops/challenge/desk-feed.json`, `docs/ops/CHALLENGE-ENTRIES-LOG.md` | `challenge-countdowns-feed/v1.2`, countdown Gantt/swimlanes | Draw only recorded instants; absent start remains a milestone, never an invented bar |
| QUE queue and governor | `ops/que/feeds/*`, `ops/que/events/*`, `ops/quota/dispatch-tiers.json`, dispatch machinery's own state feed | Desk, QUE dashboard, Quota/Cadence and DoE consumers | Queue tier, opportunity priority and quota focus are distinct dimensions |
| Dispatch claims | `ops/challenge/dispatch-state-feed.json` from dispatch watchdog | QUE queue feed fold and dashboard mirror | Claim state is not equivalent to Actions workflow queue counts |
| Quota entitlements | `ops/quota/registry.json` | Quota panel, planner, coverage | Documented limit is entitlement, not remaining balance |
| Quota allocation | `ops/quota/allocations.json` (#1884) | `allocation-plan.json`, quota allocations feed and Gantt rows | Owner-set Pool × Focus × % SSOT; generated plan never edits the allocation file |
| Quota observations | `docs/ops/generated/quota-status.json` and source-specific observations | `quota.json`, `quota-usage.json`, `usage-series.json` | Unknown/null stays unknown; do not infer consumption from entitlement |
| Referral programme terms | `config/referral_programs.json` | referral feed, referral census and marketing Gantt | Registry is SSOT; link, code, credit and commission are different resource types |
| DoE / MVT / ATES | Each experiment's own committed DESIGN/record/receipt plus family contracts | Five separate dashboard feeds | Cross-surface references are citations, not copied result payloads |
| Cross-domain project state | `ops/tracking/tracking.json` | Tracking page and generated Markdown | Joins domain records; does not overwrite their authority |
| Telemetry and provenance | `ops/lane-events`, status receipts, quota observations, source ledgers | Telemetry, nested-family, results and Delphi projections | Observability is evidence; a visualization is not a write authority |

## 3. Feed inventory — high-value planning and control surfaces

| Surface / feed | Producer and source | Cadence / observed stamp | QDesk use and caveat |
|---|---|---|---|
| Dependency-phase Gantt | `dependency_phase_engine.py` + `gantt_projection.py`; canonical dependency plan | Event/CI evaluation; canonical plan is versioned in Git | Dependency order, ready waves, critical path and phase gates |
| Temporal Gantt compiler | `scripts/temporal/gantt_compile.py` + Kahn DAG | Compile-time validation | Validates filing-format Gantt plans into DAGs; execution as a Temporal workflow remains a separate future gate |
| Challenge countdowns | `challenge-countdowns-feed/v1.2` from `CHALLENGE-ENTRIES-LOG.md` | Generated 2026-11-03T22:02:27Z; 6 entries | Deadline/timebox projection; no synthetic starts |
| QUE queue | `scripts/que/que_feed_collect.py` → `ops/que/feeds/que-queue-feed.json` + dashboard mirror | `que-feed-collect.yml`, every 10 minutes, single-flight; generated 2026-11-11T01:27:04Z | Desk producer-of-record: queued/in-progress runs by tier plus dispatch claims folded from dispatch state |
| QUE queue-by-tier | Same collector; `ops/quota/dispatch-tiers.json` | Same 10-minute cycle; 2026-11-11T01:27:04Z | First workflow-name pattern match wins; default tier 4; runs queued >7 days are excluded from counts and listed separately |
| QUE priority windows | Same collector; `dispatch-tiers.json` `priority_window` stanza | 2026-11-11T01:27:04Z | Current D1 absolute window is closed; preserve its explicit end condition and custody |
| QUE governor | Same collector folds admission stamps and Cadence's `que-governor-event/v1` batches | Envelope 2026-11-11T01:27:04Z; latest governor event 2026-11-04T01:09:15Z | Admission thresholds and flow-governor state; envelope freshness must not mask stale event evidence |
| Dispatch state | `scripts/dispatch/dispatch_watchdog.py` → `dispatch-state-feed/v1` | Watchdog every 15 minutes; feed 2026-11-11T02:15:21Z | Claimed/escalated/queued issue state; not the Actions run queue |
| Quota readings | `quota_poll.py` → generated quota status and `quota.json` | Snapshot generated 2026-11-04T01:59:43Z | 171 registry rows; public projection deliberately carries null used/reset values where not observable |
| Quota allocation plan | `quota_allocation_planner.py` → `ops/quota/allocation-plan.json` | Weekly Wed 08:47Z + dispatch/push; current file 2026-11-03T19:31:27Z | 59 plan pools in this snapshot; deterministic revision proposal, not allocation SSOT |
| Quota allocations feed | `quota_allocations.py` joins allocations + registry + readings + countdowns | Feed 2026-11-04T01:10:32Z | Pool/focus/reserve Gantt; observed actual per focus stays null until a focus-attributed reading exists |
| Quota Usage pack | `scripts/quota_usage_pack.py` → `quota-usage/v1` | 2026-11-04T02:00:11Z | 171/171 readings-row coverage; consumption coverage explicitly not published; series1 PAT observations, series2 status snapshots, series3 reconstructed Actions corpus |
| Quota usage series | `scripts/quota_usage_series.py` → `quota.usage-series/v1` | 2026-11-04T10:29:37Z | 97 provider axes: 1 measured axis (GitHub, 12 points, last 2026-11-02), 2 activity-proxy axes (Jules), 94 gap axes; activity proxy is not consumption |
| Quota dispatch tree | `dispatch_tree_feed.py` reads workflow rules/matrix + stamped Actions observation | 2026-11-02T11:07:27Z | 32-lane admission/cadence projection; snapshot, not live-at-view-time |
| Referral feed | `referral-feed/1` from `config/referral_programs.json` | 2026-11-09T17:12:30Z | Programme status, access/reward semantics and code pools; no public programme or unknown reward remains explicit |
| Marketing Gantt | `marketing-gantt/1` from referral feed + referral census; registry is SSOT | 2026-11-09T17:12:30Z | 15 accounts on a rolling 12-week maintenance horizon; live 7, pending 6 in raw census, not-established 1, no-public-programme 1; display mapping documents its 3-bucket fold |
| Dashboard surface feeds | `scripts/dashboards/surface_feeds.py` | Weekly Wed 06:41 UTC + dispatch + source-path push | Separate 3L0, MoneyBall, MVT, DoE and ATES feeds; collector reads repository records only and does not call the network |
| Telemetry | `telemetry-viz-feed/v1` | 2026-11-02T14:23:13Z | Golden signals, workflow outcomes and quota; sources include older snapshots and named gaps |
| Nested family | `nested-family/v1` from routed-dispatch records, experiment records, stamps and desk usage | 2026-11-03T09:33:50Z | 16 providers, 20 models, 4 roles, 43 tasks, 31 dispatches; exact-join gaps are recorded |
| Backup state | `backup-state/v1` from backup relays + snapshot | 2026-11-03T09:33:50Z | 58 exports, 1 drill, last drill verdict `fail`; snapshot fetch was HTTP 404, so state may be stale |
| Proposals | `proposals-feed/v2` from `docs/proposals/registry.yaml` | 2026-11-03T15:11:21Z | 60 registered proposal packs; one pass record unreadable and named as a gap |
| Oracle panel | `oracle-panel-feed/v1` from proposal registry + ledger snapshot | 2026-10-27T16:01:12Z | Older snapshot; refresh/evidence age must be visible |
| Free-tier value | `free-tier-value.json` | 2026-10-23T00:00:00Z | Explicitly stale; estimates are not cash savings or entitlement proof |
| Results index | `results-index-feed/v1` from `ops/telemetry/results-index.json` | 2026-11-02T13:26:57Z | Derived presentation of results evidence |

The published Tribute navigation includes Quota, Quota Usage, Quota Graphs, Swarm Quota, Admin, Admin Graph, Oracle, 3L0, MoneyBall, Wagering Book, Pools, MVT, DoE, ATES, Results Index, Free-Tier Value, Dispatch Tree, Countdowns, D2 Proposals, Linguist, Delphi RFP, Delphi Ledger, Classifiers, PR Lanes, Proposals, Referrals, Marketing Gantt, Telemetry, Desk, Tracking, Family and Version Comparison, plus the surfaces map. Not every page is an independent feed or a canonical authority.

## 4. Live-state observations and operational gaps

### QUE / Desk

The retrieved QUE queue snapshot (2026-11-11T01:27:04Z) reports:
- 3 queued and 16 in progress;
- 1 in-progress tier-2 workflow and 15 in-progress tier-4 workflows;
- 3 queued tier-4 workflows;
- 4 ancient queued runs listed separately and excluded from queue counts.

The dispatch-state snapshot (2026-11-11T02:15:21Z) reports 16 claimed, 7 escalated and 0 queued issue dispatches. These are different units from the Actions workflow queue above; do not add them together.

The governor reports tier-4 deferral at 400 queued, tier-3 at 800 queued, tiers 1–2 never deferred; 3 deferred-by-tier issues stamped in the last 24 hours and 12 open. Its envelope is current, but its flow-governor batch is from 2026-11-04 (4 events total). QDesk must track freshness per sub-block, not only per JSON file.

The queue feed records the 2026-11-07 Swarm App suspension incident: the QUE collector's token-mint step failed repeatedly for approximately 2.5 days and no page was raised; the watchdog dependency was also called out. See task #5132 and migration issue #5113. The workflow source has a separate failure-diagnostic step using the repository token; verify that this path can actually page when the App mint itself fails. Do not treat a configured fallback as a proven liveness drill.

### Quota Usage renderer defect

Issue [#5148](https://github.com/timerloggedout-spec/termux-monorepo/issues/5148) tracks a reproducible render failure:
- 10 quota service-state snapshots exist.
- The first 3 have a `states` object; the latest 7 do not.
- `apps/tribute-dashboard/quota-usage.html` dereferences `sn.states[svc]` without guarding the missing map.
- The page catches the resulting TypeError and renders `PACK ERROR`.

Correct behavior is to render explicit absence/no-reading for missing state maps. It must not synthesize zero or infer a provider state.

### Other freshness / integrity cautions

- The quota usage pack says consumption coverage is not yet published. 171/171 rows means readings-row coverage, not complete consumption metering.
- The 97-axis usage-series has only one measured provider axis, two activity proxies and 94 explicit gaps. Never route work based on the number of listed providers as if it were observed free capacity.
- The allocation plan (59 pools) and quota allocations feed were generated on different stamps; their pool census and source hashes should be reconciled before treating the rendered Gantt as current.
- Dispatch-tree feed is a snapshot and has three named gaps; it is not live-at-view-time.
- The surfaces map page remains explicitly DRAFT; PR #4888 landed the draft, while the serve-step PR #4898 remains open in the inspected snapshot.
- Backup state has one failed drill and a snapshot HTTP 404. Redundancy is not proven by the existence of a backup feed.
- Quota Gearbox STOP/PAUSE/throttle controls are design-only until consumer-tagged metering exists. Configured allocation share is not observed per-consumer RPM.

## 5. QDesk integration contract — compose, do not duplicate

QDesk should be the cross-domain decision and coordination layer over these existing records. It should not create a second Gantt scheduler, quota registry, challenge ledger, referral registry, DoE store or telemetry database.

For each candidate task, construct a compact context packet with references (not copied authority) to:
1. objective and owner focus;
2. canonical task/issue and its current dispatch claim;
3. dependency-phase IDs, predecessor graph and current approval evidence;
4. relevant challenge/marketing/resource timeboxes and their source timestamps;
5. quota pool, focus share, entitlement class, current observation and reset/refill semantics;
6. provider/worker eligibility and execution permissions;
7. relevant memory nodes, prior outcomes, negative results and procedure versions;
8. acceptance criteria, expected evidence receipt and independent verifier.

Keep these priority dimensions separate:
- **QUE tier:** workflow/run-queue admission class.
- **Opportunity priority/timebox:** task or challenge urgency and escalation ladder.
- **Quota focus allocation:** owner-set Pool × Focus × % budget distribution.
- **Dependency Gantt:** prerequisite ordering and parallel waves.
- **Marketing maintenance cadence:** programme verification, gate-watch and account maintenance.
- **Provider admission:** fresh capacity, reserve, reset and credential bucket.

A high score in one dimension must not silently override another dimension's hard gate. In particular, memory relevance cannot authorize spend, a Gantt milestone cannot imply a start time, a referral click cannot imply a reward, and a queue claim cannot imply task completion.

### Memory and attention integration

Memory should index each feed record by stable identity, source path, source SHA/content hash, schema version, generated/observed timestamps, authority class, owning lane, freshness state and related issue/PR/task IDs. Retrieve the minimum context needed for the active task. Keep provenance pointers and negative outcomes queryable.

The attention governor should:
- bind every task to an objective or explicitly permitted exploration lane;
- use source freshness and evidence quality as first-class retrieval features;
- detect duplicate/in-flight claims before dispatch;
- identify deadline, expiry and refill windows without inventing missing times;
- reserve resource capacity before work starts;
- defer provider work on stale/unknown quota while allowing deterministic offline work;
- explain every escalation and re-plan with the source event and policy version;
- learn from outcomes only after receipts and independent checks exist.

## 6. Recommended implementation sequence

1. **Feed catalog (derived inventory only):** generate a machine-readable catalog from page fetch references, feed schemas, producer scripts, workflow schedules and canonical-source docs. It is a navigation/metadata index, not a second SSOT.
2. **Freshness and integrity layer:** per-feed and per-sub-block timestamps, canonical/mirror parity, schema checks, missing-field handling, and named gaps.
3. **QDesk context assembler:** join task → issue/claim → dependency phase → opportunity timebox → quota focus → provider/worker → memory evidence.
4. **Attention and admission governor:** combine QUE tiers, deadline urgency, quota reservations and objective value without collapsing their semantics.
5. **Cross-feed Gantt projection:** derive a multi-lane view from canonical dependency plans, challenge countdowns, quota allocation rows, QUE windows and marketing maintenance. Render only explicit starts/ends and preserve null/unknown.
6. **Execution and feedback:** dispatch through existing approved workflows/Termux workers; persist idempotent receipts; evaluate memory utility and policy candidates under DoE; independent Delphi/verification gates remain separate.

## 7. Acceptance gates

- [ ] Gantt outputs are reproducible from the canonical plan and source feed hashes.
- [ ] Dependency, QUE tier, opportunity priority, quota focus and marketing cadence remain distinct fields.
- [ ] Missing or stale feed blocks render STALE / UNKNOWN / NOT_ESTABLISHED, never zero or success.
- [ ] Canonical/mirror pairs are byte-equal where their contracts require it.
- [ ] A missing `states` object in a quota snapshot cannot crash the Quota Usage page (#5148).
- [ ] A stale governor event batch is visible even when the enclosing QUE feed has a recent generated_at.
- [ ] Queue counts exclude wedged ancient runs only with a separate explicit list.
- [ ] Worker failover and dispatch recovery have a forced drill with receipts; a configured backup is not proof.
- [ ] No feed consumer writes to the source-of-truth record it merely projects.
- [ ] Every consequential dispatch has objective, authorization, quota reservation, idempotency and evidence references.
- [ ] Memory retrieval quality is measured against outcome receipts; no unvalidated self-promotion.
- [ ] Paid spend, credential provisioning, merge, deployment and production promotion remain separately authorized.

## 8. Key references

- [Dependency-phase automation README](../../agentic/README.md)
- [Dependency-phase canonical plan](../../agentic/dependency-phases.json)
- [DoE component registry](../../ops/DOE-COMPONENT-REGISTRY.md)
- [Dashboard surface feed contract](../../ops/DASHBOARD-SURFACE-FEEDS.md)
- [Quota allocation planning](../../ops/QUOTA-ALLOCATION-PLANNING.md)
- [Quota Gearbox concept](../../ops/QUOTA-GEARBOX-CONCEPT.md)
- [QUE producer README](../../../ops/que/README.md)
- [Adaptive dispatch](../../ops/ADAPTIVE-DISPATCH.md)
- [Dispatch Tree feed contract](../../ops/DISPATCH-TREE-FEED.md)
- [Marketing Gantt](https://timerloggedout-spec.github.io/tribute/marketing-gantt.html)
- [Quota Usage](https://timerloggedout-spec.github.io/tribute/quota-usage.html)
- [Quota Graphs](https://timerloggedout-spec.github.io/tribute/quota-graphs.html)
- [Tribute surface map](https://timerloggedout-spec.github.io/tribute/surfaces-map.html)

