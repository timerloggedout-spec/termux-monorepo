# RFP — AWS Emulator adoption and agent-built fidelity engineering loop

- **Proposal ID:** aws-emulator-agent-fidelity
- **Repository:** `timerloggedout-spec/termux-monorepo`
- **Status:** POSTED — architecture and offline contract foundation committed; runtime pilot not executed
- **Opened:** 2026-11-16
- **Priority:** P1
- **Decision class:** research, architecture, and bounded development; no cloud provisioning authorization
- **Related proposal:** [AWS Free Tier integration and Strands Decider Delphi Oracle](../aws-free-tier-strands-delphi-oracle/RFP.md)

## 1. Executive request

Use AWS Emulator as a reference and optional local test target to strengthen the monorepo's agentic engineering loop. The core lesson is not “run thousands of agents” or “rewrite the repository in Rust.” It is to give agents a precise specification, executable reference tests, bounded ownership, a reproducible environment, and independent merge gates that can reject incorrect work.

AWS's published approach separates work into three bounded teams:

1. **Test authors** derive scenarios from public API models and validate expected behavior against a reference implementation.
2. **Gap finders** replay those tests against the emulator, cluster failures by likely root cause, and file issues.
3. **Fixers** own one bounded issue, implement the correction, and submit it to an independent quality/security/fidelity gate.

Adapt these roles to the repository's existing QUE/QDesk, Brain, CI, SHE, and evidence architecture. Do not build a parallel task queue, manager, contributor roster, telemetry store, or promotion system.

## 2. What transfers — and what does not

### Transfer

- Specification-first development: machine-readable contracts are the source of truth.
- Reference-oracle tests: establish expected behavior before implementation.
- Replayable fidelity suites: deterministic tests can run repeatedly without a live cloud dependency once expected behavior is safely captured.
- Failure clustering: group correlated test failures by root cause before dispatching work.
- Single-issue ownership: one implementation claim per bounded issue/revision.
- Independent gates: compile/test, correctness, security, regression, and provenance checks are separate evidence.
- Public gap ledger: distinguish known unsupported behavior from fixed behavior.
- Continuous refresh: compare model/API changes to coverage and file new gaps rather than silently claiming completeness.

### Do not transfer literally

- Do not claim thousands of agents or a fully autonomous system based on a local proof of concept.
- Do not add AWS CodeCommit, CodePipeline, Bedrock AgentCore, Kiro, or a new agent runtime as mandatory dependencies.
- Do not copy the AWS emulator implementation or its service code into this repository.
- Do not treat emulator pass as production readiness or security certification.
- Do not run a full AWS Emulator source build on a constrained Android/Termux device. Upstream documents a large cold-build disk requirement and Linux/macOS/Windows paths, not Android/Termux support.
- Do not use LocalStack or AWS Emulator as an authority for real-cloud throttling, outages, regional availability, or all IAM/security semantics.
- Do not invoke real AWS APIs, provision resources, or incur costs without a separate owner-approved experiment.

## 3. Priority ordering

| Priority | Workstream | Rationale | Exit evidence |
|---|---|---|---|
| **P0** | Contract and evidence integrity | Without versioned contracts, source provenance, and immutable expected results, autonomous work can optimize the wrong target | Strict contract validator, fixture provenance, exact-SHA receipts |
| **P0** | Independent quality/security merge gate | Agent-written code requires a gate independent of the fixer; failures must block promotion | Compile, unit, regression, security, and policy checks; no self-approval |
| **P0** | Bounded issue ownership and failure clustering | Parallelism only helps when tasks are separable and write ownership is clear | One active writer per issue/revision; duplicate/root-cause clustering |
| **P1** | Optional AWS Emulator host adapter | Enables fast local/CI AWS SDK integration tests without mandatory cloud provisioning | Pinned supported-host smoke and service-by-service evidence |
| **P1** | AWS API model and SDK contract inventory | Provides a machine-readable coverage map; upstream Smithy model repository is generated and not a normal PR target | Model version/hash, operation inventory, service ownership |
| **P1** | Fidelity cohort and gap ledger | Distinguishes supported, verified, unverified, unsupported, and regressed behavior | Deterministic fixtures + structured coverage and gap records |
| **P1** | LocalStack comparison | Avoids assuming one emulator is best; licensing, distribution, and fidelity differ | Paired cohort, current license/distribution check, total cost |
| **P1** | Termux/Android compatibility assessment | Prevents unsupported binary/build assumptions and resource exhaustion | Actual device probe; no claim from Linux CI |
| **P2** | Multi-agent scaling and manager tournament | Scale only after quality, ownership, and instrumentation are proven | Paired experiments with outcome, conflict, retry, latency, cost, and human-effort evidence |
| **P2** | Automated model-drift discovery | Valuable once the initial service cohort and gap schema are stable | New-model diff produces reviewable candidate issues without auto-promoting |
| **P2** | Cloud-backed oracle / Bedrock integration | Existing AWS Strands proposal owns this; keep separate from local fidelity work | Separate account, budget, IAM, and owner authorization |

