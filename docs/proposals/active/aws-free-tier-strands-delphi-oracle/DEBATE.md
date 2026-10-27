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

## Telemetry-acquired Delphi evidence (authoritative collection path)

The Delphi process is **telemetry-led**, not dependent on manually soliciting every ballot in chat. The collection plane should acquire results from registered collaborators and 3L0 Delphi Oracle provider/model analogs, normalize them into a common result envelope, and preserve the source identity class and provenance.

### Source classes (never collapse these labels)

- `HUMAN_COLLABORATOR`: a distinct human reviewer with a verifiable GitHub identity and recorded ballot.
- `MODEL_PROVIDER`: an independent provider/model execution with provider, model/version, run ID, prompt/fixture version, and response hash recorded.
- `LOCAL_BASELINE`: deterministic non-model comparator.
- `AUTOMATION_GATE`: CI, schema, policy, test, and evidence checks.
- `DRIVER_SYNTHESIS`: authored synthesis, not a ballot.

Model/provider analogs are valuable independent experimental observations, but they are **not human votes** and cannot satisfy a human-quorum requirement. Multiple runs from one provider/model family are repeated measures, not automatically independent voters. Correlated models, shared upstream models, copied prompts, and shared toolchains must be marked as dependency clusters before aggregation.

### Telemetry acquisition and result contract

The collector should ingest only completed, attributable results; deduplicate by `term_id + source_id + run_id`; retain raw evidence only where policy permits; and publish a sanitized immutable receipt. Missing, skipped, timed-out, invalid, rate-limited, and failed results remain explicit states and must never be counted as negative votes or silently dropped.

Minimum normalized envelope:

```json
{
  "schema_version": "delphi-result/v1",
  "term_id": "aws-free-tier-strands-decider/experiment-order/round-1",
  "source_class": "MODEL_PROVIDER",
  "source_id": "provider/model-version",
  "run_id": "stable-run-id",
  "fixture_set_hash": "sha256:...",
  "proposal_commit": "git-sha",
  "result_state": "COMPLETED",
  "ranked_experiments": ["E-05", "E-01", "E-03"],
  "hypothesis": "falsifiable statement",
  "evidence_refs": [],
  "confidence": null,
  "limitations": [],
  "dependency_cluster": "provider-family-or-unknown",
  "started_at": "ISO-8601",
  "completed_at": "ISO-8601",
  "response_hash": "sha256:...",
  "redaction_status": "PASS"
}
```

The example is a schema illustration, not a real result. No provider outputs, human ballots, confidence values, or consensus have been fabricated.

### Collection workflow

1. Freeze the term, fixture set, rubric, candidate list, and aggregation rule.
2. Dispatch equivalent independent tasks to the registered provider/model panel and eligible human collaborators; blind candidates where practical.
3. Collect callbacks/artifacts through the existing telemetry/provider-batch integrations when they support the contract; do not create a parallel workflow until the existing path has been inspected and verified.
4. Validate schema, attribution, run state, fixture hash, source/dependency cluster, redaction, and duplicate key.
5. Store raw responses under access/retention policy; publish sanitized receipts and per-source results.
6. Aggregate human ballots separately from model/provider observations and deterministic/CI gates.
7. Publish disagreement, missingness, uncertainty, and dissent alongside any aggregate ranking.
8. Trigger the next round only from a validated collection state; never treat a merge, green workflow, queued dispatch, or provider acknowledgement as an experiment result.

### Independence and anonymity

Use stable pseudonymous voter/source IDs in the public report, with a restricted mapping for authorized auditors where needed. Anonymity is not a license to erase provenance: the system must still detect duplicate ballots, repeated model identities, dependency clusters, and conflicts. Human identities are not to be exposed publicly by default; provider/model identity and model version should remain visible unless a documented safety reason requires limited disclosure.

### State accounting

Track these independently:

```text
INVITED -> DISPATCHED -> RECEIVED -> VALIDATED -> INCLUDED_IN_ANALYSIS
                     \-> TIMEOUT / FAILED / INVALID / DUPLICATE / REDACTED
```

Only `VALIDATED` records are eligible for analysis. `INCLUDED_IN_ANALYSIS` means the result contributed to a named analysis, not that it was a vote. Human ballots, model outputs, baseline measurements, and CI gates have separate denominators.

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
