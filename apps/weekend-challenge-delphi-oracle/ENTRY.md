# Give your Agent a Tool — entry (as it would have been submitted)

**Entrant:** `entrant{entrantAwsBuilderCenter}[platform:aws-builder-center]`
**Challenge:** AWS Builder Center Weekend Challenge — Give your Agent a Tool
**Status:** completed post-window by owner ruling (2026-10-27); not a submission.

## Starting agent

The **Delphi Oracle**: a deterministic evidence-gate oracle that judges a
proposed consequential action against an evidence set and returns
ALLOW_RECOMMENDATION / ABSTAIN / ESCALATE with a versioned receipt
(offline MVP, `scripts/delphi/strands_oracle_mvp.py`, public in this
repo). It fails closed: no material evidence → ABSTAIN; consequential
action classes (merge, deploy, credential mutation, …) → ESCALATE before
evidence is ever weighed.

Its limit: it could only judge evidence it was *handed* — and handed
evidence is usually just someone's claim about the world.

## The one new tool: `fetch_evidence`

Given a decision request naming an artifact — a pull request, a file, a
workflow run — the tool retrieves the artifact's current state
**read-only** and assembles a material evidence set in which every item
carries:

- **provenance** — source, exact API path, observation time;
- **freshness** — a `fresh_until` stamp (assembly + 15 min);
- **a content hash** — so the judged set is the set that was fetched.

The agent's loop: judge on asserted evidence (ABSTAIN — claims aren't
evidence) → call the tool → judge again on the fetched set. The agent
stops grading asserted evidence and starts grading fetched evidence.

## Why

The fleet's standing rule is *evidence over claims*. This tool is that
rule, made callable: any agent that must decide whether something is
true enough to act on can fetch the proof instead of trusting the
summary. It is also the exact seam between this entry and the fleet's
Decider-gated agents that reuse the pattern.

## AWS service

The tool is packaged as an **AWS Lambda** handler (`lambda_handler.py`)
behind a Strands agent — the Decider pattern, targeting Amazon Bedrock.
The completion record runs the identical handler locally against this
public repo: no AWS account exists (the owner's card rule closes
card-gated account creation), and this entry claims no live AWS
deployment and no Bedrock invocation.

## Demo (<3 min)

Scripted in `demo-script.md`, runnable as `demo.py`, real output
captured in `evidence/demo-run.json`:

1. A merge-readiness question with asserted evidence only → **ABSTAIN**.
2. The same question naming PR #1620 → the tool fetches its real state
   and check runs → **ALLOW_RECOMMENDATION** with receipt.
3. A credential-mutation request with fetched, material evidence →
   **ESCALATE** anyway: the class rule runs before evidence is weighed.