P0 describes prerequisites already partly present in the monorepo; the immediate work is to verify and reuse them, not create duplicates. The first implementation in this branch adds a fail-closed contract and validator; it does not activate an emulator.

## 4. Target architecture

```text
AWS Smithy/API models + repository contracts
                  |
                  v
        TEST AUTHORING / FIXTURES
                  |
         reference behavior oracle
                  |
                  v
        VERSIONED FIDELITY CORPUS
                  |
                  v
       GAP FINDER / REPLAY RUNNER
                  |
       classify + deduplicate failures
                  |
                  v
         QUE/QDesk bounded issue
                  |
                  v
          FIXER / isolated worktree
                  |
                  v
       independent quality + security
                  |
                  v
         regression / fidelity replay
                  |
                  v
        existing PR / promotion gates
                  |
                  v
     SHE + JSONL + ATES + 3L0 evidence
                  |
                  v
          manager-policy learning
```

The Mermaid source of record is `AWS-EMULATOR-AGENT-FIDELITY.mmd`. It is designed for the repository's existing `.mmd → .png` documentation automation.

## 5. Initial service cohort

Do not begin with “all AWS services.” Select a small cohort from actual repository dependencies and test value. Candidate order:

1. **SQS** — queue lifecycle and message send/receive/delete; useful first end-to-end control-plane workflow.
2. **S3** — object and bucket lifecycle; broad SDK usage and useful stateful behavior.
3. **DynamoDB** — table/item operations and conditional behavior.
4. **STS/IAM-adjacent identity** — only synthetic credentials and non-authoritative local identity tests; never infer security correctness from emulation.
5. **Lambda / API Gateway** — defer until the first three are stable; code execution and multi-service behavior increase risk.

The actual selected cohort must be reconciled with the repo's existing AWS schemas and application dependencies before implementation. No service is considered supported merely because its model or endpoint exists.

## 6. Fidelity contract

Each test case must carry:

- immutable test ID and version;
- service and operation identifiers;
- SDK/CLI version;
- model source and version/hash where applicable;
- setup, action, expected state, expected error code, and cleanup;
- evidence class: model-derived, real-cloud-observed, emulator-observed, synthetic, or inferred;
- source environment and timestamp;
- supported/verified/unverified/unsupported classification;
- redaction and secret-safety result.

A passing emulator test proves only that the tested behavior matched the fixture under the recorded emulator version. It does not prove all AWS behavior, production security, regional parity, resilience, or service availability.

## 7. Runtime and security boundaries

- Integration defaults to disabled and local-only.
- Default endpoint is loopback; remote endpoints are rejected by the first contract validator.
- No ambient AWS credentials are permitted in emulator test processes. Use synthetic emulator credentials only.
- No automatic cloud fallback: unsupported emulator operations fail visibly; they must not silently call AWS.
- Emulator tests are not security tests. Do not use production credentials or production data.
- Test code may execute locally and is not assumed sandboxed by the emulator. Run untrusted code only in an isolated, disposable host environment.
- Keep runtime binaries, caches, logs, test exports, certificates, and state outside tracked worktrees.
- Use a pinned emulator release and evaluation-suite revision before any repeatable run; floating `latest` is not evidence.
- Every test resource must have deterministic unique naming and cleanup.
- Real-cloud parity tests require a separate approval, isolated sandbox account, explicit budget, least-privilege IAM, and teardown evidence.
- No production deployment, credential access, or routing changes are in scope.

