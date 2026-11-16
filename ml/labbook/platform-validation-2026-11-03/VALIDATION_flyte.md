# Flyte — hands-on validation record

Research for building our own platform, not an adoption decision. Method per
`lab_platform_validation` skill: isolated install → real workload → independent
read-back in a separate process → verdicts with evidence.

## Environment (recorded before verdicts)

- flytekit **1.16.31** · flyteidl **1.16.8** · Python **3.12.3** (venv, isolated under `~/workspace/lab-platforms/flyte/venv`, 512 MB)
- scikit-learn 1.9.1 · pandas 3.1.0 · numpy 2.5.4
- Mode: **local execution only** (in-process engine). No server stood up; nothing left running (verified: no flyte processes, `/tmp/flyte*` scratch dirs were empty shells and were removed).
- Cluster tooling present: **none** — `docker`, `kubectl`, `kind`, `minikube`, `flytectl`, `helm` all MISSING from PATH.

## Workload

`work/pipeline.py` — a 5-fold cross-validation workflow with typed artifacts
crossing every data boundary:

```
make_dataset(seed, n_rows) -> FlyteFile            (synthetic classification CSV)
fanout(dataset, n_folds, seed) -> collections      (see Step 3 failure)
map_task(train_fold)(dataset, fold_idx, n_folds, seed) -> list[float]
finalize(dataset, fold_scores, seed) -> (cv_mean, FlyteFile model.pkl, FlyteFile report.json)
```

## Per-step verdicts

### Step 1 — Install flytekit: PASS

```
Successfully installed ... flyteidl-1.16.8 flytekit-1.16.31 ...
flytekit 1.16.31
python 3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]
```

Note: a local-only install pulls the full cloud plugin surface by default
(s3fs, gcsfs, adlfs, azure-storage-blob, azure-identity, google-cloud-storage…).

### Step 2 — First local run (naive map_task): FAIL — type engine, before compute

Passing the single `dataset: FlyteFile` as a constant co-input to `map_task`
alongside the mapped `fold_idx: list[int]` failed at input conversion:

```
TypeTransformerFailedError: Error encountered while converting inputs of
'pipeline.map_train_fold_...-arraynode':
  Error converting input 'dataset':
Literal value: scalar { blob { ... uri: ".../run_outputs/dataset.csv" } }
Expected Python type: typing.List[flytekit.types.file.file.FlyteFile]
Exception: The expected python type is 'typing.List[FlyteFile]' but the
received Flyte literal value is not a collection
```

So: in flytekit 1.16.31 local execution, **map_task does not broadcast scalar
co-inputs** — the ArrayNode expects *every* input as a collection and tries to
read the FlyteFile scalar as `List[FlyteFile]`. The failure is at least
fail-fast and pre-compute, and the error prints the offending literal.

The decisive exception was also buried: it surfaced repeatedly as asyncio
`Task exception was never retrieved` plus an unrelated
`ImportError: sys.meta_path is None` from the rich logging handler during
interpreter shutdown.

A first repair attempt with bare `list` annotations failed too, at interface
compile time:

```
ValueError: Type of Generic List type is not supported, Only generic
univariate typing.List[T] type is supported.
```

### Step 3 — Fix: fan-out task materializes every map input as a collection: PASS

Added `fanout` returning `([dataset]*n, [0..n), [n_folds]*n, [seed]*n)` with
fully parameterized annotations. Re-run (exit 0):

```
CV_MEAN 0.6
FOLD_SCORES [0.55, 0.575, 0.6125, 0.625, 0.6375]
MODEL_PATH  .../run_outputs/model.pkl
REPORT_PATH .../run_outputs/report.json
```

Artifacts materialized on disk: `dataset.csv` (63,406 B), `model.pkl` (769 B),
`report.json`, plus the runner's `run_manifest.json`.

### Step 4 — Independent read-back in a separate process: PASS, exact

`work/readback.py` (fresh process; consumes only the manifest + stored
artifacts, never the workflow) verified:

```
A report-mean check:   recomputed=0.6    stored=0.6    exact=True
B manifest-mean check: recomputed=0.6    stored=0.6    exact=True
D fold-score agreement report-vs-manifest: True
C model re-score:      recomputed=0.6375 stored=0.6375 match=True
READBACK PASS
```

Check C is the substantive one: the stored `model.pkl` was unpickled cold and
re-scored against the dataset **regenerated from the seed recorded in the
report** — it reproduces the workflow's full-train accuracy exactly (0.6375).
The FlyteFile artifacts are real, durable files any process can open.

