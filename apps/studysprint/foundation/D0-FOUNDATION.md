# StudySprint foundation — D0 prerequisite pattern (extracted 2026-10-30)

[MUSEai]@{role:{challenge-entries-manager-d1}} #320 #1734

## Rule
D0 = prerequisite for D1 (owner ruling 2026-10-30). StudySprint extends
the D0 mandate-practice agent, not a from-scratch build.

## D0 package census (firsthand, monorepo @master)
Source: `apps/weekend-challenge-delphi-oracle/` in
timerloggedout-spec/termux-monorepo, landed PR #1702 merged aa110a5e,
log flip PR #1703 merged 396d07441b. Platform submission = 0
(completion record only, window ended).

| File | Size | Blob sha | Role |
|---|---|---|---|
| agent.py | 3682 | cf712eb140880ded23a5798dcc370e7eb56d5e6a | starting agent + tool loop, receipt/v1 |
| fetch_evidence.py | 4929 | 8442d8135ee276c16290e770ce6f37595f575ce0 | the one new tool |
| lambda_handler.py | 1199 | bd60f97315a441a0e4c9abd407041cf49899c61a | Lambda packaging, runs locally |
| ENTRY.md | 2787 | edd731c28739582e602b0939d268ec740aca4d0d | article-shaped entry text |
| README.md | 2439 | 39f717f536c2a33f22b0851080457db59ab001b5 | package map + honesty lines |
| demo.py | 2876 | a53f0bceb10ee4628cff8feaff435b0be93dabd8 | 3-scenario demo |
| demo-script.md | 1573 | f67a5f4107164a0d8da9a41a015df85e7a6f4a23 | <3min narration |
| evidence/demo-run.json | 59986 | (dir 759dc8b5) | captured run |
| tests/test_weekend_challenge_delphi_oracle.py | - | in monorepo tests/ | 5 offline tests |

Starting agent kernel: `scripts/delphi/strands_oracle_mvp.py`
(18532 B, blob 9a4a1c78bf4367ab8805d3d55357700a776bbbb0, PR #1620)
= deterministic_oracle: ALLOW_RECOMMENDATION / ABSTAIN / ESCALATE,
fails closed, consequential classes escalate before evidence weighed.

Demo receipts (evidence/demo-run.json, verified):
asserted-only => ABSTAIN, 0 calls, 0 items;
PR #1620 fetched => ALLOW_RECOMMENDATION, 2 calls, 103 items;
credential_mutation + fetched file => ESCALATE, 1 call, 3 items.

## Reusable verbatim
- `fetch_evidence.py` => copied verbatim to `foundation/fetch_evidence.py`
  in this repo (provenance/freshness/hash stamped evidence sets,
  GET-only, CountingTransport). Generic over PR/file/workflow_run.
- Receipt shape (agent.py): asserted decision + final decision +
  evidence_set + tool_calls + deployment:False + receipt_sha256.
- Demo shape: 3 scenarios (asserted / fetched / consequential).
- ENTRY.md structure => D1 article structure: starting agent +
  what it already did / the one new tool + why / AWS service /
  demo <3min.

## StudySprint extension (D1, not verbatim)
- Domain shift: Delphi Oracle judges consequential actions =>
  StudySprint judges study-plan readiness / practice-set trust
  (Education, social good) with Strands SDK.
- New artifact kinds needed: study source / practice set / syllabus
  file (fetch_evidence kinds are PR/file/run only today) = GAP.
- Strands SDK wiring: D0 agent loads oracle kernel by monorepo path
  (`parents[2]/scripts/delphi/...`) => not portable verbatim = GAP;
  D1 build must vendor/replace kernel + wire Strands.
- Article/demo: D0 ENTRY/demo-script are templates only; D1 article
  + <3min demo must be StudySprint-specific, published on Builder Center.

## Gaps summary
G1 kernel portability (path-bound load) | G2 new artifact kinds |
G3 Strands SDK implementation in agent.py (still stub in this repo) |
G4 workshop badge/cert (separate gate D1-WORKSHOP, in-flight) |
G5 D1 article + demo + submission (none yet)

## Honesty lines (carry from D0)
No AWS account / no live deployment / no Bedrock invocation claimed
in D0. D1 claims only what its receipts show.
