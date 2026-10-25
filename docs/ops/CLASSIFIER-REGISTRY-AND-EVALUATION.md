# Classifier Registry and Parallel Evaluation

**Status:** research-backed implementation proposal; observe-only until live adapters and labeled evaluation are verified.  
**Related issue:** [#1450 — Tournament Leaderboard for Production Utility](https://github.com/timerloggedout-spec/termux-monorepo/issues/1450)  
**Related lane:** [System One experiment plan](SYSTEM-ONE-EXPERIMENT-PLAN.md)

## Goal

Extend the System One experiment plane into a shared evaluation harness for typed decision models, conventional text classifiers, span extractors, and decision/routing cascades. Compare candidates on the same versioned question bank; never infer quality from model category, directory inclusion, latency alone, or a successful mock response.

## Research-backed building blocks

| Building block | Reference | What it supports | Boundary |
|---|---|---|---|
| Typed decisions / System One | [TypeSafe: Jev and System One](https://typesafe.ai/blog/introducing-system-one-models-and-jev); [Jev ecosystem](https://github.com/VoltAgent/typesafe-jev-ecosystem) | Typed choice, score, and yes/no-style decision interfaces | Ecosystem pages do not prove production reliability or comparative quality |
| Generalist span extraction | [GLiNER repository](https://github.com/urchade/GLiNER), [docs](https://urchade.github.io/GLiNER/), [NAACL 2024 paper](https://aclanthology.org/2024.naacl-long.300.pdf) | Caller-defined entity types, zero-shot extraction, span-level evaluation | Extraction is not interchangeable with whole-text classification |
| Selective prediction | [The Art of Abstention (ACL 2021)](https://aclanthology.org/2021.acl-long.84/), [calibrated selective classification reference implementation](https://github.com/ajfisch/calibrated-selective-classification) | Evaluate coverage versus error when systems may abstain | Thresholds must be fit on a validation split, not the final test set |
| JSONL benchmark pattern | [ResearchRubrics](https://github.com/scaleapi/researchrubrics) | Machine-readable per-sample receipts | Adopt the pattern; do not assume its schema is a universal standard |
| Evaluation harness patterns | [HeurekaBench](https://github.com/mlbio-epfl/HeurekaBench), [OfficeComprehensionBench](https://github.com/microsoft/OfficeComprehensionBench) | Repeatable tasks, grading, artifact validation and evaluation tooling | Reuse patterns only after reviewing licenses and dependency/security posture |
| Production ML checklist | [awesome-production-machine-learning](https://github.com/EthicalML/awesome-production-machine-learning) | Discovery index for production practices | Curated list, not proof that a particular integration is production-ready |

## Registry model

Keep three identities separate:

1. **Model/capability** — what decision or extraction behavior is provided.
2. **Runtime** — where/how weights execute (Transformers, ONNX, MLX, GGUF, hosted API, etc.).
3. **Adapter** — how the harness encodes requests, validates responses, maps errors and extracts evidence.

A deployable candidate is a pinned tuple: `model_ref + runtime_ref + adapter_ref + schema_version`. A model name alone is not a reproducible deployment.

Each registry entry must declare:
- stable ID, display name, family, source URL, source type and last verification date;
- task kinds: typed choice/score/boolean, single/multi-label classification, span extraction, or cascade;
- input/output schema and label ontology;
- supported modalities and languages (use `unknown` rather than guessing);
- score semantics: raw score, ranking score, probability, or calibrated probability;
- abstention capability and threshold/calibration profile;
- license/terms, artifact digest, runtime and adapter versions;
- availability state: `VERIFIED`, `EXPERIMENTAL`, `UNAVAILABLE`, `UNVERIFIED_SOURCE`, or `REJECTED`;
- resource constraints, timeout and concurrency limits;
- test/benchmark evidence and promotion status.

Directory membership or a blog mention may add a candidate as `UNVERIFIED_SOURCE`; it must not mark it live, licensed for production, or quality-tested. Do not treat the reported “GPT-6 Luna Decisions / OpenAI Decisions API” name as verified merely because it appears in a third-party directory. Resolve primary-source identity before enabling it.

## Question bank

Canonical question bank: `tests/fixtures/classifier-question-bank.json`.

Bank rules:
- stable `question_id`, schema version, task family, language, split and immutable expected result;
- include in-domain, cross-domain, multilingual, high-cardinality, malformed, ambiguous, unsupported-task, adversarial/injection-shaped, and abstention-worthy cases;
- distinguish a wrong prediction from abstention, timeout, unavailable model, invalid schema, and adapter failure;
- use explicit acceptable labels/spans where ambiguity is legitimate;
- never place secrets or personal data in benchmark fixtures;
- hold back a test split; model selection and threshold tuning use validation only;
- every edit increments the bank version and records why examples changed.

A benchmark runner must submit the same question IDs and acceptance rules to every eligible candidate. If a model cannot support a task, record `NOT_APPLICABLE`; do not count it as a model error or silently omit it from coverage statistics.

## Parallel execution contract

Parallelism is over independent (question, candidate) jobs, bounded by per-candidate and global concurrency limits. It is not permission to fan out without quotas.

- Preserve deterministic final ordering by `question_id, candidate_id`, even if completion order differs.
- Use per-job timeout and isolated error capture; one failure must not cancel unrelated candidates.
- Separate global worker count from adapter-specific concurrency.
- Record queue time, inference latency and total latency independently.
- Retries are explicit, bounded, and recorded as attempts; never overwrite the original failure.
- Mock and fixture adapters prove wiring only. Live model quality requires real inference against labeled cases.

## Evidence receipt

JSONL is append-only canonical evidence, one receipt per (run, question, candidate, attempt). Minimum fields:

```json
{
  "schema_version": "classifier-eval.v1",
  "run_id": "stable-run-id",
  "bank_version": "classifier-bank.v1",
  "question_id": "route-billing-001",
  "candidate_id": "deterministic-baseline",
  "model_ref": "deterministic-baseline@1",
  "runtime_ref": "python-stdlib@1",
  "adapter_ref": "builtin@1",
  "status": "OK",
  "prediction": "billing",
  "scores": null,
  "score_semantics": "none",
  "abstained": false,
  "expected": "billing",
  "correct": true,
  "queue_ms": 0,
  "latency_ms": 0,
  "attempt": 1,
  "input_sha256": "sha256:...",
  "source_commit": "full-git-sha",
  "error_class": null
}
```

Use null for missing measurements, never zero. Avoid storing raw sensitive input when a digest and question ID suffice. For span extraction, store character offsets and extracted text; for typed decisions, store the typed answer and schema reference.

## Metrics and promotion

Report per task, language, split and candidate:
- exact accuracy / macro-F1 / per-class precision and recall where applicable;
- span precision/recall/F1 for extraction;
- coverage, selective risk and risk–coverage curve for abstaining models;
- calibration (Brier score, log loss and ECE only when score semantics and labels justify them);
- p50/p95 latency, throughput, timeout/error rate and cost where observable;
- unsupported-task behavior, schema validity, OOD behavior and reproducibility;
- integration outcomes for cascades, with attribution to each stage.

Do not collapse these into one winner score without publishing the formula and constraints. Correctness and safety gates precede latency optimization. Compare matched cohorts and report uncertainty; promote only after repeatable held-out results, provenance checks, security review and explicit human approval.

## Security and supply chain

- Keep API keys in secret stores; never put them in fixtures, JSONL, command output or model metadata.
- Do not expose secrets to untrusted pull-request code.
- Pin GitHub Actions by full commit SHA where feasible; review permissions and downloaded artifacts.
- Verify model/dataset digests and licenses before downloading or deploying.
- Treat model cards, directories and roundup articles as leads, not independent validation.
- Validate adapter output against closed schemas; cap request sizes and timeouts.
- System One remains decision-only: no shell, provider, branch-write, merge or secret authority.

## Implementation sequence

1. Freeze bank schema and starter fixtures; add validation tests.
2. Extend registry metadata without claiming unavailable candidates are runnable.
3. Add bounded parallel runner with deterministic receipt ordering.
4. Add candidate adapters one at a time: deterministic baseline, Laya (only after live API verification), Jev (only after provider contract verification), conventional classifier, GLiNER.
5. Add aggregate report and split-aware metrics.
6. Run live cohorts, publish artifacts, compare two or more matched cohorts.
7. Keep routing observe-only until explicit promotion criteria pass.

## Current caveats

The existing System One experiment plan already says unavailable Jev is not a model failure, raw receipts are canonical, missing evidence is null, and active routing requires multiple comparable cohorts and human promotion. Preserve these invariants. The current Jev HTTP path and Laya inference path have not been independently demonstrated as successful live inference in this lane; contract/mock tests must not be presented as model-quality evidence.


## Compute plane and code ownership

The canonical shared classifier evaluator for this lane is `scripts/classifier_eval.py`; the versioned question bank is `tests/fixtures/classifier-question-bank.json`; regression tests are in `tests/test_classifier_question_bank.py`. Keep cross-project evaluation contracts, receipts, and promotion gates here rather than silently making a product-specific CLI package the source of truth.

The System One workflow (`.github/workflows/system-one-experiments.yml`) runs on GitHub-hosted `ubuntu-latest` runners. Its unit tests, fixture smoke cohort, bounded candidate matrix, scorer, and receipt validation execute in that remote Actions job; local commands in this document are developer reproduction instructions, not the production execution plane. Outputs are uploaded as run-scoped Actions artifacts with finite retention.

**Important distinction:** a hosted runner is remote compute, but it does not automatically mean inference ran on a remote model service. The current default smoke run uses the deterministic baseline; the matrix uses the deterministic baseline, a mock adapter, and a Jev adapter that is expected to report `UNAVAILABLE` when live mode/credentials are absent. These are wiring/contract checks, not live service or model-quality evidence. Any live cohort must be a deliberate, separately permissioned workflow run with provider credentials stored as GitHub Actions secrets/environment secrets, never exposed to untrusted pull-request code. Record the provider/runtime, model revision or digest, source SHA, service region where available, timeout, concurrency, and receipt artifact for each live run.

### Tier-1 placement rule

The phrase “Tier 1” must be resolved against the repository's actual tier taxonomy; it is not inferred from a folder name or a label in a comment. Before moving or duplicating code under `deepcli/`, verify the owning package, import paths, tests, deployment consumer, and issue/PR provenance. `deepcli/` is a distinct terminal/chat application surface; it is not the canonical location for this shared evaluation harness merely because both projects use Python. If Tier-1 classifier logic is genuinely a runtime dependency of DeepCLI, keep a thin, tested adapter there and retain the shared schema, question bank, runner, and evidence contract in the System One evaluation plane. Avoid copying the implementation into both places; define one owner and test the integration boundary.

## Executable candidate-matrix mode

The evaluator now supports a bounded cross-product of question-bank items and candidate adapters. The default remains the deterministic baseline for backward-compatible smoke checks. To compare adapters against the same bank, run:

```bash
python scripts/classifier_eval.py \
  --bank tests/fixtures/classifier-question-bank.json \
  --candidates deterministic-baseline laya-mock jev \
  --workers 8 --per-candidate-workers 2 \
  --run-id local-matrix-001 \
  --output artifacts/system-one/classifier-matrix.jsonl
python scripts/eval_tournament.py \
  artifacts/system-one/classifier-matrix.jsonl \
  --output artifacts/system-one/classifier-matrix-report.json
```

Add `laya-live` and `--live` only for an intentional live run. The Jev adapter is also attempted only with `--live`; without it, eligible questions are recorded as `UNAVAILABLE`. The runner never treats mock output or unavailable adapters as correctness evidence.

Concurrency contract:
- global jobs are bounded by `--workers` (1–64);
- each candidate has its own semaphore bounded by `--per-candidate-workers` (1–16);
- jobs are submitted concurrently but receipts are emitted in stable question-bank order, then candidate argument order;
- `NOT_APPLICABLE`, `UNAVAILABLE`, `MOCK`, `ERROR`, and `OK` remain distinct states;
- only `OK` predictions are marked with a correctness value; other states use null rather than zero or false;
- candidate compatibility currently maps text classification and typed Choice questions. Multilabel and span-extraction tasks are explicitly `NOT_APPLICABLE` for these Choice-only adapters rather than silently mis-scored.

This is a bounded adapter comparison surface, not a claim that every registered ecosystem model is integrated. Add new adapters behind the same receipt contract, verify their primary API/runtime, and use the same bank version and held-out split before comparing quality.
