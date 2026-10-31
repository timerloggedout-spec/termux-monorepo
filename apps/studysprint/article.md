# StudySprint — a study plan you can trust, built with the Strands Agents SDK

[MUSEai]@{role:{challenge-entries-manager-d1}} — Builder Center article
draft for the D1 submission (publish via the fleet Builder session).

## The problem

First-generation college students often get a syllabus and nothing
else: no family playbook for turning twelve weeks of topics and due
dates into a daily plan. The failure mode is quiet — a missed week
compounds, and by the midterm the plan is fiction.

## The agent

StudySprint is an agent built with the Strands Agents SDK. Give it a
syllabus and it produces a week-by-week study plan (a learn block and
a retrieval block per topic), daily recall quizzes, and — when life
happens — a re-plan that folds a missed week forward instead of
pretending it went fine.

## The starting agent, and what it already did

StudySprint extends our D0 mandate-practice agent, stated plainly as
the D1 rules require. The starting agent is the **Delphi Oracle**: a
deterministic evidence gate that judges a proposed action against an
evidence set and returns ALLOW_RECOMMENDATION / ABSTAIN / ESCALATE,
failing closed. In D0 ("Give your Agent a Tool") we gave it its one
new tool, `fetch_evidence` — read-only artifact retrieval that
assembles provenance-, freshness- and hash-stamped evidence sets.
Its receipts: asserted evidence only → ABSTAIN; a fetched pull
request (103 stamped items) → ALLOW_RECOMMENDATION; a
credential-mutation request → ESCALATE even with material evidence.

StudySprint keeps that gate and that tool verbatim (vendored in
`foundation/`), because a study plan has the same trust problem: a
plan built on a *claimed* syllabus is a plan built on a guess.

## The new tool

`fetch_study_evidence` adds the two artifact kinds a student actually
has — a **syllabus** and a **practice set** — in the same stamped
evidence shape. The agent's loop is the D0 loop, domain-shifted:
judge on asserted evidence (ABSTAIN) → fetch the syllabus evidence
set → judge again → only then build the plan and quiz.

When the Strands SDK is present, StudySprint's tools register on a
Strands `Agent` directly (`build_strands_agent` in `agent.py`); the
workshop behind this entry — "Building AI Agents with Strands SDK:
From Simple Loops to Multi-Agent Swarms", completed in-window on
2026-10-30, all seven modules — is where that surface was exercised
end-to-end, including deployment to AgentCore Runtime.

## What it does, concretely

Against the sample syllabus in the repo (`examples/syllabus.json`,
BIO 101, 3 weeks, 6 topics), the demo produces: ABSTAIN on the
asserted-only request; then, on the fetched syllabus,
ALLOW_RECOMMENDATION with a 12-session plan, a week-1 recall quiz,
and a re-plan carrying week 1's 4 sessions into week 2. Every run
emits a hashed receipt (`evidence/demo-run.json`) — decisions,
evidence set, plan, quiz — so what the agent judged is exactly what
you can inspect.

## Honesty lines

The demo runs locally and offline; no live deployment of StudySprint
itself is claimed. The sample syllabus is synthetic. The gate's
kernel is a deterministic baseline — no model ballots are represented
in its receipts. Where the SDK is installed the same tools run under
a Strands Agent; where it is not, the identical gate loop runs
standalone, and the receipt says which.

## Repo + demo

Public repo: https://github.com/timerloggedout-spec/studysprint
Starting-agent (D0) repo: https://github.com/timerloggedout-spec/delphi-oracle
Demo video (1:10, public): https://www.youtube.com/watch?v=N3HBRV4LOGQ
Demo: under 3 minutes, scripted in `demo-script.md`, runnable as
`demo.py`, receipts in `evidence/demo-run.json`.
