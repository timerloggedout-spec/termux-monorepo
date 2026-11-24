# BRR Cross-Repository DoE

Campaign: `brr-cross-repo-doe`  
Design: `DESIGN.json`  
Evaluator: `evaluate.py`  
Dataset contract: `dataset.schema.json`  
Proposal: `docs/proposals/active/brr-cross-repo-doe/`

## Purpose

Measure how accurately existing repository evidence helps an agent find relevant branches, commits, PRs, issues, regression context, and related discussion references across repositories.

This is a separate DoE campaign. It consumes existing exports and graph records; it does not replace or extend BRR's authority.

## Existing sources

- BRR v2 registry and delta exports — source-owned by existing BRR machinery.
- QUE #5552 — differential regression checks and feature-progress map.
- QUE #5640 — BRR + commit + regression + comment/context graph join.
- Context Relationship Graph and cross-plane graph — verified relationship evidence and separately labeled candidates.

The campaign does not create another BRR collector, queue, scheduler, graph store, or dashboard. Runtime automation must attach to the existing export/event path.

## Four comparison arms

| Arm | Evidence |
|---|---|
| `lexical` | Repository, branch, commit subject, PR/issue title metadata |
| `branch_commit` | BRR ancestry/disposition + commit lineage |
| `context_graph` | Verified context/comment graph relationships |
| `fused` | Equal-weight lexical + branch/commit + graph + regression signals |

Each frozen query is evaluated by all four arms. Queries are blocked by repository and task family. The minimum confirmatory cohort is 30 adjudicated queries across at least 3 repositories and 3 task families.

Seed discovery targets include the exact term `gitReverse` (repository/branch/commit identity remains unresolved until verified evidence is found), [fast-anything_fork](https://github.com/timerloggedout-spec/fast-anything_fork), and [rust-anything_fork](https://github.com/timerloggedout-spec/rust-anything_fork). Repository names seed searches; they do not count as verified branch or commit relationships.

## Outcomes and decision rule

Primary: macro F1@5 against the frozen, human-adjudicated gold target IDs. Precision@5 uses a fixed denominator of five (missing ranks count as misses); recall@5 divides hits by the gold target count; F1@5 is their harmonic mean.

Secondary: precision@5, recall@5, mean reciprocal rank, candidate-only leads, source coverage, unresolved/untestable fraction, and ranking latency.

The fused arm becomes a champion candidate only when the preregistered sample and coverage requirements are met, its F1@5 improvement is at least 0.05 absolute, the paired 95% bootstrap interval has a lower bound above zero, and verified precision@5 does not regress. Adoption remains subject to independent review and existing gates.

## Dataset contract

The evaluator accepts an offline JSON snapshot conforming to `dataset.schema.json`. Every candidate uses repository-qualified identity:

`owner/repository::branch@commit_sha`

Candidate records preserve the full unique commit SHA list, PR numbers, issue numbers, regression verdict and untestable/no-benchmark reason, plus graph-edge confidence and evidence URLs.

Each source carries an immutable SHA, observation timestamp, coverage state, and evidence URL. A complete dataset includes BRR and commit receipts for every covered repository, plus regression, graph, and adjudicated gold-set receipts. Each query carries adjudicated gold target IDs. Candidate graph edges remain separate from verified evidence and never count as verified hits.

## Execution

```bash
python3 scripts/doe/brr_cross_repo_doe.py \
  --dataset path/to/frozen-dataset.json \
  --output-dir experiments/doe/brr-cross-repo-doe/records \
  --summary experiments/doe/brr-cross-repo-doe/SUMMARY.json
python3 -m unittest discover -s tests -p 'test_brr_cross_repo_doe.py' -v
```

The runner is offline and deterministic for a frozen dataset. It does not fetch GitHub or private-store data and does not mutate repositories. It writes a SHA-256-addressed dataset snapshot and one immutable record per query × arm; identical replays are idempotent and conflicting rewrites fail closed. The summary includes ranked target IDs, scores, and per-signal breakdowns.

## Current state and limits

`admitted_design_only`. The VM-published BRR v2 registry and joined cross-repository records remain the runtime dependency. Issue #5552 records that its 2026-11-17 private registry export was unavailable to the current GitHub session and that a full cycle and consumer read remain outstanding. The campaign records this as pending; it does not fabricate source rows, complete coverage, run receipts, or a winner.

One observation is one query under one arm and emits one record conforming to `docs/ops/corpus/EXPERIMENT.schema.json`. Historical observations are retained; design amendments create a new design revision/cohort.
