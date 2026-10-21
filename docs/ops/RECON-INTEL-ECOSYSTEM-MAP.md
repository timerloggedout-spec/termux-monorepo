# RECON INTEL — AI Engineering Ecosystem Map

**Status:** evidence-backed reconnaissance and integration plan  
**Repository baseline inspected:** `feat/system-one-experiment-lanes` at `3051b1a10c0d7bf3a146e08cf241ee69652f6e7f`  
**Purpose:** map existing repository capabilities before proposing dependencies; identify high-leverage integrations and clean-room alternatives; preserve source, implementation, license, and evidence distinctions.

## Executive result

The repository already has a substantial evaluation and reconciliation substrate. The correct move is **not** to bolt on five overlapping platforms. It is to connect existing controls through shared contracts and adopt external systems selectively.

### Existing implementation evidence found

| Capability | Repository evidence | Assessment |
|---|---|---|
| Agent/model/tool evaluation architecture | `docs/architecture/AGENT-EVALUATION-FRAMEWORK.md` | Existing architecture defines outcomes, cohorts, treatments, repeated trials, blinded evaluation, benchmark families, and provenance. |
| Blind agent evaluation | `docs/architecture/AGENT-SELECTION-BLIND-EVALUATION.md`; `.agents/skills/blind-agent-evaluation/SKILL.md` | Existing design/skill; use as the candidate tournament’s blindness boundary. |
| SWE reference evaluation | `.github/workflows/swe-reference-evaluation.yml`; `docs/evaluations/swe-performance/`; `scripts/ci/swe_evaluation_contract.py` | Existing, bounded, manually enabled reference lane. One-instance smoke receipts are not benchmark-quality claims. |
| CodeQL | `.github/workflows/codeql-advisory.yml`; `docs/proposals/active/actions-refinements/B6-CODEQL-ADVISORY.md` | Implemented advisory workflow for Actions, JavaScript/TypeScript, and Python. Does not cover all repository languages. |
| OpenSSF Scorecard | `.github/workflows/scorecard-advisory.yml`; `docs/proposals/active/actions-refinements/B6-SCORECARD-ADVISORY.md` | Implemented advisory lane with pinned action and reviewed container digest boundary. |
| Repository and cross-provider reconciliation | `docs/ops/RECON_INTEL.md`; `.github/agentic/recon-intel-policy.json`; `.github/workflows/recon-intel-discovery.yml`; `.github/workflows/recon-intel-reconcile.yml` | Existing observation-first, SHA-bound coordination and explicitly authorized reconciliation. |
| Production reconciliation skill | `.github/skills/production-reconciliation/SKILL.md` | Existing RECON → PLAN → IMPLEMENT → COMMIT → WAIT → VALIDATE → RE-FETCH → CLASSIFY → RECORD → REPEAT protocol. |
| PR/Actions evidence evaluation | `.github/workflows/pr-evidence-evaluation.yml`; `.github/workflows/continuous-evaluation.yml`; `.github/workflows/repository-development-evaluation.yml` | Existing evaluation and workflow evidence surfaces; use them rather than create parallel ledgers. |
| GitHub telemetry | `.github/workflows/github-telemetry-snapshot.yml`; `docs/ops/GITHUB-OBSERVABILITY.md`; `ops/github-telemetry/` | Existing longitudinal Actions/repository telemetry and metric policy. |
| Classifier registry and offline tournament utility | `docs/ops/CLASSIFIER-REGISTRY-AND-EVALUATION.md`; `scripts/classifier_eval.py`; `scripts/eval_tournament.py` | Existing first-stage taxonomy, question-bank, and offline pairwise scoring work on the experiment branch; CI status must be checked against the exact current SHA. |

**Coverage caveat:** the inventory above is grounded in file paths and the contents of the named documents/workflows. A path search cannot prove that a tool name is absent from every historical file or arbitrary source file. The table labels integrations found in authoritative paths, not an exhaustive semantic scan of the entire 5,000+ path tree.

## Candidate ecosystem and intended role

