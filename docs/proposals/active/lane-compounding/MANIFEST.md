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
    status: requested
  - id: Hark
    role: author+executor
    status: executing
related_prs: [1244, 1274, 1277, 1278, 1280, 1447]
related_branches:
  - hark/lane-compounding
  - docs/biudl-audit-dossier-20261021
gates_required: [repo-gate]
---

# MANIFEST — lane-compounding

## Summary

BIUDL slice (broad → identify lane → thin slice → validate → broaden). The repository already owns the canonical evidence layer (GitHub JSONL / ATES, ForeSight spine, sweep ledger) and the decision math (dependency-phase DAG, Bayesian routing). This proposal stacks them instead of adding a parallel store:

1. **Live dashboard data (slice 1, this PR).** The Tribute dashboard and lane matrix fetched the Vercel-baked `data/*.json` first and only fell back to master. Deploys are intentionally not triggered by data pushes (Hobby quota), so the live page showed data frozen at the last code deploy. Order is now: raw master JSON first, baked copy as offline fallback. Data freshness no longer costs deployments.
2. **Tribute qualification posteriors.** Reduce `help-wanted-evidence/*.jsonl` receipts into Beta-Bernoulli posteriors per lane and per upstream repo (`scripts/bayesian_routing.py` primitives), gated by `help_wanted_diff_gate.py --expect solution` so stakes never count as solutions.
3. **Markov tribute-state chain.** Transition counts STAKE → SOLUTION → MERGED | CLOSED per lane; expected time-to-merge and absorption probabilities. No Markov code exists yet.
4. **ATES value-of-information.** Pick the next audit/scout by posterior uncertainty × DAG criticality (`dependency_phase_engine.py`, `gantt_projection.py`).
5. **ForeSight → HindSight calibration.** ForeSight registers each forecast (append-only, `evidence_hash`); HindSight `retain/recall/reflect` scores it after outcome and recalibrates priors. HindSight's PostgreSQL + pgvector is the only role here that needs a hosted database.
6. **Blind-graded treatments.** n8n (bridge wired, webhook unset), Bifrost (#611), Temporal (P1 observational), Neon (mirror / HindSight), Platform201 Solo (host only: 3 containers, 0 queue nodes), GitHub JSONL (control) are graded through `blind-agent-evaluation` and ranked by MoneyBall/3L0 after the evaluation boundary, replacing the earlier single-author 30-point scores.
7. **DAG execution + corpus audit.** Issue #1443 and PR #1447 document and test the existing dependency-phase engine; the audit preserves the historical corpus's parser failures, unresolved reference, and independent checkpoint-eligibility gate. It does not create a second scheduler or promote the corpus.

## Non-goals

- No new canonical store; GitHub JSONL / ATES remains authority.
- No Neon writes or secret changes without operator approval (#1277 stays a no-op).

## Quota constraints (see ops/quota/registry.json, PR #1280)

Vercel Hobby 100 deployments/day; repo GITHUB_TOKEN 1,000 requests/hour (exhausted 2026-10-19 03:07 PDT); Neon Free 100 CU-hours/project/month.