### Step 5 — Queryable execution/lineage store in local mode: NONE — finding, not failure

Verified firsthand:

- No execution metadata is registered anywhere: no `~/.flyte` directory, the
  `/tmp/flyte*` per-task scratch dirs are **empty** (0 bytes), and nothing
  listens on FlyteAdmin's ports (30081 / 8089 / 31080 all closed).
- Outputs exist after the process exits **only** as (a) the Python values the
  caller received and (b) files the task code itself wrote. `FlyteFile` in
  local mode is a path passthrough — the dataset URI in the Step-2 error is a
  plain local path; there is no content hash, no dedup, no registry.
- `FlyteRemote` therefore has nothing local to query: execution history,
  per-task lineage, and input/output records live only in-process, in the
  compiled flyteidl representation, for the lifetime of the run.

### Step 6 — Cluster-backed platform tier (FlyteAdmin/Propeller on Kubernetes): UNESTABLISHED — infra-bounded

Exact blockers in this VM: no Docker daemon or CLI (the `flytectl demo`
sandbox is Docker-based), no Kubernetes (`kubectl`/`kind`/`minikube`/`helm`
absent), `flytectl` not installed. A backend additionally needs FlyteAdmin +
Propeller + Postgres + a blob store. Not attempted, per instructions — the
backend's scheduling, retries, and UI lineage remain **claimed, not verified**.

## Verified / claimed / unestablished

- **Verified firsthand:** install + versions; local end-to-end execution of a
  typed, map-parallel workflow; FlyteFile artifacts materialize as real files;
  stored model + report re-derive headline numbers exactly from a cold
  process; map_task's all-collections input contract (by failure); bare-`list`
  annotation rejection; local mode keeps **no** queryable execution store.
- **Claimed by documentation only:** the same workflow definition deploys
  unchanged to the Kubernetes backend; backend provides execution lineage,
  caching, retries, and versioning.
- **Unestablished:** everything about the cluster tier (Step 6 blockers);
  task caching and data-lineage behavior under the backend.

## Research note — for our own build

### Take

- **Typed contracts enforced at every boundary, failing before compute.** The
  type engine caught a real wiring error at literal-conversion time and
  printed the offending value next to the expected type. Interfaces compile to
  a language-neutral protobuf IDL (flyteidl), so the DAG spec exists
  independently of the Python that authored it.
- **Files as first-class typed artifacts.** `FlyteFile`/`FlyteDirectory` make
  "a model file", "a dataset CSV" contract objects, not path strings smuggled
  through parameters — and because they materialize as ordinary files, an
  unrelated process (our read-back) could consume them with zero Flyte code.
- **A declarative parallel primitive with collection fan-in.** `map_task`
  over folds returning `list[float]` straight into an aggregator is the right
  shape for experiment sweeps; the workflow stays a pure composition of tasks.

### Deliberately do not copy

- **Map inputs that refuse scalars.** Requiring every co-input as a collection
  forced a boilerplate fan-out task and N references to one file. Broadcast
  constants natively.
- **Local-mode amnesia.** A science lab's run record *is* the product; an
  engine that forgets every execution when the process exits fails the core
  use case. Persist an execution ledger (inputs, outputs, hashes, code
  version) even — especially — in local mode.
- **Path-passthrough artifacts.** Local FlyteFiles carry no content address,
  checksum, or dedup (contrast the content-addressed store validated in the
  Metaflow wave). Hash-address artifacts and verify on read.
- **Diagnostics buried in noise.** One decisive exception arrived wrapped in
  repeated asyncio "exception was never retrieved" reports and an unrelated
  logging ImportError at shutdown. One primary error, cleanly presented.
- **Spelling-level type traps.** `tuple[...]` returns accepted, bare `list`
  rejected, `typing.List` vs PEP-585 behavior split across the surface — the
  failure modes are orthographic, and every author pays the tax. Accept and
  normalize; when rejecting, name the fix.
- **Wholesale plugin weight by default.** ~512 MB venv with three clouds' SDKs
  for a laptop run. Optional integrations should be opt-in installs.

### Gaps hit → candidate requirements for the own-build

1. Persistent, queryable local execution ledger as a first-class artifact.
2. Scalar broadcast in parallel map primitives.
3. Content-addressed artifact store with read-back checksum verification.
4. Single-primary-exception diagnostics (no shutdown noise, no duplicates).
