# Kubeflow (Pipelines focus) — Validation Record

Research for building our own lab platform. Kubeflow is the platform tier:
its cluster side was expected to be infra-bounded in this VM, so the
SDK / compile surface is what this record validates firsthand. Everything
about the cluster platform itself is filed under CLAIMED, not verified.

## Environment and versions (recorded before any verdict)

| Fact | Value |
|---|---|
| Host | Linux x86_64, Python 3.12.3, 7.7 GB RAM |
| Isolation | dedicated venv at `~/workspace/lab-platforms/kubeflow/venv` |
| Docker | **absent** on this host (`which docker` → nothing) |
| Kubernetes cluster | none |
| `kfp` | **2.18.0** |
| `kfp-pipeline-spec` / `kfp-server-api` | 2.18.0 / 2.18.0 |
| `kubernetes` client pulled in by SDK | 30.1.0 |
| Compiled IR schemaVersion | **2.1.0** |
| Mode | local-only; no server left running; 0 stray processes at end |

Files: `pipeline.py` (authored pipeline), `lab_pipeline.yaml` (compiled IR,
16,125 bytes), `verify_ir.py` (IR assertions), `run_local.py` (local run),
`readback_local.py` (independent read-back), `run_local_full.log`.

## Step verdicts

### 1. Install the Pipelines SDK — PASS

```
Successfully installed ... kfp-2.18.0 kfp-pipeline-spec-2.18.0
kfp-server-api-2.18.0 kubernetes-30.1.0 protobuf-6.33.6 ...
kfp 2.18.0
```

### 2. Author a real pipeline and compile it to IR — PASS

Pipeline `lab-train-eval` (in `pipeline.py`), five components, all stdlib-only
so local execution runs the exact code the IR describes:

```
load_data ──Dataset──► train_model ──Model──► evaluate_model ──Metrics
    │                                              │ accuracy (parameter)
    └──Dataset──► data_profile ──Metrics           ▼
                                     Condition(accuracy > threshold)
                                          └──► promote_model ──Model
```

`train_model` and `data_profile` are parallel branches off the same Dataset
artifact. Compile output:

```
DeprecationWarning: dsl.Condition is deprecated. Please use dsl.If instead.
compiled -> lab_pipeline.yaml   (16,125 bytes)
```

The deprecation warning on first contact is itself evidence: the authoring
surface churns inside a single major version (see Research Note).

### 3. Parse the compiled IR back and assert the graph — PASS (20/20)

`verify_ir.py` loads `lab_pipeline.yaml` and asserts structure, not vibes:

```
components in IR: ['comp-condition-1', 'comp-data-profile', 'comp-evaluate-model',
                   'comp-load-data', 'comp-promote-model', 'comp-train-model']
schemaVersion   : 2.1.0
PASS  load_data emits system.Dataset
PASS  train_model: Dataset in / Model out
PASS  data_profile emits system.Metrics
PASS  evaluate_model: Model in / Metrics out
PASS  pipeline parameters present: ['accuracy_threshold', 'seed']
      param types: {'accuracy_threshold': 'NUMBER_DOUBLE', 'seed': 'NUMBER_INTEGER'}
PASS  evaluate-model.model wired from train-model (taskOutputArtifact ref)
PASS  evaluate-model.dataset wired from load-data
PASS  train-model.dataset wired from load-data
PASS  data-profile.dataset wired from load-data (parallel branch source)
PASS  evaluate-model depends on train-model; data-profile depends only on load-data
PASS  exactly one conditional task group; condition string:
      inputs.parameter_values['pipelinechannel--evaluate-model-accuracy']
        > inputs.parameter_values['pipelinechannel--accuracy_threshold']
PASS  promote-model nested inside condition-1
PASS  5 executors in deploymentSpec; sample container image: python:3.12-slim
VERDICT: PASS
```

Two IR facts worth their own line:

- Every compiled task carries `"cachingOptions": {"enableCache": true}` — result
  caching is **on by default** in the IR, a hidden default a run can silently
  inherit.
- Each executor's container command self-bootstraps: it pip-installs
  `kfp==2.18.0 --no-deps` at container start, then runs the component's
  **source text** (the function body is embedded verbatim in the IR as a
  string) via `--function_to_execute train_model`. Components are
  source-extracted, not packaged.

