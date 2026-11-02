# Test Suite Timing Map — termux-monorepo

Owner: ICM lane (Repo Organization tree) · Consumer: Cadence lane (timed test plan) · Status: v1, 2026-11-02
Method: durations from check-run timestamps (started_at→completed_at) on sampled PR heads; trigger classes from the workflow YAML of record; Actions-minutes = duration/60 on 1 ubuntu runner. Trigger vocabulary (Cadence consumer classes): `per-PR | merge-queue | tree-scheduled | on-demand`, with `path-filtered` as a modifier. Scores are Bayesian posteriors on the stated samples and are expected to move on the named update routes. Unmeasured suites are **unpriced + flagged**, never estimated.

## Priced suites

| Suite | Workflow | Contents | Duration | Actions-min | Trigger class | Price / ALE |
|---|---|---|---|---|---|---|
| Hygiene + portability gate | `repo-gate.yml` | unittest discover on 9 named files (test_repo_gate_index_scope, test_orchestration_contract_validator, test_dag_execution, test_dag_properties, test_briefing_contract_validator, test_curate_briefing_sources, test_emit_agent_throughput, test_procurement_edge_contracts, test_vercel_ignore_commands) + source-citations job | 22s (n=1) | ≈0.4 | per-PR + merge-queue (push master/master-staging) + on-demand leg | Passing gate; cost line only |
| Agentic termux smoke | `termux-smoke.yml` | test_termux_smoke.py | 10s (n=1) | ≈0.2 | per-PR + merge-queue (push master/master-staging/termux-smoke) + on-demand leg | Passing gate; cost line only |
| Flywheel offline core loop | `flywheel-validate.yml` | test_flywheel.py + test_dependency_phase*.py | 21s (n=1) | ≈0.4 | per-PR, path-filtered (scripts/agentic/**, scripts/ci/{repo_gate,termux_smoke}.py, flywheel test paths, dependency-phase fixtures/doc, self) + on-demand leg | Passing gate; cost line only |
| ci-sweep ("sweep") | `ci-sweep.yml` | Script-carried sweep operations; no direct unittest invocation in YAML | 18–19s per instance (×2 instances on sample head) | ≈0.3/instance | tree-scheduled (cadence owned by quota-dispatch-tree, #1573; fires via workflow_dispatch) | Cost line; instance duplication is a timing-model input |
| DeepWiki import harvest (reference point, not a test suite) | `deepwiki-import-harvest.yml` | Structure harvest job | 15s job total (run 41367735561) | ≈0.25 | on-demand + push (master, docs/icm/**) | Cost line |

## Priced non-suite draw (per-PR head, for draw math)

| Item | Duration | Actions-min | Trigger class | Note |
|---|---|---|---|---|
| CodeQL advisories (python 172s · actions 80s · js/ts 75s) | Σ 327s (n=1) | ≈5.5 | per-PR | Largest single per-PR draw; ≈700 Actions-min/day at the current-tempo posterior (≈130 PR/day, numbering Δ #3253→#3401 over ≈27h — peak-tempo caveat) |
| All checks on a code-touching PR head | Σ ≈13–14 min (53 check-runs, PR #3335 head) | ≈13–14 | per-PR | Includes duplicate fan-out instances (ledger ×6, sweep ×2) |

## Chronic-red price (ALE = SLE × ARO)

| Item | ARO | SLE | ALE | Class |
|---|---|---|---|---|
| Baseline-5 red checks: discover (17s) · ledger instances (≈50s Σ) · collect-peer-responses (5s) · collect redacted PR evidence (11s) | ≈1.0 per PR head (failed on 11/11 sampled factory PR heads, runs #1–#11) | ≈1.4 Actions-min wasted execution per head; real SLE = gate-signal degradation (not blocked merges — these are not required gates) | ≈180 Actions-min/day (interval ≈90–260 across tempo/minute ranges) | Unblocking |
| remote-knowledge-fabric mint failure | 1.0 per run in observed window (6/6 runs failed 2026-10-21→26 at App mint) | Minutes unpriced (early-exit runs); SLE = knowledge-fabric manifest staleness | Unpriced | Unblocking; fix pattern proven (app-id mint, PR #3350) |

## Unpriced + flagged (priors + update routes, no invented precision)

| Suite / block | Trigger class | Prior | Evidence that updates |
|---|---|---|---|
| tribute-telemetry-tests ("Targeted telemetry regression tests", `tribute-telemetry-tests.yml`) — targeted unittest over tribute scripts | per-PR, path-filtered (tribute workflows, scripts/ci/tribute_*.py, apps/help-wanted-dashboard/index.html, telemetry docs) | Highest deadline-exposure item in the Tests slate: legacy-name coupling is certain to engage during the help-wanted → tribute rename (8 central tribute test files; 430-file rename census) × rename-tranche delay | Check-runs of any tribute-path PR (duration) · the rename sweep's first test-tranche run (failure/re-run minutes) |
| hygiene-sweep (`hygiene-sweep.yml`) | tree-scheduled (dispatch-tree owned) | Small (sibling sweep shape) — stated as prior only | One tree-fired run's job timestamps |
| Central suite remainder: ~340 of 354 files under `tests/` not invoked by name in the gate workflows above | NOT_ESTABLISHED | Cannot score a suite whose trigger and duration are unmeasured | Code-search `unittest discover` / `pytest` across all 270 workflows + ci-sweep's script payload |
| Thin-floor areas (test-count census 2026-11-02): cli-synthegration 79 src/0 tests · archwiz 94/2 · termux-multi-agent 67/2 · multi-ai-cli 15/0 · nexuscli 6/0 · hub_mcp 6/0 | (execution surface per remainder row) | Regression-escape cost unmeasured; no incident history in ICM records. Impact prior raised for archwiz (dispatch surface). Note: she (38 src/0 in-area) is covered centrally by 20 she-* files in `tests/` — not a thin area | First incident postmortem per area, or a coverage/fault-injection pass |

## Provenance

- Test census: per-area recursive git trees @master, 2026-11-02 (ICM priorities-window slice 2).
- Timing sample: check-runs on PR #3335 head `fb27c7f4` (53 runs) + harvest job record 41367735561; failure frequency: PRs #3257–#3401 (factory runs #1–#11).
- Update protocol: append dated revision sections; never rewrite prior figures (freeze rule — additive only). Multi-head timing pull (10–20 PR heads) is the named next measurement on manager word.