| Candidate | Best-fit role | Proposed integration boundary | Status in inspected repository | Key caveat |
|---|---|---|---|---|
| [DSPy](https://github.com/stanfordnlp/dspy) | Program/signature optimization for routing, extraction, and multi-step pipelines | Optional optimizer adapter that consumes a frozen train/validation split and emits a versioned program/config plus held-out evaluation receipts | Research candidate; no dedicated integration path found in the inspected path inventory | Optimizer must not see held-out test labels. Verify current license, dependencies, and model/provider terms before reuse. |
| [Langfuse](https://github.com/langfuse/langfuse) | LLM traces, prompts, datasets, scores, production feedback | OTLP/OpenTelemetry or narrow exporter adapter; project evidence ledger remains canonical | Research candidate; no dedicated integration path found in the inspected path inventory | Self-hosting, cloud, enterprise features, and release licenses/terms may differ; check exact revision and deployment mode. |
| [Arize Phoenix](https://github.com/Arize-ai/phoenix) | Open-source tracing, span inspection, retrieval/agent evaluation | Alternative trace/eval sink behind the same normalized event contract; do not require Phoenix-specific SDK types in core code | Research candidate; no dedicated integration path found in the inspected path inventory | Validate the current license and the relevant integration/hosted terms; do not duplicate Langfuse and Phoenix ingestion without a decision. |
| [SWE-bench](https://github.com/swe-bench/SWE-bench) | Issue-to-patch task benchmark | Reuse existing SWE reference workflow/manifest contract; add datasets only through a pinned cohort manifest and approved license review | Related reference-evaluation lane exists; benchmark dataset execution is optional/manual and bounded | Dataset versions, instance validity, environment reproducibility, contamination, and patch-verification rules matter. |
| [CodeQL](https://codeql.github.com/) | Semantic static analysis and security findings | Keep the current isolated advisory workflow; promote only through a reviewed policy and supported language/build matrix | Implemented, advisory | CodeQL CLI/query/language and product terms are distinct from the MIT-licensed action wrapper; inspect current terms before changing use. |
| [OpenSSF Scorecard](https://github.com/ossf/scorecard) | Repository supply-chain posture signals | Keep current advisory workflow; normalize findings into the evidence ledger, never a universal trust score | Implemented, advisory | Score is a signal, not a security proof; pinned action and image digest checks are part of current boundary. |
| [OpenTelemetry GenAI conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) | Vendor-neutral traces and runtime metrics | Canonical internal event/span schema; exporters to optional backends | Architecture recommendation; verify current dependencies before claiming instrumentation is complete | Semantic conventions evolve; pin schema version and redact sensitive payloads. |
| [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) | Task/solver/scorer evaluation runner | Consider an adapter for benchmark execution, preserving existing JSONL receipt schema | Research candidate | Evaluate runner overlap, plugin trust, data terms, and license before adoption. |
| [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) | Reproducible model/task evaluations | Import task adapters only where task semantics and output schemas align | Research candidate | Avoid duplicating the existing AEF orchestration and distinguish model benchmarks from repository task success. |
| [HELM](https://crfm.stanford.edu/helm/) | Multi-metric evaluation design | Adopt scorecard design principles: accuracy, robustness, calibration, efficiency, fairness/safety where relevant | Methodology inspiration | Benchmark availability does not automatically grant reuse rights for all datasets or artifacts. |
| [Promptfoo](https://github.com/promptfoo/promptfoo) | Prompt regression, red-team and CI testing | Optional CLI adapter for scenario definitions; normalize output to repository receipts | Research candidate | Avoid a second source of truth for test definitions. Review licenses and secret-safe configuration. |
| [Syft](https://github.com/anchore/syft) + [Grype](https://github.com/anchore/grype) | SBOM generation and vulnerability matching | Artifact-stage SBOM + vulnerability manifest linked to commit, lockfiles, image digest and advisory DB timestamp | New candidate; no implementation inferred from path scan | Findings depend on database freshness, package detection, exceptions, and severity policy. |
| [pytest-benchmark](https://github.com/ionelmc/pytest-benchmark) | Reproducible Python microbenchmarks | Use for deterministic local hot paths, not end-to-end model latency alone | New candidate | Pin environment; avoid flaky hard thresholds before a baseline distribution exists. |
| [Mutation testing](https://github.com/theofidry/awesome-mutation-testing) | Test-suite fault-detection quality | Start with small changed-module cohort; record killed/survived mutants and runtime | New candidate | Costly; do not make broad mutation sweeps blocking until calibrated. |
| [Test Impact Analysis](https://docs.datadoghq.com/tests/test_impact_analysis/) | Selective test execution based on change impact | Prefer a clean-room dependency graph + coverage mapping before any vendor dependency | Research lead | Third-party docs are not proof of open-source availability or terms; selection must not suppress required security/regression suites. |
| [Giskard](https://github.com/Giskard-AI/giskard-oss) / [Guardrails](https://github.com/guardrails-ai/guardrails) | LLM quality/risk tests and output validation | Evaluate as task-family adapters, not a new global policy authority | Research candidates | Inspect current maintenance, exact license, transitive dependencies and whether checks duplicate current tests. |
| [DVC](https://github.com/iterative/dvc) / [MLflow](https://github.com/mlflow/mlflow) | Dataset/model/run lineage | Adopt only if current Git + JSONL artifacts + provenance records stop meeting query/scale requirements | Deferred | Adds operational surface; do not introduce a second artifact ledger without a measured need. |

## Novel integration: one contract, multiple evidence producers

Build a small internal **Evidence Envelope** rather than a monolithic vendor integration. Each tool becomes an adapter that emits the same versioned record:

- `schema_version`, `event_id`, `event_type`, UTC timestamps;
- repository, source commit SHA, workflow/run/job IDs, task/cohort and treatment IDs;
- producer identity, tool version, adapter version, config/prompt/dataset hashes;
- outcome status (`PASS`, `FAIL`, `PARTIAL`, `UNKNOWN`, `ERROR`);
- measurements and units (latency, tokens, cost, memory, retries, coverage);
- evidence URIs and SHA-256 hashes; redaction and retention classifications;
- license/provenance references for external code, datasets, models and artifacts.

Keep **source records immutable**. Derived leaderboards and summaries are rebuildable projections, not authorities. Bind every result to the exact commit and experiment configuration; never join solely by branch name or display label.

### Recommended flow

1. **RECON:** inventory source files, workflows, dependencies, existing records, current SHA and outstanding issues.
2. **Classify:** mark each capability `EXISTS`, `PARTIAL`, `PROPOSED`, `BLOCKED`, or `RETIRED`; attach path and evidence.
3. **Select:** state the missing capability and why the existing substrate cannot satisfy it.
4. **License/provenance gate:** review code, data, weights, hosted terms, transitive dependencies and attribution separately.
5. **Prototype adapter:** no broad refactor; emit the canonical receipt schema.
6. **Validate:** unit tests, fixture tests, contract checks, license/SBOM scan, failure-mode test, matched baseline.
7. **Observe:** advisory/shadow mode with redacted artifacts.
8. **Promote:** require reproducible improvement, acceptable cost/latency, no safety regression, explicit owner and rollback plan.
9. **Reconcile:** re-fetch current branch/PR SHA, check current CI and comments, update status, repeat.

## Prioritized roadmap

### P0 — Reconcile existing work first
- Run the exact current-head checks for classifier/tournament additions; do not infer green status from earlier commits.
- Link SWE evaluation manifests, CodeQL SARIF status, Scorecard output, telemetry snapshots and PR evidence into one index.
- Reconcile duplicate evaluation concepts across AEF, SWE performance, continuous evaluation and the classifier lane; retain the authoritative owner for each.

### P1 — Low-coupling improvements
- Add an Evidence Envelope JSON Schema and strict validator.
- Add a manifest-only inventory for candidate integrations, versions, upstream URLs, license review state, evidence path, owner and next action.
- Add performance baselines for internal deterministic hot paths before gating on percentages.
- Add SBOM generation as an advisory artifact if the existing dependency inventory cannot answer package/source questions.

### P2 — Optional adapters
- Prototype a single trace exporter against OpenTelemetry first; compare Langfuse and Phoenix using the same synthetic trace set and privacy constraints.
- Prototype DSPy on a small held-out-safe classifier/extraction task; compare against current deterministic baseline and at least one non-optimized candidate.
- Expand SWE reference cohorts only after dataset/version, compute budget, secret handling, reproducibility and license review are recorded.

### P3 — Promotion only after evidence
- Consider mutation testing, test-impact analysis, and additional benchmark runners after cost and failure modes are measured.
- Do not add both Langfuse and Phoenix as required runtime dependencies by default.
- Do not let any model, judge, observability backend, security score or bot comment unilaterally approve its own result or authorize a repository write.

## License and provenance policy

For every candidate, record separate statuses for:
1. source-code license at the exact pinned revision;
2. dependency/transitive license report;
3. dataset and benchmark terms;
4. model weights and model card terms;
5. hosted API/service terms and data retention;
6. prompts, examples and copied documentation;
7. trademarks, patents or other special restrictions when applicable.

Allowed disposition values: `APPROVED`, `APPROVED_WITH_OBLIGATIONS`, `REVIEW_REQUIRED`, `REJECTED`, `NOT_APPLICABLE`. An unknown license is `REVIEW_REQUIRED`, never assumed permissive. A clean-room rewrite may reduce source-code copying but does not automatically clear dataset, weights, text, patents, trademarks or service terms.

## Primary-source references

- DSPy: https://github.com/stanfordnlp/dspy and https://dspy.ai/
- Langfuse: https://github.com/langfuse/langfuse and https://langfuse.com/docs
- Arize Phoenix: https://github.com/Arize-ai/phoenix and https://arize.com/docs/phoenix
- SWE-bench: https://github.com/swe-bench/SWE-bench and https://www.swebench.com/SWE-bench/
- CodeQL: https://codeql.github.com/ and https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-cli
- OpenSSF Scorecard: https://github.com/ossf/scorecard
- OpenTelemetry GenAI conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- Inspect AI: https://github.com/UKGovernmentBEIS/inspect_ai and https://inspect.aisi.org.uk/
- lm-evaluation-harness: https://github.com/EleutherAI/lm-evaluation-harness
- HELM: https://crfm.stanford.edu/helm/
- Promptfoo: https://github.com/promptfoo/promptfoo
- Syft: https://github.com/anchore/syft
- Grype: https://github.com/anchore/grype
- pytest-benchmark: https://github.com/ionelmc/pytest-benchmark
- Mutation-testing index: https://github.com/theofidry/awesome-mutation-testing
- Giskard: https://github.com/Giskard-AI/giskard-oss
- Guardrails: https://github.com/guardrails-ai/guardrails
- DVC: https://github.com/iterative/dvc
- MLflow: https://github.com/mlflow/mlflow

**Research discipline:** links above are primary project/documentation entry points. This map is not a legal opinion or a guarantee of current release license. Before dependency adoption, capture the exact release/revision and inspect its license and all applicable data/model/service terms.
