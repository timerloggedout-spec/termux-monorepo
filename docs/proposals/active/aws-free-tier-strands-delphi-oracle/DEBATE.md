# DEBATE — AWS Free Tier & Strands Decider Engineering Oracle

**Purpose:** independently rank proposal concepts and surface hard-stop risks. This is not a vote on AWS account creation, a deployment authorization, or evidence that any concept works.

## Decision under review

Which experiments should be implemented first in the isolated proposal silo, before any AWS account creation or resource provisioning?

Concept details and kill criteria: [EXPERIMENT-MATRIX.md](EXPERIMENT-MATRIX.md). Scope, gates, and acceptance criteria: [RFP.md](RFP.md).

## Round 0 — driver shortlist (not a ballot)

The driver proposes starting with:
1. E-05 Adversarial Evidence Firewall
2. E-01 Evidence-Gated Engineering Oracle
3. E-03 Counterfactual Replay

Rationale: safety and policy integrity first; then validate the core decision contract; then test evidence sensitivity. This ordering is provisional and must not be represented as consensus.

## Independent ballot protocol

Each eligible human reviewer should submit a separate ballot before group discussion:

- Rank at least three experiment IDs (1 = highest priority), or abstain.
- State one falsifiable reason for the top choice.
- Cite repository or external evidence, or explicitly state that the judgment is a hypothesis.
- Identify a disqualifying risk and the condition that would change the ranking.
- Disclose relevant conflicts or implementation ownership.
- Do not use an LLM-generated ranking as a human vote.
- Do not coordinate ballots before submission; the registrar should preserve timestamps and attribution as permitted.
- Nonresponse, emoji reactions, comments, author count, model agreement, and generated rubric scores are not votes.

## Aggregation

After the ballot window closes, the registrar records the eligible voter set, number invited, ballots received, abstentions, incomplete ballots and conflicts. Publish the aggregation method before calculating a result. Preserve dissent and uncertainty; do not erase minority objections into a single score.

A tie, missing evidence, or unresolved high-severity security concern returns to a new independent round. A ranking decides experiment order only. Account creation, paid use, deployment and promotion each require their own explicit gate.

## Oracle / model participation

Models may generate candidate hypotheses, counterarguments, test designs, and evidence summaries. These are advisory inputs only. They cannot cast votes, manufacture consensus, self-approve their outputs, or authorize actions.

## Term record

```text
term: aws-free-tier-strands-decider/experiment-order/round-1
status: OPEN_FOR_INDEPENDENT_HUMAN_BALLOTS
opened: 2026-10-23
deadline: set by human registrar
scope: experiment sequencing only
account_creation_authorized: false
aws_resources_authorized: false
paid_invocations_authorized: false
votes_received: 0
consensus: NONE
registrar: UNASSIGNED
```

## Ballots

_No ballots have been received or recorded yet._

## Open questions

1. Which three experiments maximize information gain per unit of engineering time before account creation?
2. Which failure modes must be hard-stop disqualifiers even if weighted scores are high?
3. What evidence is sufficient to proceed from local prototype to account creation?
4. Who will serve as human registrar and what is the ballot close time?
5. Is the hackathon submission still feasible under the official deadline and all eligibility requirements?

## Scope guardrails

- No AWS account or resource was created by opening this debate.
- No Free Tier entitlement, promotional credit, or zero-cost usage is assumed.
- No ballot or consensus is implied by the driver's recommendation.
- No experiment may send private repository/user data to external services without a separate data-flow review and explicit authorization.
- Any implementation result must distinguish COMMITTED, EXECUTED, VALIDATED and PROMOTED; queued or planned work is not success.
