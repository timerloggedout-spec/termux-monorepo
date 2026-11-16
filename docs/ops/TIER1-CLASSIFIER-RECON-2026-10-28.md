# Tier 1 classifier recon — full sweep (2026-10-28)

Firsthand from live sources only: GitHub API pulls 2026-10-28 ~13:23–13:40
PDT (workflows, runs, labels, secrets names, full git tree). Repo totals at
pull time: **246 workflows, 103 labels, 53 Actions secrets, 10,663 tree
files.** 76 workflows matched the classifier pattern; every unit below was
verified present in the tree or in the runs API. State vocabulary:
**LIVE** (fired ≤7d with effect) · **SKIP-GATED** (event-triggered, idle
between matching events — normal) · **DORMANT** (trigger exists, no fire
>7d) · **NEVER-RUN** (0 runs ever) · **CODE-ONLY** (no workflow trigger) ·
**FAIL-LAST** (most recent run failed) · **EXTERNAL** (not repo-run).

## A. deepcli observatory (LLM response classification)

| Unit | Defined | Classifies | Trigger | State |
|---|---|---|---|---|
| Mev/Jev/Kev/Laya + trial.py | deepcli/deepcli/observatory/ (1.3–5.5 KB ea) | LLM responses: produce → judge (rubric) → verify (token-F1) → rank | dispatch only | LIVE via dispatch |
| dispatch.py + adapters (gemini/openrouter/systemone) | deepcli/deepcli/observatory/dispatch.py, llm/adapters/ | free-only route enforcement + SystemOne decide | classifier-trial-dispatch.yml | LIVE — runs 2026-10-27: success 40509162104, fail 40517046438 (demo 403 + producer 429) |
| System One catalog | config/system_one_catalog.json (88 entries) | external decision models by layer/state | none (data) | current 2026-10-27 (PR #1842) |

Coverage: only what a human dispatches. No standing trigger classifies the
repo's LLM traffic; the quartet fires per-dispatch only.

## B. ml/pipelines (PR/lane classification stack)

| Unit | Defined | Classifies | Trigger | State |
|---|---|---|---|---|
| classify_pr (vocab v2: EXTRACT/SUPERSEDE/NEED_EVIDENCE/CANDIDATE) | ml/pipelines/lanes/classify.py + minesweeper/supersede rules | PRs into disposition vocab | keepalive only | **DORMANT** — ml-pipelines-keepalive.yml last ran 2026-10-21 (push) despite daily pushes since |
| stages pipeline (features/evaluate/bind/ingest/recon/train/monitor/export) | ml/pipelines/stages/ | lane lifecycle | keepalive_dag | DORMANT with keepalive |
| moneyball scorer | ml/pipelines/moneyball/{scorer,weights,explain}.py | PR priority scores | code-only + hex evidence wf | CODE-ONLY (see overlap O3) |
| peers (registry/collision/overlap/grok/jules) | ml/pipelines/peers/ | collaborator collision/overlap | code-only | CODE-ONLY |
| eval_lanes (registry/contract/native/app_probe/gamut) | ml/pipelines/eval_lanes/ | evaluator lanes by capability | code-only | CODE-ONLY |
| ates spine/observer | ml/pipelines/ates/ | actor/critic/judge arms | ates-orchestrator-benchmark.yml | **DORMANT** — last run 2026-10-22 success; phase-b receipt last 2026-10-23 |
| command_center board | ml/pipelines/command_center/ | session/board ranking | code-only | CODE-ONLY |

Coverage gap: the vocab-v2 PR classifier — the closest thing to a Tier-1
PR router in code — classifies nothing in production. The live PR stream
is classified by section E surfaces instead, in a different vocabulary.

## C. Model selection / routing

| Unit | Defined | Classifies | Trigger | State |
|---|---|---|---|---|
| model_selection_market (selector/market/ledger/dspy_doe/provider_batch/review_evidence/resource_index) | scripts/model_selection_market/ (14 files) | providers/models into selection + quota ledgers | provider-batch.yml, provider-recon-compound.yml | LIVE — provider-batch last 2026-10-28 success; recon-compound **FAIL-LAST** 2026-10-28 |
| model_router + bootstrap | scripts/model_router.py (20 KB) | task → model route | code-only | CODE-ONLY |
| model_performance_index | scripts/model_performance_index.py | model performance tiers | code-only | CODE-ONLY |
| decision_engines | scripts/decision_engines.py (14 KB) | decision rules | code-only | CODE-ONLY |
| provider_model_catalog | scripts/provider_model_catalog.py (20 KB) | provider catalog + secret-name map | provider workflows | LIVE (via provider-batch) |

## D. Delphi system (RFP/proposal classification + weighting)

| Unit | Defined | Classifies | Trigger | State |
|---|---|---|---|---|
| gate.py (45 KB) | scripts/delphi/gate.py | RFP issues → parked/shadow/promoted via labels delphi:* | delphi-gate.yml (issue_comment) | LIVE — runs 2026-10-28 (skips = non-matching comments); 72 open delphi:rfp at last census, all gate-scored |
| cross_vote / method_cycle / generate_proposal | scripts/delphi/ (14–24 KB) | proposals: generation + panel votes + calibration | delphi-cycle.yml, delphi-generate.yml, delphi-oracle-mvp.yml | LIVE — all fired 2026-10-27/28 success |
| participant_cycle | scripts/delphi/participant_cycle.py | research participants (12) arm states | delphi-participant-cycle.yml | **NEVER-RUN** — landed with the 2026-10-28 participants reclassification; its cycle has not fired once |
| rfp_flood_feed + segments + research_axes | scripts/delphi/rfp_flood_feed.py (21 KB), ops/delphi/*.json | RFPs into segments/silos; axes states | delphi-rfp-feed-collect.yml | LIVE — fired 2026-10-28 |
| ledger_feed / ledger_fetch | scripts/delphi/ | ledger comments → feed + Neon mirror currents | delphi-ledger-feed-collect.yml | LIVE — fired 2026-10-28 |
| oracle_panel_feed | scripts/delphi/oracle_panel_feed.py (33 KB) | proposals → public panel feed | oracle-panel-feed-collect.yml | **FAIL-LAST** 2026-10-28 |
| tribute_ingest | scripts/delphi/tribute_ingest.py | tribute outcomes → ledgers | delphi-tribute-ingest.yml | **FAIL-LAST** 2026-10-28 |
| delphi-signal | scripts/delphi/ (workflow_call) | signal fan-in | delphi-signal.yml | NEVER-RUN by design (workflow_call only); bridge fired 2026-10-28 skipped |
| panel.json / ledgers.json / surfaces.json | ops/delphi/ | panel + ledger + surface registries | data | current |

Labels (live, 103 total; classifier families): delphi:board/converged/
needs-access/outcomes/parked/participant/promoted/rfp/shadow/weights (10).

## E. Repo gates & audits

| Unit | Defined | Classifies | Trigger | State |
|---|---|---|---|---|
| repo_gate | scripts/ci/repo_gate.py (35 KB) | every PR: hygiene + portability verdict | repo-gate.yml | LIVE — 2026-10-28 success |
| tribute_system1 (+ participation, tribute audit) | scripts/ci/tribute_system1.py (30 KB) | upstream issues → CPPH-ranked tribute targets | tribute-system1.yml, tribute-participation.yml | LIVE — both 2026-10-28 success |
| reviewer_metrics collect | scripts/reviewer_metrics/collect.py (20 KB) | reviewer surfaces by delivery rate | reviewer-metrics-collect.yml | LIVE — fired 2026-10-28 |
| secrets_audit (phantom) | scripts/secrets_audit/audit.py (14.5 KB) | secret refs → compiled/dead-branch/provisioning | phantom-secrets-audit.yml | LIVE — doc regenerated 2026-10-28T04:27Z (section K) |
| secrets-scan | (workflow) | secret patterns in tree | secrets-scan.yml | **DORMANT** — last 2026-10-05 success |
| comment_quality_sweep | scripts/comment_quality_sweep.py | issue comments → productive/noise (2 deletable classes) | comment-quality-sweep.yml (weekly + dispatch) | **NEVER-RUN** — landed 2026-10-28 (PR #2051); weekly fire + delete-mode dispatch both unproven |
| help_wanted preflight_candidate | scripts/ci/help_wanted_contribute.py + tribute lane | claim candidates → already-claimed block | help-wanted workflows | LIVE — diff-gate tests 2026-10-27 success; help-wanted-diff-gate.yml itself NEVER-RUN |
| _v1_pr_rollup / _v1_mergeable | deepcli/deepcli/ (10 KB / 3 KB) | PRs → rollup/mergeable classes (legacy gen) | code-only (tests only) | CODE-ONLY, superseded in practice by repo_gate + orchestrator |
| session_categories | cli-synthegration/session_categories.py (+ 2 vendored copies) | sessions → categories | code-only | CODE-ONLY; 3 identical copies (drift risk) |

## F. Workflow triage / review classifiers

| Unit | Trigger | State |
|---|---|---|
| peer-review-orchestrator.yml | PR events | LIVE — 2026-10-28 (skipped = path/event gating) |
| gemini-dispatch.yml | dispatch/events | LIVE — fired 2026-10-28 |
| gemini-after-peers.yml | after peer reviews | LIVE — 2026-10-28 success |
| gemini-review.yml | — | **DEAD-ish** — last run 2026-08-20 failure; superseded by dispatch/after-peers |
| gemini-triage.yml | — | **NEVER-RUN** |
| gemini-invoke.yml | — | **NEVER-RUN** |
| gemini-interactions-smoke.yml | — | **NEVER-RUN** |
| cellcog-review.yml | skip-gated | LIVE-gated — 2026-10-28 skipped |
| agent-review-auto-jules.yml | events | LIVE-gated — 2026-10-28 skipped |
| issue-lifecycle-triage.yml | issue events | LIVE — 2026-10-28 success |
| issue-comment-router.yml | comment events | LIVE — fired 2026-10-28 |
| remote-gamut-evaluation.yml | dispatch | **NEVER-RUN** — and its judge key is phantom (section K): dead surface |
| agent-mvt-experiment.yml | dispatch | **NEVER-RUN** |
| team-mvt.yml | events | **FAIL-LAST** 2026-10-28 |

## G. Intake classifiers (issue-template family, all landed 2026-10-28)

| Unit | Defined | Classifies | State |
|---|---|---|---|
| research_intake.py | scripts/research/research_intake.py | research:provider/service issues → seed records | LIVE — research-intake.yml fired 2026-10-28 (burst-proven: exactly 1 record per filing after PR #2137) |
| observatory_intake.py | scripts/github/observatory_intake.py | research issues → observatory provenance (4th signal) | LIVE — inside repository-observatory.yml (2026-10-28 success) |
| apk_xref_intake.py | scripts/apk_xref/apk_xref_intake.py | apk-xref filings → apk-xref/v1 records | LIVE-gated — apk-xref-intake.yml fired 2026-10-28 |
| re_taxonomy_intake.py | scripts/reverse_engineering/re_taxonomy_intake.py | re-taxonomy filings → validated taxonomy nodes | LIVE-gated — fired 2026-10-28 |
| target-intake (validate_brief) | target-intake.yml + brief validator | target briefs → intake plans | LIVE-gated — fired 2026-10-28 |
| proposal-delphi-trigger.yml | workflow | proposals → Delphi trigger | LIVE — last 2026-10-24 success |

Labels: research, research:provider, research:service, apk-xref,
re-taxonomy, target-brief (6 of the 17 classifier-family labels).

## H. Repository observatory (repo census classifier)

repository-observatory.yml + collector: classifies 1,297 integration
repos by provenance signals (starred/forked/watched/issue). LIVE — daily
cron + dispatch, 2026-10-28 success; index: owned 692 / starred 3,128 /
watching 128 (128/128 exact vs live subscriptions). Naming collision with
section A is real (three "observatory" systems: deepcli, repository,
issue-observatory.yml — the last fired 2026-10-28; a fourth,
delphic-bayesian-observatory-lab.yml, is DORMANT since 2026-10-05).

## I. Dashboard / feed classifiers

| Unit | Classifies | State |
|---|---|---|
| surface_feeds (collect_3l0/moneyball/doe/mvt) | surfaces → public dashboard feeds | LIVE — surface-feeds-collect 2026-10-28 success |
| dispatch_tree_feed | workflow dispatches → cadence tree | LIVE (in surface_feeds file set) |
| action-effectiveness-ledger / pr-production-ledger / pr-change-effectiveness-ledger | actions/PRs → effectiveness classes | LIVE — fired 2026-10-28 (one cancelled run = superseded dispatch) |
| hex-moneyball-evidence | moneyball evidence artifacts | LIVE — last 2026-10-24 success |

## J. Provider substrate classifiers

| Unit | Classifies | State |
|---|---|---|
| provider-batch reconcile (claims) | upstream catalogs → per-family claims (totals 187 at last pin) | LIVE — contracts gate repaired PR #1780; diagnose run 40508502147 success |
| quota registry + quota-dispatch-tree / quota-router-regression | quota families → dispatch routes | dispatch-tree LIVE 2026-10-28; router-regression **DORMANT** since 2026-10-21 |
| openrouter-free-catalog-sync | OpenRouter catalog → free-route allowlist state | LIVE — 2026-10-28 success |
| provider-recon-compound | provider recon fan-in | **FAIL-LAST** 2026-10-28 |

## K. Phantom-secret audit surface (steward: this lane)

- audit.py classifies every `secrets.*` reference as provisioned /
  compiled / dead-branch / provisioning-needed. Doc regenerated
  2026-10-28T04:27Z: **60 phantom names / 139 references** (provisioning
  114, compiled 20, dead-branch 5) — down from 73/165 on 2026-10-27;
  burn-down is moving (Actions secrets 41 → **53** in the same window).
- Intersections with this census: **GAMUT_JUDGE_API_KEY still phantom** →
  section F gamut stays dead. **NEON_API_KEY +
  LANE_EVENTS_DATABASE_URL**: neon-fix lane reports provisioning in
  progress 2026-10-28 (unverified until its PR + run land). Classifier/
  provider subset (~34 names) is owned by the account-creation lane
  (created 2026-10-27 on owner order); steward verifies flips via audit.
- provision-secrets.yml last ran 2026-10-19 success (the provisioning
  route used by lanes).

## L. External classifier surfaces (delivery per reviewer_metrics)

CodeRabbit (delivery 0.173 at the 2026-10-25 map), Devin, Qodo, ECC
Tools, Gemini 2nd pass, CellCog, Jules/Bolt. Not repo-run; classified
here because they classify the same PR stream as sections B/E — the
fleet's effective Tier-1 review layer is mostly these + the orchestrator.

## Overlaps

- **O1. PR classification ×4 generations:** _v1_pr_rollup (legacy,
  code-only) → ml classify_pr vocab v2 (dormant) → peer-review-
  orchestrator + external reviewers (live) → issue-lifecycle-triage
  (issues side). No generation was retired when the next landed.
- **O2. Gemini ×6 workflows:** dispatch + after-peers live; review dead
  since 2026-08-20; triage/invoke/interactions-smoke never ran. The
  live path works; the dead three still occupy the namespace.
- **O3. MoneyBall ×3:** ml/pipelines scorer (code-only), Oracle-pass
  explained scoring (per-pass manifests), hex-moneyball-evidence +
  surface-feeds rendering. Two planes chartered 2026-10-28 (MoneyBall
  plane PR #2201, 3L0 plane PR #2202) to disentangle — in progress.
- **O4. Secret classification ×3:** phantom audit (live, weekly-class),
  secrets-scan (dormant since 2026-10-05), provision-secrets (the write
  side, 2026-10-19). Only the phantom audit is current.
- **O5. "Observatory" ×4:** deepcli quartet, repository observatory,
  issue-observatory, delphic-bayesian lab (dormant). Name collision is a
  standing confusion source in cross-lane traffic.

## Top gaps

1. **No production PR classifier.** Vocab-v2 classify_pr is dormant
   (keepalive last fired 2026-10-21); nothing classifies the live PR
   stream into the fleet's own disposition vocabulary.
2. **Gamut is dead end-to-end:** remote-gamut never ran, eval_lanes
   gamut is code-only, GAMUT_JUDGE_API_KEY phantom.
3. **Never-run set (9):** agent-mvt-experiment, comment-quality-sweep,
   delphi-participant-cycle, gemini-interactions-smoke, gemini-invoke,
   gemini-triage, help-wanted-diff-gate, recon-intel-reconcile,
   remote-gamut-evaluation (+ delphi-signal by design). Three of these
   landed within the last week — built, not yet exercised.
4. **Fail-last cluster (2026-10-28):** oracle-panel-feed-collect,
   delphi-tribute-ingest, provider-recon-compound, team-mvt — four
   classifiers red on their most recent run, same day.
5. **Dormant set:** ates benchmark (2026-10-22), secrets-scan
   (2026-10-05), delphic-bayesian lab (2026-10-05), quota-router-
   regression (2026-10-21), ml keepalive (2026-10-21), tribute-vercel-
   prod (fail, 2026-10-22).
6. **No classifier registry.** This sweep is the first unified one;
   SYSTEM-ONE-CATALOG covers external models only. Sections A–L exist
   in no single in-repo index — this doc is the seed of one.
7. **Phantom-gated classifiers:** beyond gamut, any provider classifier
   whose key sits in the 60-name phantom set is one secret away from
   dead; the burn-down (73→60) is the fix in motion.

*Method note: run states are the runs API's 3 most recent per workflow;
"skipped" conclusions on event-triggered workflows are the gate working,
not failures. Counts are live-derived at pull time, never copied from
dated docs.*