### 4. Local execution surface — PARTIAL (core DAG PASS, conditional FAIL)

`kfp.local` with `SubprocessRunner`, `pipeline_root=./local_outputs`.

What genuinely ran (two separate runs, same result):

```
Task 'load-data'       finished with status SUCCESS
Task 'train-model'     finished with status SUCCESS
Task 'evaluate-model'  finished with status SUCCESS
Task 'data-profile'    finished with status SUCCESS
Pipeline 'lab-train-eval' finished with status SUCCESS
```

Independent read-back (`readback_local.py`, separate process, stored parts
only) — the reproducibility check closes **exactly**:

```
accuracy recorded by evaluate-model: 0.995
train_accuracy recorded by train-model: 0.995
re-derived accuracy from stored Dataset+Model artifacts: 0.995 (199/200)
MATCHES recorded accuracy: True
tasks with stored parts: ['data-profile', 'evaluate-model', 'load-data', 'train-model']
```

Where it stops — the conditional branch:

```
accuracy = 0.995  >  threshold 0.8   → condition is TRUE
promote-model stored parts present: False
condition group stored parts present: False
grep of the full run log for "condition|promote|skip": 0 hits
```

The local runner **silently drops the entire condition group**: the gated
task never executes, is never reported as skipped, and the pipeline still
reports SUCCESS. Local execution is therefore **not semantics-complete**
against the IR it claims to run — a whole branch of the graph can vanish
without a trace in the verdict.

Not established locally:

- `DockerRunner` — untestable, no Docker on this host.
- Cluster submission (`Client.create_run_from_pipeline_func` against a KFP
  backend / Argo) — no cluster; the entire control plane is out of reach here.

### 5. Wider Kubeflow surface — CLAIMED (docs/architecture level, unverified)

Read from the project's architecture material and distribution docs; none of
this was executed and none of it should be quoted as verified.

| Component | Claimed role |
|---|---|
| KFP backend | API server + persistence agent over **Argo Workflows**; run/artifact metadata in **ML Metadata (MLMD)**; artifacts in S3/MinIO object store; web UI for runs, caching, recurring runs |
| Notebooks / Workspaces | JupyterLab / VS Code / RStudio servers as per-user namespaced pods with PVC-backed home directories, behind the central dashboard |
| Katib | Hyperparameter tuning / AutoML: Experiment & Trial controllers, algorithms from random/grid to Bayesian optimization, TPE, Hyperband; recently extended to LLM fine-tuning |
| Trainer v2 (ex-Training Operator) | Distributed training behind a **unified `TrainJob` API** (replacing per-framework `PyTorchJob`/`TFJob`/… CRDs) with reusable `TrainingRuntime`/`ClusterTrainingRuntime`; lowers to JobSet; queueing delegated to external **Kueue** |
| KServe | Model serving (`InferenceService`: predictors, transformers, explainers, canary, autoscaling); graduated out of Kubeflow into a standalone CNCF incubating project, still integrated, incl. with Model Registry |
| Model Registry ("Kubeflow Hub") | Versioned model metadata store linking a model version back to the run that produced it; dedicated UI; feeds serving |
| Spark Operator | Declarative Spark applications on Kubernetes for data prep / feature engineering |
| Platform layer | Central Dashboard, Profiles + KFAM multi-tenancy (namespace per profile), **Dex** OIDC auth, Istio in full distributions. One distribution's component table alone lists ~a dozen controllers plus Dex — the platform's operational weight is architectural, not incidental |
| Positioning | Kubeflow 1.11 (Dec 2025) rebranded the platform as the "Kubeflow AI Reference Platform" with a GenAI / distributed-LLM-training focus |

## Verified vs claimed vs unestablished — summary

- **Verified firsthand:** SDK install (kfp 2.18.0); authoring → compile to
  IR 2.1.0; the IR contains the full typed graph (20/20 assertions); local
  subprocess execution of the unconditional DAG, with an exact artifact
  read-back; the local runner's silent conditional drop.
- **Claimed (documentation):** everything in §5 — the whole platform tier:
  backend, notebooks, Katib, Trainer, KServe, registry, multi-tenancy, auth.
- **Unestablished:** Docker-based local execution; any cluster behavior;
  caching semantics in practice; whether the cluster engine honors the
  trigger policy as compiled (the IR says it should; nothing here ran it).

