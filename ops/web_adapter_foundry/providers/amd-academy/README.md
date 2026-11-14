# AMD AI Academy — Web Adapter Foundry provider

**Registry:** `registry.json`  
**Provider ID:** `amd-academy-netexam`  
**State:** discovery-only; no operation is promoted or executable.

## Established facts

- AMD's public AI Academy onboarding flow is sign-up, email verification, join the AI Developer Program, then access the Academy: https://developer.amd.com/amd-ai-academy/
- The public learner portal at `academy.amd.com` identifies as NetExam.
- NetExam vendor documentation describes a Learner API and Integration API in general: https://netexam.com/channel-partner-training-tour/api-custom-integration-sso/
- AMD's Developer Community has documented learner-lab progress tracking incidents and later restoration notices: https://devcommunity.amd.com/t/jupyter-notebook-does-not-record-my-progress/971

## Explicitly not established

- Whether AMD's specific NetExam tenant exposes learner API credentials or grants learner-level API access.
- Any AMD-tenant OpenAPI specification, endpoint URL, auth scope, or rate limit.
- A supported MCP server for this tenant.
- Any verified direct HTTP, Web2API, CLI, or browser automation operation.

Do not guess endpoints, use admin/integration APIs without tenant authorization, bypass MFA/CAPTCHA/anti-bot controls, or scrape credentials from browser storage. The registry therefore contains operation IDs only; every operation remains `discovered` with `evidence_label=unknown`.

## Operation inventory

Read candidates:
- `amd_academy.courses.list`
- `amd_academy.course.progress`
- `amd_academy.points.snapshot`
- `amd_academy.certificate.get`

State-changing candidates:
- `amd_academy.course.enroll`
- `amd_academy.module.launch`
- `amd_academy.lab.launch`
- `amd_academy.lab.submit`
- `amd_academy.quiz.submit`

These are normalized operation names, **not observed NetExam endpoints**.

## Safety and completion semantics

- Account isolation is mandatory; credentials are vault references only.
- Read LMS state before resuming. Never automatically retry a write after an ambiguous result.
- Notebook execution and LMS-recorded lab completion are separate states. A notebook that ran is not proof that the LMS recorded the module complete.
- Read back course/module progress after lab actions; tracker timeouts remain `OUTCOME_UNKNOWN` until reconciled.
- Each course completion requires the certificate plus the actual course-bound points-balance screenshot. Transcript text is supporting evidence only.
- A course outcome, compliant execution, evidence capture, gate submission, and gate acceptance are separate states.
- QUE attribution requires the execution provenance contract; external-computer/seat-browser execution is never QUE-native execution.

## Promotion gate

An operation may move beyond `discovered` only after its exact route is established from official tenant documentation or authorized observation, its input/output contract is recorded, credentials and session boundaries are reviewed, read/write semantics and idempotency are tested, and an independent verifier reproduces the operation. This registry is not a live adapter and is not a QUE course-completion demonstration.


## Promotion evidence checklist

Before promoting any operation beyond discovery-only, attach all of the following to its operation record:

1. Official AMD-tenant documentation or an authorized, reproducible observation proving the exact route and tenant entitlement.
2. A bounded input/output contract with account and session boundaries; secrets remain vault-only.
3. A read/write classification, explicit idempotency key, and read-after-action reconciliation behavior.
4. Tests for expiry, unhandled MFA/CAPTCHA, ambiguous write outcomes, cross-account isolation, and secret redaction.
5. An independent reproduction receipt tied to the adapter version.

A vendor-wide NetExam API description does not satisfy item 1. A successful notebook run does not satisfy LMS completion until the Academy progress record is read back. The current registry intentionally remains discovery-only until these conditions are met.


## Assessment integrity boundary

AMD's current ROCm Certified Developer Program Agreement (v1.1, effective July 2026) prohibits unauthorized assistance, unauthorized collaboration, unauthorized materials/devices, and generative-AI tools or services during Evaluations unless AMD expressly permits them. It also treats evaluation questions, tasks, item banks, scoring rubrics, and keys as confidential Program Assets.

Accordingly, the adapter MUST stop at any quiz, exam, scored assessment, proctored step, or other Evaluation unless the applicable AMD rule explicitly authorizes the proposed assistance. Do not read, capture, persist, summarize, answer, submit, or replay evaluation content. A human may continue independently under AMD's rules. Course modules and labs may be supported only outside protected evaluation steps and within the applicable course terms.