## 8. LocalStack comparison

LocalStack remains a legitimate comparison candidate, not an assumed loser. Its published distribution changes describe a unified account-based experience and free-plan restrictions; verify current terms before adoption. Compare both tools using the same test cohort and report:

- service and operation coverage;
- behavioral fidelity and known gaps;
- test startup/runtime latency;
- CPU, memory, and disk footprint;
- CI suitability and license/terms;
- authentication and telemetry requirements;
- maintenance/update cadence;
- developer ergonomics and Termux host compatibility.

The AWS Emulator's CC0 dedication applies to its own repository subject to its stated third-party vendor exceptions; do not assume the evaluation suite, SDKs, or every linked AWS repository share that license.

## 9. Implementation plan

### Pass 1 — this branch

- Register this proposal and source ledger.
- Add the architecture Mermaid source.
- Add a machine-readable, disabled-by-default integration contract.
- Add an offline stdlib validator and negative tests for unsafe configurations.
- Do not install packages, start the emulator, or call AWS.

### Pass 2 — integration discovery

- Reconcile existing AWS schema, SDK, Strands, and evaluation infrastructure.
- Confirm no duplicate gate, fixture store, or task router is introduced.
- Choose a pinned host-supported emulator release and official evaluation-suite revision.
- Run only on supported Linux CI or a supported developer host.

### Pass 3 — bounded pilot

- Execute SQS, then S3, then DynamoDB fixtures.
- Record exact model/test/emulator/SDK versions and environment fingerprints.
- Compare emulator behavior with official evaluation evidence and, only if approved, sandbox reference observations.
- Report every unsupported behavior as a gap; do not mask it with cloud fallback.

### Pass 4 — agent-team loop

- Test author proposes/validates a fixture.
- Gap finder replays and files a bounded issue.
- Fixer takes one issue claim and an isolated worktree.
- Independent reviewer and automated gates check correctness, security, and regression.
- Existing PR policy controls promotion.
- Existing evidence systems record actual invocation and integrated outcome.

### Pass 5 — scale only with evidence

Run a controlled manager tournament only after the first pilot shows low false-positive rates, reproducible fixtures, manageable conflicts, and useful integrated outcomes. Measure quality first; throughput is not a substitute for correctness.

## 10. Acceptance criteria

1. Proposal registry and lifecycle validation pass on the exact PR head.
2. Offline contract validation rejects remote endpoints, cloud fallback, ambient credentials, runtime activation, production scope, and unknown contract versions.
3. Focused tests pass and are wired to the canonical repo gate after owner-path review.
4. No AWS account/resource/API call, package install, Docker daemon, or emulator build is implied by CI passing.
5. A pinned supported-host smoke test produces a sanitized receipt before the integration is described as executed.
6. Fidelity status is operation-specific and separates model presence from observed behavior.
7. No emulator pass can authorize production release or replace real-cloud testing.
8. Existing QUE/QDesk, Brain, SHE, evidence, and promotion ownership remains canonical.

## 11. Sources and visual references

See [SOURCES.md](SOURCES.md) for the complete 25-item source ledger, source roles, and transferability notes.

![AWS Emulator agent-team architecture — source image 1](https://assets.aboutamazon.com/dims4/default/770f29a/2147483647/strip/true/crop/1600x900+0+0/resize/767x431!/quality/90/?url=https%3A%2F%2Fassets.aboutamazon.com%2F2b%2F9c%2F38699c294dba9a69b27d004d9729%2Faws-emulator-ai-1-amazonnews-cdlt-09102026.jpeg)

![AWS Emulator agent-team architecture — source image 2](https://assets.aboutamazon.com/dims4/default/f58c09b/2147483647/strip/true/crop/1600x900+0+0/resize/767x431!/quality/90/?url=https%3A%2F%2Fassets.aboutamazon.com%2Ffd%2F1e%2F3401edd44b5397d0120a11ec9f00%2Faws-emulator-ai-2-amazonnews-cdlt-09102026.jpeg)

## 12. Non-goals

This RFP does not authorize merging, deploying, provisioning AWS resources, installing the emulator on Android, creating a fork, adding a mandatory external dependency, changing production credentials, or representing a proposal/contract test as a successful runtime pilot.
