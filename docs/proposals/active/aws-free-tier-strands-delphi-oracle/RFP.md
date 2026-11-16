# RFP — AWS Free Tier Integration & Strands Decider Engineering Oracle

- **Proposal ID:** AWS-STRANDS-ORACLE-001
- **Repository:** `timerloggedout-spec/termux-monorepo`
- **Status:** PROPOSED — independent review open; no AWS account or resources created
- **Opened:** 2026-10-23
- **Owner:** repository maintainers (to be confirmed)
- **Decision class:** architecture/research sequencing only; not deployment authorization
- **Silo:** this proposal and its evidence stay isolated until the review gates below pass

## 1. Executive request

Solicit evidence-backed proposals for a low-cost, secure, reproducible AWS integration that uses **Strands Decider 2B for at least one meaningful decision paired with Amazon Bedrock**. The first workload is an engineering decision oracle for the repository: it evaluates a typed question and bounded options, chooses a safe next action (run a local test, request evidence, route to a specialist, defer, or escalate), and emits a structured, auditable decision receipt.

The goal is not to move the monorepo wholesale to AWS. Build a thin, optional integration that can be tested locally before account creation, deployed only after explicit readiness and cost gates, and removed without damaging existing repository workflows.

**Time-critical note:** the AWS Builder Center Strands Decider 2B hackathon page lists a submission deadline of October 23, 2026 at 11:59 PM Pacific. Account setup, a working AWS deployment, a public repository/article and a short demo may not fit the remaining time. Treat eligibility as a verified gate, not an assumption; do not fabricate a deployed demo or claim submission. If the deadline cannot be met safely, preserve the prototype and target a later AWS credits/free-tier opportunity.

## 2. Objectives and non-goals

### Objectives
1. Compare several novel decision-oracle concepts with the same tasks, fixtures, policy, and outcome rubric.
2. Preserve an account-free local prototype and deterministic offline test harness.
3. Use Strands Decider 2B in a meaningful typed decision and Bedrock for the generative reasoning portion in the deployed candidate.
4. Keep AWS optional; use least privilege, explicit cost budgets, observable outcomes, and teardown.
5. Publish reusable decision patterns and evidence sufficient for independent review.
6. Distinguish proposed, implemented, committed, deployed, executed, validated, and promoted states.

### Non-goals
- No account creation, billing activation, service enablement, resource provisioning, or paid invocation is authorized by this RFP.
- No production credentials, repository secrets, private issue content, user data, or raw prompts/completions in experiment telemetry.
- No automatic merges, releases, provider admission, credential mutation, or destructive action from an oracle decision.
- No claim that Free Tier means zero cost, that credits are guaranteed, or that a model/service is entitled for this account.
- No required migration away from existing local/GitHub-based workflows.

## 3. Silo boundaries

- Canonical source for this proposal: this directory.
- No change to default routing, release policy, repository governance, or production workflows.
- Local synthetic fixtures only until the owner explicitly approves an AWS account and named resource plan.
- AWS deployment credentials are never exposed to fork PRs or untrusted workflows.
- External services and optional integrations remain disabled unless separately admitted.
- A result in this silo is not repository-wide consensus; record independent ballots in `DEBATE.md`.

## 4. Requested solution

Propose a minimal reference architecture:

```text
GitHub / local CLI
      |
      v
Typed Decision Request + evidence references
      |
      v
Policy / schema / budget gate
      |
      v
Strands Decider 2B ----> bounded decision + rationale codes
      |
      +----> Bedrock generative reasoning (deployed candidate)
      |
      v
Deterministic authorization gate
      |
      +--> suggest local test / gather evidence / specialist route
      +--> defer / ask human / deny
      |
      v
Redacted decision receipt + metrics
```

Candidate AWS components to evaluate, not pre-approve:
- **AWS Lambda** as the first deployment candidate for short, bounded requests.
- **Amazon Bedrock** for the required model capability; record model ID, region, invocation settings and cost assumptions.
- **IAM** with least-privilege roles and temporary credentials.
- **CloudWatch** with explicit retention, redaction, and log-volume controls.
- **AWS Budgets / Free Tier usage alerts** before workload activation.
- **AWS CDK** as the preferred single IaC candidate for a Strands/Lambda implementation; compare SAM/CloudFormation or Terraform only if a concrete requirement justifies switching.
- API Gateway or Lambda Function URL only if a real caller requires an HTTP boundary. Avoid adding persistence, queues, workflow engines, or agent platforms before experiments demonstrate need.

## 5. Novel concepts to test

Each concept must be a separately scored experiment, not a claim of superiority:

