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
| CodeQL advisories (python 172s · actions 80s · js/ts 75s) | Σ 327s (n=1) | ≈5.5 | per-PR | Largest single per-PR draw; the per-day figure is a derived view — see Revision 2026-11-02b (record `pr_tempo_per_day` × this measured draw) |
| All checks on a code-touching PR head | Σ ≈13–14 min (53 check-runs, PR #3335 head) | ≈13–14 | per-PR | Includes duplicate fan-out instances (ledger ×6, sweep ×2) |

## Chronic-red price (ALE = SLE × ARO)

> **Superseded as a pricing surface by Revision 2026-11-02b (end of file)** — per the DoE bayesian-updating v0 shape ruling (PR #3724), prices live in expectation records and ALE is a derived view only. This table is retained as the evidence summary the records were built from; where any figure here and a posterior differ, the posterior governs.

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

## Revision 2026-11-02b — expectation records (DoE bayesian-updating v0, PR #3724)

Shape ruling applied: per candidate ONE expectation record `{quantity, prior{value,basis}, evidence[]{source,direction,likelihood,corroboration}, posterior{value,range,updated_at,n_evidence}}`. ALE and the risk matrix are derived views of the ARO/SLE posterior pair — no parallel hand-computed numbers; where a view and a posterior disagree, the record is defective and the posterior governs. Weighting per rule 9: corroborated legs update at full strength, single-leg held/provisional, disputed excluded, self-asserted ~no movement; unknowns widen the range, not the point. Unevidenced quantities are labeled **INTAKE**.

### Records

**`baseline5.aro` — failure probability per PR head (baseline-5 red checks)**
- prior: {value: 0.5, basis: uninformative — chronic-red hypothesis untested at map v0}
- evidence: [{source: "check-runs on 11 factory PR heads, PRs #3257–#3401 (runs #1–#11)", direction: up, likelihood: "failed on 11/11 heads", corroboration: corroborated (firsthand API check-run records)}]
- posterior: {value: 0.92, range: 0.75–1.0, updated_at: 2026-11-02, n_evidence: 11}

**`baseline5.sle` — Actions-minutes wasted per occurrence**
- prior: {value: 2.0, basis: order-of-magnitude placeholder before measurement}
- evidence: [{source: "check-run durations, PR #3335 head (discover 17s + ledger instances ≈50s + collect-peer-responses 5s + collect redacted PR evidence 11s ≈ 83s)", direction: down, likelihood: "measured Σ ≈1.4 min on the sampled head", corroboration: single-leg (n=1 head) — held provisional}]
- posterior: {value: 1.4, range: 0.8–2.5, updated_at: 2026-11-02, n_evidence: 1}
- Note: the governing SLE for priority is gate-signal degradation (these checks are not required gates; merges proceeded on all 11 heads) — a qualitative impact carried in the risk render, not in this minutes record.

**`pr_tempo_per_day` — PRs created per day, repo-wide**
- prior: {value: 60, basis: fleet-tempo impression, weak}
- evidence: [{source: "PR numbering Δ #3253→#3401 ≈ 148 created over ≈27h (2026-11-01→02)", direction: up, likelihood: "implies ≈130/day in-window; peak-tempo caveat applies", corroboration: single-leg (one window) — held provisional}]
- posterior: {value: 130, range: 70–160, updated_at: 2026-11-02, n_evidence: 1}

**`fabric_mint.aro` — failure probability per remote-knowledge-fabric run at App mint**
- prior: {value: 0.3, basis: mint auth failures usually intermittent/config-local}
- evidence: [{source: "run records 2026-10-21→26: 6/6 runs failed at mint (APP_PRIVATE_KEY class)", direction: up, likelihood: "6/6 in window", corroboration: corroborated (mgr-relayed run census + ICM's own #3350 fix-pattern proof on the same mint shape)}]
- posterior: {value: 0.86, range: 0.6–1.0, updated_at: 2026-11-02, n_evidence: 6}
- `fabric_mint.sle` (minutes): **INTAKE** — runs exit early; no duration evidence carried. ALE therefore not derivable; the item's value class is unblocking (manifest staleness), not minutes.

**`codeql.draw_min_per_pr` — measured draw (not a risk quantity)**
- evidence: [{source: "check-run durations, PR #3335 head: 172+80+75 = 327s", direction: n/a (measurement), corroboration: single-leg (n=1) — provisional}]
- posterior: {value: 5.5 min, range: not yet established (n=1), updated_at: 2026-11-02, n_evidence: 1}

### Derived views (computed from the posteriors above; never stored as independent figures)

- **Baseline-5 ALE** = `baseline5.aro` × `baseline5.sle` × `pr_tempo_per_day` = 0.92 × 1.4 × 130 ≈ **170 Actions-min/day**; derived range from posterior ranges ≈ 40–400. (The ≈180 in the superseded table sits inside this range; the record governs.)
- **CodeQL daily draw** = `codeql.draw_min_per_pr` × `pr_tempo_per_day` = 5.5 × 130 ≈ **715 Actions-min/day**; derived range ≈ 385–880 on tempo range alone (draw range unestablished at n=1).
- **Risk render (discretized from the posterior pairs):** baseline-5 = likelihood HIGH (ARO posterior 0.92) × impact LOW-minutes / MEDIUM-signal ⇒ fix for signal integrity. Fabric mint = likelihood HIGH (0.86) × impact staleness-class ⇒ unblocking, S-size (fix pattern proven PR #3350).

### INTAKE (unevidenced — no posterior, no price)

- `tribute_telemetry.duration` + its ALE — evidence route: check-runs of any tribute-path PR. (Its deadline-exposure risk statement in the flagged table is a likelihood judgment with its evidence leg stated there; it carries no numeric price until this record exists.)
- `hygiene_sweep.duration` — route: one tree-fired run's job timestamps.
- Central-remainder (~340 files) trigger/duration — route: code-search across 270 workflows + ci-sweep script payload.
- Thin-floor areas' ARO/SLE pairs — route: first incident postmortem per area ∨ coverage/fault-injection pass.
- `fabric_mint.sle` — route: durations of the failed runs from the Actions run records.
