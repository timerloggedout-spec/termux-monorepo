# Issue Intake Admission Firewall

## Purpose

The issue-open event path must not spend provider quota before a cheap, deterministic admission decision. This firewall controls **advisory provider triage only**. It does not reject public issue filing, apply labels, assign work, close issues, ban actors, or prove malicious intent.

## Event path

`issues.opened/reopened → issue-intake-dispatch.yml → deterministic admission → (trusted + normal-volume) gemini-triage.yml`

The existing `issue-lifecycle-triage.yml` remains the independent provider-free label floor. The new workflow replaces the issue-open trigger previously owned by `gemini-dispatch.yml`; on-demand Gemini commands and PR review routing remain there.

## Admission policy v1

The classifier admits advisory triage only when all conditions hold:

- action is opened or reopened;
- sender is a GitHub User and is the issue author;
- issue author association is OWNER, MEMBER, or COLLABORATOR;
- title/body are within conservative size bounds;
- the GitHub API reports no more than three issues by that author in the preceding ten minutes.

All other cases receive `deterministic_only`. A failed or unknown volume lookup fails closed for provider fan-out. This is deliberately conservative: an authorized maintainer reopening someone else's issue does not pass v1 actor/author matching. Revisit only with an authoritative actor-permission check.

## Safety and limitations

- Public filing is never blocked by this workflow.
- Burst volume is a rate-control signal, not a spam verdict.
- The workflow does not quarantine, ban, auto-close, or invoke privileged implementation routes.
- GitHub API pagination is bounded to 100 recent issues. The count is a coarse signal, not a comprehensive abuse detector.
- Workflow concurrency is per issue; it is not a repository-wide queue or hard DDoS shield. GitHub platform admission/rate limits still apply.
- The issue lifecycle deterministic workflow continues independently.
- The issue body is untrusted data. It cannot alter workflow permissions or dispatch policy.
- Provider quota/balance is not inferred from public tier limits. The reusable Gemini triage's model-router remains responsible for current route eligibility.

## Actions quota accounting

Each opened/reopened issue starts exactly one bounded admission job before any provider fan-out. The job has a **3-minute timeout**, performs one GitHub REST list request for the author's recent issue volume (plus the GitHub-hosted action/checkout overhead), and invokes no model. The reusable provider triage job runs only after a positive admission decision. Public-repository standard GitHub-hosted runner minutes are recorded as free in `ops/quota/registry.json`; this workflow still consumes Actions execution capacity and creates a run per event, so operators should track run count and elapsed runner minutes during rollout. No per-workflow live minute attribution is available from the current quota reader; do not invent a numeric allowance or treat the free entitlement as unlimited concurrency.

## Validation

Run:

```sh
node --test tests/issue_lifecycle/intake_admission.test.js
```

The tests cover trusted admission, public/untrusted authors, bots, actor/author mismatch, burst threshold, oversized payload, malformed events, unknown volume evidence, and unsupported actions.

## Follow-up

#4010 owns production hardening and end-to-end abuse controls. #4015 owns the parallel DoE comparison of control/treatments, fleet topologies, quota-aware selection, and critique/validation escalation. Do not promote a more permissive policy without replay evidence, exact-head CI, and owner review.
