---
name: deepseek-provenance
description: Evidence-first procedure for attributing DeepSeek/Termux automation across GitHub, Actions, local deepcli, and agent workers without equating the shared GitHub actor with the acting agent.
---

# DeepSeek Provenance

## Purpose

Reconstruct who/what produced a DeepSeek-related GitHub observation while preserving uncertainty. A shared GitHub identity such as `timerloggedout-spec` is an account boundary, not sufficient evidence of agent identity.

## Evidence hierarchy

Prefer direct evidence in this order:

1. GitHub Actions workflow run, job, step, and SHA.
2. Explicit experiment ID and prompt variant emitted by the worker.
3. Provider/model telemetry tied to the same run.
4. Issue/PR event and timestamp correlation.
5. Explicit local provenance records from `deepcli`, `providence.py`, `fragment_matcher.py`, `synthegration`, or related indexes.
6. Lexical, timing, or co-change heuristics only as `candidate` relationships.

Never infer agent identity solely from commit author, issue commenter, or GitHub account.

## Required observation fields

For each experiment, retain metadata only:

- repository
- run ID / job ID when available
- commit SHA
- target issue or PR number
- provider
- requested model
- observed model when available
- workload role
- experiment ID
- prompt variant
- status
- error class
- latency when available
- token counts when available
- attribution confidence
- evidence URLs or source locations

Do not persist issue bodies, PR bodies, review bodies, cookies, tokens, authorization headers, session databases, or browser state.

## Outcome separation

Keep these dimensions independent:

- routing: intended provider/model selected
- admission: provider accepted the request
- execution: a model response was returned
- task outcome: response was correct/useful
- attribution: evidence strength for the acting worker

A 429, quota error, authentication rejection, or pre-execution timeout is not evidence of poor model quality.

## Local `deepcli` relationship

The Termux `.zshrc` alias is an operator-side invocation path. It may produce valuable provenance evidence, but local session state must not be copied into CI. Exported session material is sensitive and remains outside tracked worktrees.

## GitHub relationship graph

When reconstructing intersecting lanes, query exact PR/issue/file roots first. Report `verified` relationships separately from `candidate` relationships. Use explicit GitHub timeline references when available. Do not turn graph discovery into comments, labels, or routing decisions automatically.

## 3L0 / MoneyBall

Score the integrated outcome, not the loudest actor. A useful attribution record allows the manager to compare workers and orchestration strategies without counting every PAT-signed commit as human or as one specific agent.

## Promotion discipline

Never promote a provider/model or worker attribution rule from one observation. Require repeated observations, a peer comparison, and enough evidence to distinguish provider admission from model execution and task correctness.