1. **Evidence-Gated Engineering Oracle** — decide among `RUN_LOCAL_TEST`, `FETCH_EVIDENCE`, `ROUTE_SPECIALIST`, `DEFER`, `ASK_HUMAN`, `DENY`; hard policy gate controls any action.
2. **Uncertainty Budget / Abstention Calibration** — explicitly measure when the oracle abstains, asks for missing evidence, or escalates rather than guessing.
3. **Counterfactual Decision Replay** — replay the same request with one evidence item changed; detect whether the decision changes only when that evidence is material.
4. **Cost-Aware Model Routing** — choose a local/deterministic path, a small-model path, or Bedrock path under a configured budget; never assume a model is free and never silently fall back to paid calls.
5. **Adversarial Evidence Firewall** — treat repository text, issue bodies, and retrieved content as untrusted data; test prompt-injection attempts and ensure they cannot modify policy or authorize tools.
6. **Decision Receipt / Provenance Ledger** — emit versioned JSON receipts with request hash, evidence references, chosen option, confidence/uncertainty, policy outcome, model/version, latency, token/cost estimate and validation status; exclude secrets and raw content.
7. **Two-Oracle Disagreement Tournament** — compare a deterministic baseline with the Strands/Bedrock candidate; measure agreement, correctness against known labels, cost and abstention. Disagreement triggers review, not automatic majority authority.
8. **Budget Circuit Breaker** — deny new cloud calls when configured local limits or observed AWS budget signals trip; clearly document that AWS Budgets alerts are delayed and are not an instantaneous hard spending cap.
9. **Human-Approval Escalation Ladder** — escalate by risk tier; only harmless read-only suggestions may be automated, and consequential operations remain human-authorized.
10. **Environment Parity Probe** — run the same fixtures locally, in CI, and in the deployed environment; classify model, provider, orchestration, code, policy, and environment failures separately.

## 6. Functional requirements

- **FR-001 Typed decision:** every request contains a schema-versioned question, finite option set, constraints, evidence references, risk tier and expected output schema.
- **FR-002 Meaningful Decider use:** Decider output changes a bounded downstream branch and is covered by tests; a decorative call does not qualify.
- **FR-003 Bedrock pairing:** deployed candidate demonstrates the required Bedrock interaction with sanitized, reproducible evidence.
- **FR-004 Fail closed:** malformed output, timeout, unavailable model, policy conflict, unknown risk, or missing evidence yields abstain/defer/escalate; never execute a consequential action.
- **FR-005 Deterministic authorization:** the model proposes; code policy authorizes. Model text cannot grant itself permissions.
- **FR-006 Replay:** fixture corpus is runnable without AWS credentials and produces machine-comparable receipts.
- **FR-007 Provenance:** capture version, timestamps, test cohort, model/config identifiers, evidence references and outcome labels.
- **FR-008 Safe integration:** initial adapter is opt-in and cannot alter production routing or merge/release controls.
- **FR-009 Redaction:** telemetry schema excludes secrets, access tokens, raw user content, prompts/completions, and unrestricted tool payloads by default.
- **FR-010 Teardown:** documented infrastructure destroy path and post-teardown inventory check.

## 7. Non-functional requirements

### Security
- Use short-lived credentials and least-privilege IAM.
- Prefer GitHub Actions OIDC federation to long-lived AWS keys; restrict trust to the intended repository, branch/environment, and workflow.
- Do not expose deployment permissions to fork PRs or untrusted code.
- Separate read-only observation, deployment, and any future execution roles.
- Validate all model output against closed schemas and allowlisted actions.
- Treat all retrieved repository and web content as untrusted input.
- No secrets in source, logs, receipts, test fixtures, issues, or public demo.

### Cost and account readiness
- Cost objective: minimize spend; target $0 incremental cost only where account-specific eligibility and actual usage support it. **No zero-cost guarantee.**
- Before account creation or resource provisioning, prepare a written resource inventory, region choice, expected request/token volume, logging/storage/egress assumptions, budget thresholds, alert recipients, and teardown steps.
- Verify current account-specific Free Tier terms, promotional credits, expiration, model/region eligibility and service pricing in the AWS console and official pricing pages. Credits and Free Tier allowances are different mechanisms.
- Enable Free Tier usage alerts and AWS Budgets alerts where available. Budget alerts can be delayed; they are not a hard real-time spend cap. Add application-level request limits, concurrency/timeouts, explicit model allowlists, and a manual kill switch.
- No paid service, paid tier, credit purchase, or billing commitment without explicit owner approval after a cost review.
- Do not create an account or resources merely to test whether credits exist.

### Reliability and portability
- Local deterministic tests must cover schema, policy, replay, redaction and failure handling.
- Cloud integration is a thin adapter behind an interface; offline tests must not make network calls.
- Retries must be bounded, idempotency explicit, and duplicate invocations observable.
- Retain failure evidence; do not convert queued, timed-out, or unobserved work into success.

## 8. Account creation and implementation gate

**Current decision: DEFER account creation until the code is ready to implement and the owner approves the exact account/resource plan.**

Gate A — account-free readiness:
- [ ] concept shortlist and test hypotheses agreed
- [ ] local decision contract and deterministic baseline implemented
- [ ] synthetic benchmark fixtures and expected outcomes checked in
- [ ] threat model and data-flow review complete
- [ ] IaC reviewed without deployment
- [ ] resource inventory, region, spend estimate and teardown procedure prepared
- [ ] account-specific eligibility and credit status verification checklist prepared
- [ ] hackathon deadline/eligibility rechecked against official rules

