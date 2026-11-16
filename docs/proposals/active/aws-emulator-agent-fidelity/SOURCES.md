# Source register — AWS Emulator adoption and agent-built fidelity loop

Research snapshot: 2026-11-16. Links are source references supplied by the operator unless otherwise marked. The register distinguishes primary vendor statements, independent reporting, code repositories, and visual assets. A repository's presence in this list does not mean it is adopted, forked, licensed for vendoring, or runtime-compatible.

## Primary narrative and engineering method

1. [GeekWire — AWS gives developers a free local stand-in for its cloud, built from scratch by AI agents](https://www.geekwire.com/2026/aws-gives-developers-a-free-local-stand-in-for-its-cloud-built-from-scratch-by-ai-agents/) — independent reporting on the launch, three-team structure, and caveats.
2. [About Amazon — How autonomous AI agents built AWS Emulator](https://www.aboutamazon.com/news/aws/how-autonomous-ai-agents-built-aws-emulator) — primary AWS account of the test-author, gap-finder, and fixer teams; Smithy/API models as specification and real AWS as reference oracle.
5. [About Amazon — AWS unveils frontier agents](https://www.aboutamazon.com/news/aws/amazon-ai-frontier-agents-autonomous-kiro) — agent roles and persistent, long-running software-development work.
6. [About Amazon — AWS CEO: AI inference transforms developer capabilities](https://www.aboutamazon.com/news/aws/aws-ceo-ai-inference-transforms-developer-capabilities) — task-accomplishing agents as a new compute/application building block.
7. [Anthropic — Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/research/building-c-compiler) — primary research on long-running agent loops, isolated Docker workspaces, task locks, test oracles, and CI guardrails. Transfer lesson: autonomy is enabled by harness quality, not raw parallelism.
8. [GeekWire — Amazon rewrites its software engineering playbook for an era when AI writes the code](https://www.geekwire.com/2026/amazon-rewrites-its-software-engineering-playbook-for-an-era-when-ai-writes-the-code/) — independent reporting on the changing engineering role and agent-generated implementation.
9. [InfoWorld — AWS unveils local emulator service](https://www.infoworld.com/article/4247383/aws-unveils-local-emulator-service-to-help-enterprises-accelerate-app-development-and-testing.html) — independent analysis of benefits and limits, including throttling/outage/region gaps and sandboxing risk.
10. [LocalStack — The Road Ahead for LocalStack](https://blog.localstack.cloud/the-road-ahead-for-localstack/) — vendor statement on account-based unified distribution and free-plan boundaries; verify current terms before adoption.

## Upstream implementation and models

3. [aws/aws-emulator](https://github.com/aws/aws-emulator) — official emulator implementation; local API endpoint, CLI/SDK compatibility, Rust workspace, server and embedded modes, known-gap ledger, and build resource requirements.
4. [aws/api-models-aws](https://github.com/aws/api-models-aws) — public Smithy JSON AST models. Its README warns the repository is generated and not closely monitored; use as a read-only specification input, not as a PR target.
13. [aws organization](https://github.com/aws) — upstream project discovery index, not a dependency.
14. [aws/eks-pod-identity-agent](https://github.com/aws/eks-pod-identity-agent) — example of a focused, service-specific agent with explicit build/test workflows; not an emulator component.
15. [aws/aws-advanced-python-wrapper](https://github.com/aws/aws-advanced-python-wrapper) — database-driver wrapper pattern and failure-monitoring reference; not required by this integration.
16. [aws/aws-sam-cli](https://github.com/aws/aws-sam-cli) — serverless build/deploy/local-development tooling reference; compare only if a concrete SAM workflow is selected.
17. [aws/c3r](https://github.com/aws/c3r) — AWS repository reference; evaluate its actual scope/license before reuse.
18. [aws/jsii](https://github.com/aws/jsii) — polyglot library and interface-generation reference, relevant to CDK's language ecosystem rather than emulator runtime.
19. [aws/csi-components](https://github.com/aws/csi-components) — minimal container-component build and supply-chain reference; not a runtime dependency.
20. [aws/aws-cdk](https://github.com/aws/aws-cdk) — infrastructure-as-code reference; optional and separate from local emulator execution.
22. [aws/agent-toolkit-for-aws](https://github.com/aws/agent-toolkit-for-aws) — official AWS skills, MCP server, plugins, and agent guardrails. Candidate for later metadata-only skill discovery; no automatic install or credentialed AWS access.
23. [aws/aws-kotlin-repo-tools](https://github.com/aws/aws-kotlin-repo-tools) — repository automation/tooling reference; not a runtime dependency.

## Evaluation and fork references

11. [timerloggedout-spec/aws-emulator-evaluation-suite_fork](https://github.com/timerloggedout-spec/aws-emulator-evaluation-suite_fork) — operator fork reference. Inspect current fork HEAD, license, upstream divergence, and whether the fork adds value before using it. The upstream evaluation suite is explicitly read-only and contains behavioral tests driven by boto3.
12. [timerloggedout-spec/aws-emulator_fork](https://github.com/timerloggedout-spec/aws-emulator_fork) — operator fork reference. No fork code is vendored or assumed compatible by this proposal.
21. [timerloggedout-spec/event-ruler_fork](https://github.com/timerloggedout-spec/event-ruler_fork) — related AWS ecosystem fork; separate event-pattern capability, not an emulator dependency.

## Visual assets supplied with the research set

24. [AWS Emulator architecture image 1](https://assets.aboutamazon.com/dims4/default/770f29a/2147483647/strip/true/crop/1600x900+0+0/resize/767x431!/quality/90/?url=https%3A%2F%2Fassets.aboutamazon.com%2F2b%2F9c%2F38699c294dba9a69b27d004d9729%2Faws-emulator-ai-1-amazonnews-cdlt-09102026.jpeg) — embedded in RFP.md as a linked source asset.
25. [AWS Emulator architecture image 2](https://assets.aboutamazon.com/dims4/default/f58c09b/2147483647/strip/true/crop/1600x900+0+0/resize/767x431!/quality/90/?url=https%3A%2F%2Fassets.aboutamazon.com%2Ffd%2F1e%2F3401edd44b5397d0120a11ec9f00%2Faws-emulator-ai-2-amazonnews-cdlt-09102026.jpeg) — embedded in RFP.md as a linked source asset.

## Verified technical observations

- AWS Emulator README describes a local HTTPS endpoint at `127.0.0.1:9297`, AWS CLI/SDK endpoint configuration, synthetic emulator credentials, server and Rust embedded modes, and a supported source-build path for Linux x86_64/aarch64.
- AWS Emulator's source README says a full cold build needs at least 100 GB free for Cargo's target directory. This makes building it on a constrained Termux phone inappropriate; use a supported host/CI runner if a pilot is approved.
- The API model repository contains Smithy JSON AST models organized by service and version. Its README says it is generated from other sources and not closely monitored.
- AWS Emulator is for development/testing, not production or security testing. Its operation-level fidelity must be checked against published fidelity evidence and the official evaluation suite.
- The official evaluation suite describes short Python/boto3 fidelity tests whose expected behavior was verified against at least two sandbox AWS accounts. Only behavior covered by a fidelity test is verified by that suite.
- InfoWorld's launch analysis identifies resilience gaps such as throttling, outages, snapshots/restore, and per-region availability, and warns the emulator does not sandbox executed code. These are material limitations, not footnotes.
- LocalStack's 2025/2026 delivery update describes account-based unified distribution and free-tier non-commercial restrictions. Treat this as a changing vendor policy and re-check current terms before any selection.

## Interpretation boundary

The strongest transferable idea is the closed-loop engineering method: specification → reference test → replay → gap issue → bounded fix → independent gates → evidence. It is not evidence that a small repository should imitate AWS's agent count, internal services, or cloud build pipeline. All performance, fidelity, cost, and autonomy claims must be measured in this repository before being asserted.
