---
id: lane-compounding
title: "Lane compounding: live dashboard data, Bayesian/Markov tribute qualification, ForeSight→HindSight calibration, blind-graded store/orchestrator treatments"
author: Hark
posted_at: 2026-10-19
source: (none - direct proposal, BIUDL thin slice)
status: posted
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: Hark
    role: author+executor
    status: executing
related_prs: [1244, 1274, 1277, 1278, 1280, 1447]
related_branches:
  - hark/lane-compounding
  - docs/biudl-audit-refresh-20261021
gates_required: [repo-gate]
---

# MANIFEST — lane-compounding

## Summary

BIUDL slice (broad → identify lane → thin slice → validate → broaden). The repository already owns the canonical evidence layer (GitHub JSONL / ATES, ForeSight spine, sweep ledger) and the decision math (dependency-phase DAG, Bayesian routing). This proposal stacks them instead of adding a parallel store:

1. **Live dashboard data (slice 1, this PR).** The Tribute dashboard and lane matrix fetched the Vercel-baked `data/*.json` first and only fell back to master. Deploys are intentionally not triggered by data pushes (Hobby quota), so the live page showed data frozen at the last code deploy. Order is now: raw master JSON first, baked copy as offline fallback. Data freshness no longer costs deployments.
2. **Tribute qualification posteriors.** Reduce `tribute-evidence/*.jsonl` receipts into Beta-Bernoulli posteriors per lane and per upstream repo (`scripts/bayesian_routing.py` primitives), gated by `tribute_diff_gate.py --expect solution` so stakes never count as solutions.
3. **Markov tribute-state chain.** Transition counts STAKE → SOLUTION → MERGED | CLOSED per lane; expected time-to-merge and absorption probabilities. No Markov code exists yet.
4. **ATES value-of-information.** Pick the next audit/scout by posterior uncertainty × DAG criticality (`dependency_phase_engine.py`, `gantt_projection.py`).
5. **ForeSight → HindSight calibration.** ForeSight registers each forecast (append-only, `evidence_hash`); HindSight `retain/recall/reflect` scores it after outcome and recalibrates priors. HindSight's PostgreSQL + pgvector is the only role here that needs a hosted database.
6. **Blind-graded treatments.** n8n (bridge wired, webhook unset), Bifrost (#611), Temporal (P1 observational), Neon (mirror / HindSight), Platform201 Solo (host only: 3 containers, 0 queue nodes), GitHub JSONL (control) are graded through `blind-agent-evaluation` and ranked by MoneyBall/3L0 after the evaluation boundary, replacing the earlier single-author 30-point scores.
7. **DAG execution and corpus audit.** The DAG audit dossier documents the existing dependency-phase engine and corpus quality gates. It preserves the distinction between execution ordering, historical relationship evidence, and quota/decision policy.

## Non-goals

- No new canonical store; GitHub JSONL / ATES remains authority.
- Neon writes within the provisioned lane-events scope are authorized; new Neon write surfaces or secret changes still require operator approval.

## Quota constraints (see ops/quota/registry.json, PR #1280)

Vercel Hobby 100 deployments/day; repo GITHUB_TOKEN 1,000 requests/hour (exhausted 2026-10-19 03:07 PDT); Neon Free 100 CU-hours/project/month.

## Decisions of record (2026-11-03, owner delegation to main)

1. **Operator-authorizer: ACCEPTED** — 2026-11-03, by owner delegation to main.
2. **LC-003 … LC-007: AUTHORIZED** to proceed under Hark as executor; outputs through MoneyBall/3L0 as designed.
3. **LC-002: APPROVED conditioned on firsthand verification of LC-001.** Verification (Docs lane, 2026-11-03): **FAIL** — the served dashboard's raw-first source names `docs/ops/generated/Tribute-status.json` (capital T), which returns 404 on master (the file of record is `tribute-status.json`, lowercase); the page therefore loads its baked fallback copy, so LC-001's mechanism is not live and the served stamp is the baked copy's, not master's. Per the condition, LC-002 is **HELD** and the data-path triggers in `tribute-dashboard-deploy.yml` are NOT dropped.
4. **LC-008: DECIDED** — overtaken by events: the #1277 Neon lane_events writer is LIVE as the Neon lane-events recorder under the 2026-10-28 end-to-end provisioning (recorder run 40770746018, rows verified; Neon is the primary store per owner scope correction). The keep-no-op branch is dead.
5. PR #1278 — **DECIDED + CLOSED** by main under this delegation (2026-11-03; close comment 6606592898): superseded by the cadence-law migration — help-wanted-scout.yml and help-wanted-status-refresh.yml retired from master, merge-promotion-queue-v3.yml schedule-free; the PR's ~50-runs/day goal achieved and exceeded. NOT merged (merging would resurrect retired workflows).
6. **Non-goal clause RESTATED** (not removed): Neon writes within the provisioned lane-events scope are authorized; new Neon write surfaces or secret changes still require operator approval.