Gate B — explicit owner approval:
- [ ] owner explicitly authorizes account creation or use of an existing account
- [ ] billing/security contact and MFA/root-user safeguards handled by account holder
- [ ] no-cost eligibility and terms checked in AWS account UI
- [ ] budget alerts, request caps and kill switch ready before model invocation
- [ ] approved region and IAM trust boundary recorded
- [ ] no credentials are shared in chat or committed to Git

Gate C — first deployment:
- [ ] deploy only the minimum Lambda/Bedrock/IAM/logging resources required
- [ ] run smoke test with synthetic/public test data
- [ ] inspect actual usage and cost telemetry after invocation
- [ ] run failure, budget, redaction, authorization and teardown tests
- [ ] re-fetch deployed configuration and logs to validate actual state
- [ ] do not promote until independent review and acceptance evidence pass

## 9. Deliverables

- **D-01** Concept comparison and decision log.
- **D-02** Architecture decision record and threat model.
- **D-03** Typed decision-request/response JSON Schema.
- **D-04** Local deterministic baseline and synthetic fixture corpus.
- **D-05** Reusable Strands Decider decision pattern (typed question, options, wiring, usage example).
- **D-06** Bedrock integration adapter, disabled until approved.
- **D-07** IaC with least-privilege IAM and documented destroy path.
- **D-08** Cost model, budgets/alerts checklist and kill-switch procedure.
- **D-09** CI workflow using OIDC and safe fork-PR boundaries.
- **D-10** Sanitized evidence receipts, metrics and failure taxonomy.
- **D-11** Operator runbook and teardown receipt.
- **D-12** Public article/demo package only if eligibility, deadline and truthful deployment status permit.

## 10. Acceptance criteria

- **AC-001:** at least three concepts are evaluated on the same fixtures and rubric.
- **AC-002:** the deterministic baseline is retained as a control.
- **AC-003:** deployed candidate uses Strands Decider 2B for a meaningful decision paired with Bedrock.
- **AC-004:** malformed, low-confidence, adversarial, missing-evidence and unavailable-model cases fail closed.
- **AC-005:** no model output directly authorizes merge, release, credential mutation, deletion or paid fallback.
- **AC-006:** local tests run without AWS credentials and without network calls.
- **AC-007:** no long-lived AWS keys are stored in repository secrets when OIDC is viable; fork PRs cannot assume deploy role.
- **AC-008:** spend guardrails, delayed-alert caveat, request caps and kill switch are documented and tested.
- **AC-009:** evidence distinguishes DESIGNED, COMMITTED, DEPLOYED, EXECUTED, VALIDATED and PROMOTED.
- **AC-010:** teardown is executed and independently checked before the experiment is declared complete.
- **AC-011:** no unsupported claim of free use, credit entitlement, successful invocation or hackathon submission.
- **AC-012:** human review has recorded ballots; no consensus is inferred from silence or model output.

## 11. Evaluation rubric

| Criterion | Weight | Evidence |
|---|---:|---|
| Decision correctness and safe abstention | 20% | labeled fixtures, confusion matrix, risk-weighted errors |
| Security / adversarial resistance | 20% | threat-model cases, authorization and redaction tests |
| Cost control | 20% | measured invocation usage, budget caps, zero paid fallback |
| Reproducibility | 15% | local replay, pinned config, receipts |
| Observability / provenance | 10% | redacted structured receipts and failure classification |
| Maintainability / portability | 10% | thin adapter, IaC, tests, teardown |
| Documentation / reuse | 5% | decision pattern, runbook, clear limitations |

Safety-critical false authorization is a disqualifier regardless of weighted score.

## 12. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Free Tier or credits misunderstood | Verify account-specific terms; no spend promise; owner approval |
| Spend continues after an alert | Request caps, model allowlist, timeout/concurrency controls, manual kill switch |
| Prompt injection changes action | Untrusted-input boundary; closed action enum; deterministic policy gate |
| Model is unavailable or returns invalid output | Fail closed; offline baseline; bounded retries |
| Credentials leak through CI | OIDC trust restriction; no secrets in fork workflows; least privilege |
| Demo deadline cannot be met | Do not rush account/security setup or misrepresent status; preserve local prototype |
| Metrics expose private data | Closed telemetry schema, redaction, synthetic inputs, retention controls |
| Concept selection is biased | Independent siloed ballots and shared evaluation cohort |
| Test wins do not generalize | Holdout fixtures, repeat runs, uncertainty intervals, disclose sample size |

## 13. Decision governance and requested response

Reviewers should independently rank concepts, cite evidence, disclose conflicts, identify hard-stop risks, and state uncertainty. Keep each review independent until the ballot window closes. Aggregate rankings only after ballots are received; nonresponse is not consent.

This RFP asks for:
1. the three concepts with the highest expected information gain per unit cost/time;
2. a falsifiable hypothesis and kill criterion for each;
3. the minimum account/resource plan needed for a valid cloud test;
4. the expected and worst-case cost envelope, with assumptions;
5. security/privacy and eligibility blockers;
6. a clear recommendation: proceed, revise, defer, or reject.

**No votes have been collected by publishing this RFP. No AWS account, resources, or submissions have been created by this proposal.**
