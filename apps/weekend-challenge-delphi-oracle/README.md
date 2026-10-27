# Weekend Challenge D0 — Delphi Oracle + fetch_evidence

Completion package for AWS Builder Center **Weekend Challenge: Give your
Agent a Tool** (entered 2026-10-23 as registration R2; window closed
2026-10-26 1:00 PM PT with no submission). Owner ruling 2026-10-27: the
entry is completed anyway, because the fleet entered it. This package is
the finished entry and its completion record — a post-window completion
is **not** a submission, and nothing here claims one.

## What's in the package

| File | Role |
|---|---|
| `agent.py` | The entry agent: the Delphi Oracle as starting agent + the tool loop, emitting a receipt per decision |
| `fetch_evidence.py` | **The one new tool** — read-only artifact retrieval → provenance/freshness-stamped evidence sets |
| `lambda_handler.py` | AWS Lambda packaging (the Strands Decider pattern's deployable unit); runs locally unchanged |
| `demo.py` | Scripted 3-scenario walkthrough (<3 min); writes `evidence/demo-run.json` |
| `demo-script.md` | Narration script for the <3-minute demo video |
| `ENTRY.md` | The entry text as it would have been submitted |
| `evidence/demo-run.json` | Captured real run output (the completion record's evidence) |

The starting agent is the Delphi Oracle offline MVP
(`scripts/delphi/strands_oracle_mvp.py`, PR #1620 → `81a0d77be3ae`): a
deterministic evidence-gate oracle that judges a proposed action against
an evidence set and returns ALLOW_RECOMMENDATION / ABSTAIN / ESCALATE
with a versioned receipt. Its limit is the challenge's opening: it could
only judge evidence it was handed. `fetch_evidence` removes that limit —
the agent stops grading asserted evidence and starts grading fetched
evidence.

## Run it

```bash
python3 demo.py            # live, read-only, against this public repo
python3 -m pytest ../../tests/test_weekend_challenge_delphi_oracle.py
```

No credentials are needed (public repo reads); `GITHUB_TOKEN` is honored
if present, for rate limits only.

## Honesty lines

- No AWS account exists (owner card rule, 2026-10-26). The Lambda
  handler is packaged and run **locally**; the package claims no live
  AWS deployment and no Bedrock invocation.
- The oracle baseline is the deterministic MVP kernel — no model or
  provider ballots are represented anywhere in the receipts.
- The demo's evidence is real: PR #1620's actual state and check runs,
  fetched at run time and stamped in `evidence/demo-run.json`.
