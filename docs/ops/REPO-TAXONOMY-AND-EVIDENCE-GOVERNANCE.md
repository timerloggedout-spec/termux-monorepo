# Repository Taxonomy, Evidence Governance, and System-One Tournament

**Status:** implementation blueprint plus reproducible offline scoring utility. Live provider/model quality remains unverified until candidate outputs are collected against the same labeled bank.  
**Scope:** `termux-monorepo` intent, classifier families, System One cross-evaluation, runtime/message performance, and reconciliation of GitHub claims against durable evidence.  
**Anchor issue:** [#1450 — Tournament Leaderboard for Production Utility](https://github.com/timerloggedout-spec/termux-monorepo/issues/1450)  
**Related implementation:** [PR #740](https://github.com/timerloggedout-spec/termux-monorepo/pull/740)

## 1. What is covered, and how many categories?

There is no single universal category count for this repository: several different taxonomies serve different purposes and must not be collapsed into one number. In the existing System One / Jev scaffold, the **operational routing catalog has six top-level labels**: `routing`, `security`, `agent`, `code`, `ops`, and `general`. Those are routing intents, not the full repository mission, classifier task families, GitHub labels, or benchmark suites.

For this implementation, use **12 mission domains** and **8 evaluation task families** as an explicit, versioned working taxonomy. They are proposed organizing dimensions, not a claim that the repository already has complete implementations for every leaf. The machine-readable registry is `docs/ops/repository-taxonomy.v1.json`. Each entry records its status and evidence level. Add a domain only with a concrete issue, artifact, owner, and acceptance criterion; do not create categories just to inflate coverage.

### 12 mission domains

1. **Repository governance & provenance** — issue/PR/commit relationships; claim ledgers; source links; ownership; change traceability.
2. **AI / agent orchestration** — role contracts, routing, tool boundaries, delegation, retries, stop conditions.
3. **System One / typed decisions** — choice, score, yes/no, ranking, abstention, constrained outputs.
4. **Text classification & routing** — intent, support queues, repository task routing, OOD detection.
5. **Extraction & structured understanding** — entity/span extraction, schema parsing, multi-label outputs.
6. **Code intelligence & repair** — code review, patch generation, regression analysis, issue-to-patch workflows.
7. **Performance & resource efficiency** — latency distributions, throughput, concurrency, memory, token/compute cost.
8. **Observability & message quality** — trace/span structure, message size, retries, tool-call failures, privacy-safe diagnostics.
9. **Security & trust** — prompt injection, secret boundaries, dependency risk, provenance, policy compliance.
10. **Testing & evaluation science** — datasets, splits, judges, statistical uncertainty, reproducibility, regression gates.
11. **Research & FOSS procurement** — discovery, evidence quality, upstream status, compatibility, license/terms review.
12. **Operations & delivery** — CI, release readiness, deployment health, artifacts, rollback and incident evidence.

### 8 benchmark task families

- typed decision; single-label classification; multi-label classification; span/entity extraction; ranking/pairwise preference; abstention/selective prediction; code task success; tool/trace/process conformance.

The question-bank fixtures currently exercise only a **small synthetic slice** of these task families. Coverage must be reported as measured question IDs per task/language/risk slice, not inferred from the number of taxonomy entries.

## 2. System One should evaluate System One — with independent evidence

Use a tournament, not a single model-as-oracle leaderboard:

1. **Shared cases:** all candidates receive the same versioned input, allowed context, schema, timeout and task-specific options.
2. **Candidate runs:** record candidate/model, runtime, adapter, exact configuration, source revision, prompt/schema hashes, start/end timestamps, latency, token/resource usage, response and error class.
3. **Ground-truth scoring first:** compare to labeled expected outputs wherever possible. Candidate self-reports and peer opinions are not ground truth.
4. **Pairwise cross-judging:** candidate A and B may compare blinded outputs, with left/right order randomized and reversed. Store each judge's verdict and rationale separately.
5. **Judge calibration:** each judge must score known control pairs; measure agreement with expert labels, position bias, self-preference, variance and abstention. A judge with failed calibration is diagnostic only.
6. **Independent adjudication:** disagreements go to a human/curated rubric or an explicitly separate judge pool. Never let a candidate unilaterally certify itself.
7. **Promotion gates:** require minimum sample count, slice coverage, uncertainty bounds, no critical safety regression, valid schemas, acceptable cost/latency, and reproducible reruns. Use a held-out test split; tune thresholds on validation only.

Pairwise win rates are useful diagnostics, not substitutes for task correctness. Keep separate score dimensions for correctness, calibration/abstention, schema validity, safety, latency, throughput, cost, and reproducibility. Report Pareto frontiers or context-specific recommendations instead of pretending one scalar winner is universally best.

## 3. Performance and message quality

Collect **per request and per tool hop** rather than only an aggregate run duration:

- end-to-end latency and component latency; p50/p90/p95/p99; time-to-first-token where applicable;
- throughput under a fixed concurrency schedule; queue wait, timeout, retry and cancellation rates;
- input/output bytes and tokens, truncation, context size, tool-call count, invalid schema rate;
- peak memory/CPU/GPU where measurable, energy/cost when instrumentation is credible;
- message/trace completeness, correlation IDs, parent-child span linkage, error category and retry lineage;
- task correctness and safety outcome alongside speed; latency never counts as correctness.

Use a vendor-neutral trace shape and OpenTelemetry GenAI semantic conventions where appropriate. Avoid storing raw secrets, credentials, personal data, or full sensitive prompts in routine telemetry. Prefer redaction, stable hashes, sampled payloads and explicit retention rules. Do not compare performance unless hardware/runtime, warm/cold state, batch size, concurrency, context length, cache state, timeout, and measurement method are stated.

## 4. Commits vs. claims vs. issues and PR comments

A commit message is an assertion about intent; it is not proof that the change works. A passing test is evidence for only the behavior it exercises. An issue comment can be a hypothesis, automated triage, bot error, or human decision; preserve author, timestamp, URL, and trust class.

Every material claim should be represented as:

- **claim ID and exact statement**;
- **claim kind:** intent, implementation, test, security, performance, compatibility, licensing, deployment, or production readiness;
- **scope:** file/function/endpoint, task slice, runtime, version, and environment;
- **supporting evidence:** commit SHA, changed file/line, test name/run ID, raw artifact hash, issue/PR/comment URL;
- **status:** `SUPPORTED`, `PARTIALLY_SUPPORTED`, `CONTRADICTED`, `UNVERIFIED`, `STALE`, or `NOT_APPLICABLE`;
- **reviewer and last-verified time**, plus superseding claim/evidence links.

Reconciliation rules:
- A commit/PR description without a test or artifact remains `UNVERIFIED`.
- A test pass supports only the tested contract, not general production quality.
- Mock/fixture success supports wiring, not real model inference.
- A live HTTP 200 supports reachability, not correctness.
- A bot response such as HTTP 429/incomplete invocation is a failed or missing observation, not a model-quality failure.
- Conflicting comments remain visible and linked; never silently rewrite history or treat reaction counts as truth.
- If a claim has no current evidence, mark it stale/unverified rather than inferring success from a later commit.
- Link every PR checklist item to the exact test/evidence that supports it; link every issue acceptance criterion to a PR/commit and verification artifact.

## 5. License-aware FOSS inspiration map

Treat these projects as **design references**, not drop-in dependencies. Before copying code, prompts, datasets, weights or fixtures, inspect the exact repository's current LICENSE, model/dataset terms, dependency licenses, and any non-commercial / attribution / acceptable-use clauses. Record a license review with URL, revision/date, artifact covered, intended use, obligations, and approver. “Open source,” “open weights,” and “public on GitHub” are not interchangeable.

| Inspiration | Adaptable pattern | Initial posture | Primary source |
|---|---|---|---|
| Inspect AI | task / solver / scorer separation; eval logs | Study architecture; license-check before code reuse | https://github.com/UKGovernmentBEIS/inspect_ai |
| OpenAI Evals / simple-evals | eval definitions and regression cases | Reimplement compatible concepts; check repo license and dependencies | https://github.com/openai/evals ; https://github.com/openai/simple-evals |
| EleutherAI lm-evaluation-harness | task registry and repeatable model comparisons | Adapter pattern; review license and model/dataset terms | https://github.com/EleutherAI/lm-evaluation-harness |
| HELM | multi-metric, transparent evaluation | Adopt multi-axis reporting; do not conflate benchmark coverage | https://github.com/stanford-crfm/helm |
| DSPy | declarative modules and metric-driven optimization | Inspiration for typed module boundaries; verify version-specific license | https://github.com/stanfordnlp/dspy |
| Promptfoo | scenario-based tests, red-teaming and CI gates | Optional adapter; review licensing and security posture | https://github.com/promptfoo/promptfoo |
| Langfuse / Phoenix | traces, dataset-backed evaluation and feedback loops | Integrate via OpenTelemetry/export boundaries first | https://github.com/langfuse/langfuse ; https://github.com/Arize-ai/phoenix |
| OpenTelemetry GenAI conventions | portable spans and GenAI attributes | Prefer standard semantic fields; conventions evolve | https://opentelemetry.io/docs/specs/semconv/gen-ai/ |
| SWE-bench | issue-grounded repository tasks and patch evaluation | Use for code-agent eval design; dataset terms and task reproducibility matter | https://github.com/swe-bench/SWE-bench |
| Aider benchmark | language-level code edit evaluation and runtime accounting | Study benchmark methodology; pin exact dataset/version | https://github.com/Aider-AI/aider |
| GLiNER | caller-defined span/entity extraction | Keep extraction task separate from label classification | https://github.com/urchade/GLiNER |
| Selective prediction / abstention | risk-versus-coverage curves and calibrated reject option | Reimplement metrics; fit thresholds on validation split | https://aclanthology.org/2021.acl-long.84/ |
| OpenSSF Scorecard | supply-chain hygiene checks | Optional CI evidence source; avoid equating score with safety | https://github.com/ossf/scorecard |
| CodeQL | semantic static analysis | Use existing authorized scanning or local query packs; respect product/license terms | https://codeql.github.com/ |
| MLflow / DVC | run and dataset lineage | Consider only if the repository's data/experiment volume warrants it | https://github.com/mlflow/mlflow ; https://github.com/iterative/dvc |

The list is intentionally not a dependency declaration. A clean-room rewrite of a mechanism can reduce code-license coupling but does not automatically eliminate obligations relating to copied text, datasets, model weights, patents, trademarks, or API terms. Legal review is needed for ambiguous or high-impact reuse.

## 6. Implementation and evidence status

Implemented in this branch:
- versioned classifier question bank and deterministic smoke baseline;
- bounded parallel runner with deterministic output ordering and JSONL receipts;
- explicit model/runtime/adapter identity and candidate-state vocabulary;
- this taxonomy and cross-evaluation/evidence-governance contract;
- offline tournament scorer for candidate result receipts.

Not yet proven:
- real provider endpoint success or model quality;
- complete coverage of every mission-domain leaf;
- a calibrated independent judge pool;
- stable production latency/cost under matched load;
- legal clearance for any third-party code, dataset, weights or service terms.

## 7. Research citations

- Inspect AI docs: https://inspect.aisi.org.uk/
- OpenAI Evals: https://github.com/openai/evals
- lm-evaluation-harness: https://github.com/EleutherAI/lm-evaluation-harness
- HELM: https://crfm.stanford.edu/helm/
- DSPy: https://dspy.ai/
- Promptfoo: https://github.com/promptfoo/promptfoo
- Langfuse: https://langfuse.com/docs
- Phoenix: https://arize.com/docs/phoenix
- OpenTelemetry GenAI conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- SWE-bench paper: https://arxiv.org/abs/2310.06770
- GLiNER NAACL 2024 paper: https://aclanthology.org/2024.naacl-long.300.pdf
- The Art of Abstention (ACL 2021): https://aclanthology.org/2021.acl-long.84/
- OpenSSF Scorecard: https://github.com/ossf/scorecard
- CodeQL: https://codeql.github.com/
- MLflow: https://github.com/mlflow/mlflow
- DVC: https://github.com/iterative/dvc
- Related issue / context: https://github.com/timerloggedout-spec/termux-monorepo/issues/1450
