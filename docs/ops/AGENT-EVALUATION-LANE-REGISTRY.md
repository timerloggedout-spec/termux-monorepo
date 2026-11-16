# Agent Evaluation Lane Registry

**Status:** active design contract; adapters are observational and do not become merge authority.

## Purpose
The repository has several evaluation surfaces with different scopes. The control-plane mistake to avoid is treating a single vendor, benchmark, or dashboard as the canonical measure of agent quality.

The canonical evidence boundary remains the repository's redacted JSON/JSONL receipts, SHA/run linkage, task cohort, validation results, attribution confidence, and Action→Effect records.

External evaluators consume that evidence through bounded adapters.

## Lane taxonomy

| Lane | Measures | Use here | Authority |
|---|---|---|---|
| Repository-native development evaluation | lifecycle, review, checks, task outcome, integration evidence | promotion evidence and longitudinal corpus | canonical repository evidence |
| ATES / WTCV / TCV / TPV / RPI | execution and throughput behavior | action/effect and efficiency analysis | canonical derived metrics |
| TDQS / Glama | MCP/tool-definition quality | tool-selection and schema-quality evidence | observational |
| Gamut AI / ATF / ACRS / MAESTRO | agent governance, capability exposure, assurance and threat-model evidence | governance/assurance adapter when scope is appropriate | observational; framework-scoped |
| **GAMUT benchmark** | factual completeness of open-ended generation | research benchmark for completeness/factuality cohorts | observational; benchmark-scoped |
| Langfuse | traces, datasets, experiments, scores | hosted experiment/evaluation adapter; CEEL candidate | observational |
| Phoenix | traces, evaluations, datasets, experiments | open/self-hosted experiment/evaluation adapter | observational |
| PromptLayer | prompt registry/version lineage and request analytics (candidate hypotheses; verify by version) | prompt lifecycle comparison participant | observational; not runtime-verified |
| PostHog | event analytics, experiment assignment/exposure and cohorts (candidate hypotheses; verify by version) | product/experiment measurement participant | observational; not runtime-verified |
| Braintrust | evaluation datasets, scorers and experiment lineage (candidate hypotheses; verify by version) | evaluation comparison participant | observational; not runtime-verified |
| SWE-style reference suites | issue-to-patch/software-engineering task outcomes | bounded external reference comparison | observational |
| AWS Emulator + AWS Emulator Evaluation Suite | AWS API behavioral fidelity for covered operations and multi-step workflows; service-specific coverage only | external cloud-emulation fidelity reference; compare against real AWS sandbox evidence and local project cohorts | observational; upstream read-only; never a security oracle or merge authority |
| Local cohort harnesses | project-specific task success, cost, latency, regressions | highest-fidelity manager experiments | evidence source owned by this repository |

### Gamut is not one thing

Two current uses of the name must not be silently conflated:

1. **Gamut AI** documents a governance/assurance platform with ATF, ACRS, MAESTRO and runtime enforcement surfaces. Its documentation describes Gamut as a governance and evidence system rather than merely an agent orchestrator.
2. **GAMUT** is also the name used by a 2026 research benchmark for factual completeness in open-ended generation.

If a future lane selects either one, the adapter must record the exact product/framework/benchmark identifier and version/date. A name-only gamut label is insufficient provenance.

## Admission contract

An external lane is eligible only when:
1. its scope matches the question being evaluated;
2. the task cohort and evidence schema are frozen;
3. the external adapter is version-pinned or otherwise reproducibly identified;
4. credentials, if any, are runtime-injected and absent from artifacts;
5. raw provider output is redacted before retention;
6. the result can be linked to the same cohort, repository SHA, runtime fingerprint and evaluator version;
7. missing or unsupported measurements remain null/missing rather than synthetic zeroes.

## Comparison design

```text
                         SAME COHORT
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
     Repository          Gamut adapter       Other adapter
     canonical           (optional)        Langfuse/Phoenix/
     evidence                               SWE/local/etc.
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                    Evidence normalization
                              |
                              v
                    3L0 / MoneyBall analysis
```

Compare task outcome, integration quality, time, useful/duplicate actions, retries, conflicts, human intervention, provider failures, attribution confidence, validation results and cost. Do not collapse unlike scopes into one leaderboard number.

## Selection rule

Use **parallel adapters before replacement**. A lane is retained when it adds decision-relevant evidence at acceptable operational cost. A lane is retired when it duplicates existing evidence without improving coverage, reproducibility, or decision quality.

No external score is a universal model-quality score and no external dashboard is a merge gate by itself.

## Cloud-emulator fidelity

AWS Emulator is an optional local execution surface, not a canonical evaluator. Its public API models (Smithy JSON AST) describe service contracts; the AWS Emulator Evaluation Suite supplies reusable behavioral scenarios; real AWS sandbox accounts remain the reference oracle for any newly authored fidelity test. The evaluation suite states that each included test was verified against at least two sandboxed AWS accounts, and that uncovered behavior is not verified. The AWS Emulator and evaluation-suite repositories both declare upstream contribution restrictions; our forks are tracking mirrors, not assumed contribution channels.

Admission requirements for any local cohort using an emulator:
1. Pin emulator release/commit, API-model snapshot, evaluation-suite commit, SDK/CLI versions, and runner version.
2. Record exact service, operation, scenario, request-shape class, expected result/error, and coverage status.
3. Separate `PASS`, `FAIL`, `ERROR`, `SKIP`, `UNSUPPORTED`, and `NOT_TESTED`; unsupported or absent tests are not passes.
4. Run each stateful fidelity test in an isolated emulator instance; retain cleanup outcomes.
5. Use only loopback endpoints and emulator-generated credentials; do not expose the listener or inject real AWS credentials.
6. Disable emulator telemetry for controlled evaluation runs unless a separately reviewed measurement requires it.
7. Preserve a real-AWS sandbox validation tier for IAM, cross-account/Region, quotas, throttling, outages, data-plane behavior, and release readiness.
8. Link results to the existing canonical experiment record and repository SHA. Do not create a parallel evidence ledger.

AWS Emulator is explicitly unsuitable for production workloads and security testing. LocalStack, SAM local, mocks, and real AWS are complementary comparison arms with distinct scopes; no one surface is assumed to subsume the others.

## Current alternatives

The current research set already contains Langfuse, Phoenix, TDQS, Tree-sitter/Lizard/Radon complexity providers, SWE-style reference evaluation, Docker/Codespaces parity, and repository-local cohorts. Gamut therefore belongs in the same adapter registry rather than receiving a privileged routing branch.

## Sources

- Gamut AI framework overview: https://docs.gamutassure.com/frameworks/overview/
- Gamut AI agentic stack: https://docs.gamutassure.com/agentic/overview/
- Gamut AI ATF: https://docs.gamutassure.com/frameworks/atf/
- Gamut AI ACRS: https://docs.gamutassure.com/frameworks/acrs/
- Gamut AI MAESTRO: https://docs.gamutassure.com/frameworks/maestro/
- GAMUT factual-completeness benchmark: https://arxiv.org/abs/2607.19322

## CEEL multi-platform comparison

Langfuse, PromptLayer, PostHog and Braintrust enter as four independent, observational candidate factors. They are not assumed to be substitutes: they may compete within one capability while complementing one another across capabilities. The CEEL matrix preregisters a native baseline and a complete 2^4 combination design when all adapters are executable. Each adapter must satisfy the admission contract; missing data stays unknown, and no vendor score becomes merge authority.

The native repository evidence path remains canonical. Phoenix, DSPy, SWE-style cohorts and local harnesses remain existing participants; CEEL adds comparison links rather than duplicating their machinery.