## Research note — what we take, what we deliberately do not copy

### TAKE

1. **Compile-to-IR as the center of the design.** Authoring (a Python DSL)
   is fully separated from execution by a static, portable artifact
   (protobuf-schema YAML, schemaVersion 2.1.0) that a third party can parse
   and *assert properties against* — we verified 20 structural claims about
   the graph with zero infrastructure. The pipeline definition becomes an
   auditable research artifact in its own right, diffable and archivable
   like data.
2. **Typed artifact edges with explicit producer→consumer wiring.** The IR
   names every edge (`taskOutputArtifact: {producerTask, outputArtifactKey}`)
   and types it (`system.Dataset` / `system.Model` / `system.Metrics`), so
   the provenance graph is *in* the artifact, not reconstructed after the
   fact from logs.
3. **Gates as compiled data, not code.** The accuracy gate is a string
   expression in `triggerPolicy.condition` over named task outputs —
   inspectable before anything runs, and in principle portable across
   executors.
4. **Metrics and artifact metadata as first-class stored parts.** Dataset
   metadata (schema, n_rows), Metrics values, and per-task
   `executor_output.json` are all persisted in the run tree — which is what
   made an exact independent read-back (0.995 re-derived = 0.995 recorded)
   possible at all.
5. **Typed pipeline parameters with defaults, declared in the IR**
   (`NUMBER_DOUBLE`, `NUMBER_INTEGER`) — runs are reproducible from the IR
   plus a parameter assignment.

### DO NOT COPY

1. **"SUCCESS" that can hide a missing branch.** The local runner dropped
   the condition group with the gate condition *true*, printed nothing, and
   still returned pipeline SUCCESS. Any executor of ours must either run
   the full compiled semantics or fail loudly / mark unsupported constructs
   explicitly. A verdict that omits part of the graph is worse than a
   failure — it manufactures false evidence. (This is the single sharpest
   finding of this validation.)
2. **Nominal typing mistaken for enforcement.** `system.Model` is a schema
   *label*: our "model" is a JSON file of two centroids and nothing anywhere
   validated it against any model schema. Typed edges earn their keep for
   wiring and provenance; they must not be presented as conformance.
   Our build should add an actual validation hook where a type makes a
   promise.
3. **Source-extracted components that self-bootstrap.** The IR embeds each
   function's source text and every container re-installs the pinned SDK
   (`kfp==2.18.0 --no-deps`) before running it. That couples correctness to
   source inspection (closures, local helpers, module state all break),
   bakes the SDK version into every executor, and makes environments
   rebuild per task. Prefer explicit, packaged entrypoints with declared
   environments.
4. **Silent defaults in the compiled artifact.** `enableCache: true` rides
   along in every task unless the author opts out — a stale-result reuse
   hazard that is invisible at the DSL level. Defaults with evidentiary
   consequences belong in the author's face, not in the compiler's.
5. **Platform weight as the price of the pipeline model.** The validatable
   core here is ~a compiler and a schema; the platform around it (per the
   claimed architecture) is a fleet of controllers plus Argo, MLMD, an
   object store, Dex, Istio, and namespace-level multi-tenancy machinery.
   That weight buys multi-user GPU-platform operations; a lab platform
   should take the IR/graph/metadata ideas and refuse the control plane
   until multi-tenancy is a real requirement.
6. **Authoring-surface churn.** `dsl.Condition` was deprecated in favor of
   `dsl.If` within the same major SDK line (warning at compile time, kfp
   2.18.0). If we borrow DSL ideas, the DSL must be versioned as carefully
   as the IR — the IR's stability (a numbered schemaVersion) is the part
   worth imitating.

### Gaps hit, stated as requirements for our own build

- A local/dev executor that is semantics-faithful to the compiled graph —
  conditionals included — or that refuses, by name, the constructs it
  cannot run.
- Run verdicts that enumerate every task in the graph with an explicit
  state (ran / skipped-by-gate / not-supported), so a missing branch is
  itself a reported fact.
- Artifact-type validation hooks at edge boundaries, so a type label can
  optionally carry a checkable promise.
- Cache behavior declared in the pipeline definition and echoed in the run
  record, never inherited silently from compiler defaults.
