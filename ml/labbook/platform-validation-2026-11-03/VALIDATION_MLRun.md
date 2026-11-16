# MLRun — hands-on validation

**Frame:** research for building our own platform, not adoption. Method: `lab_platform_validation` skill — isolated install, real workload, independent read-back in a separate process, one headline number re-derived from stored parts.

## Environment (exact)

| Fact | Value |
|---|---|
| Host | Linux x86_64, 4 CPU, 7.7 GiB RAM, no docker / kubectl / kind / helm (verified: `which` returns nothing for all four) |
| Host Python | 3.12.3 (only interpreter preinstalled) |
| Runtime used | CPython **3.11.18** (uv python-build-standalone, installed into the workspace) |
| Client venv | `~/workspace/lab-platforms/mlrun/venv` (py3.11, isolated) |
| **mlrun** | **1.12.1** |
| Key deps (client) | numpy 1.26.4 · pandas 2.1.4 · storey 1.12.6 · nuclio-sdk 0.6.3 · pydantic 2.14.2 |
| Mode | fully local, loopback only, no API server for the core run (see §4) |

## Step verdicts

### 1. Install — PASS, with a platform constraint found firsthand

- `pip install mlrun` on the host Python 3.12.3 resolves only **mlrun 1.5.2** (every release ≥1.6 declares `Requires-Python <3.12`; 1.10.x: `>=3.9,<3.12`, 1.11.x: `>=3.11,<3.12`), and 1.5.2 then fails to build: it pins `numpy<1.23`, whose sdist cannot build on 3.12 (`ModuleNotFoundError: No module named 'distutils'`).
- Route that works: standalone CPython 3.11.18 via uv → `pip install mlrun` → **mlrun 1.12.1**, imports cleanly.
- Verdict: current MLRun simply does not support Python 3.12. Any environment pinned to 3.12 is capped at a 2023-era release that no longer builds.

### 2. Project + function + local run — PASS

- Project `lab-mlrun` created from `./proj` (`project.yaml` on disk: `kind: project`, `desired_state: online`).
- Function `trainer` (kind `job`) from `proj/funcs.py`: closed-form least-squares fit on synthetic data (n=200, true slope 2.5, intercept 1.0, seed 42), logging a dataset artifact, a model artifact, and scalar results.
- Local run (`fn.run(local=True)`) → state **completed**, UID `839c453a21814911a337e8f529dbd764`:

```
Run execution finished: {"name":"train-run-1","status":"completed"}
RUN_RESULTS: {
  "slope": 2.532960458215284,
  "intercept": 0.8454206917321301,
  "mse": 0.24895213767453064,
  "rmse": 0.4989510373518935, ... }
```

- Artifact **files** on disk under `train-run-1/0/`: `dataset.parquet` (200×2), `model/model.txt`, `model/model_spec.yaml` (spec carries producer URI `lab-mlrun/<uid>`, metrics `{mse: 0.24895213767453064}`, target_path).
- Two defects hit and worked around (both are findings, §6):
  - `context.log_artifact(key, df=...)` is dead in 1.12 — `Artifact.__init__() got an unexpected keyword argument 'df'`; the run silently finished with status `created` and null results. `log_dataset()` is the live API.
  - The returned run object's `.status.artifacts` property raises `AttributeError: 'NoneType' object has no attribute 'to_dict'` (a `None` entry in the list), and `run.outputs` **polls the run DB forever** in client-only mode (log line `run train-run-1 is not completed yet, waiting for it to complete` repeating every ~3 s until killed).

### 3. Separate-process read-back — SPLIT verdict

Leg 1 — MLRun's run-DB API (what a second process is offered): **FAIL by design in client-only mode.**

```
run db class: NopDB
get_run: RAISED AttributeError: 'NopDB' object has no attribute 'get_run'
list_runs: -> RunList len=0
list_artifacts: -> ArtifactList len=0
```

The client wheel ships exactly two run-DB implementations (`mlrun/db/`: `httpdb.py`, `nopdb.py`). With no API server, the DB is `NopDB`: runs execute and artifact files land on disk, but **no run record is persisted anywhere a second process can query** — the run dict's own `status.artifacts` list is empty (`[]`) even though artifact files + spec YAMLs exist. Every local execution starts with the warning pair `Could not detect path to API server` / `MLRUN_DBPATH is misconfigured`.

Leg 2 — MLRun's datastore API over the artifact files: **PASS, exact.**

```
dataset read via get_dataitem: (200, 2) ['x', 'y']
re-derived: slope=2.532960458215284 intercept=0.8454206917321301 mse=0.24895213767453064
logged:     {'slope': 2.532960458215284, 'intercept': 0.8454206917321301, 'mse': 0.24895213767453064}
MATCH slope: True
MATCH intercept: True
MATCH mse: True
model artifact body: slope=2.532960458215284 | intercept=0.8454206917321301
```

A separate process read `dataset.parquet` via `mlrun.get_dataitem(...).as_df()`, refit least squares, and reproduced the logged slope/intercept/MSE **bit-for-bit**. The seeded training run is also exactly reproducible across executions (two runs → identical floats). So: the *data* layer is a real, queryable store; the *run-record* layer is server-only.

### 4. API server from source — PASS (hand-assembled; not the supported deployment)

The wheel ships no server, but the v1.12.1 source tree does (`server/py`), and it can be stood up on loopback with SQLite:

- Dependency archaeology required: the client's package set is not enough. The import chain demanded, in order: `humanfriendly`, `timelength`, `httpx`, `igz-mgmt` 0.4.2, `iguazio` 0.2.9 (both vendor SDKs, imported by the OSS server's main path), `protobuf`/`grpcio`, `kafka-python`, `apscheduler`, the OpenTelemetry exporter family, `sqlalchemy-utils` — and then a hard version wall: current fastapi (0.162.0) refuses MLRun's pydantic-v1 response models (`PydanticV1NotSupportedError`). The authoritative set is buried in `dockerfiles/mlrun-api/locked-requirements.txt`; installing it (fastapi **0.125.0**, SQLAlchemy 2.0.51, uvicorn 0.34.3, alembic 1.19.1) plus aligning `opentelemetry-exporter-otlp==1.44.0` made the app import.
- Launch: `uvicorn services.api.daemon:app --factory` with `MLRUN_HTTPDB__DSN=sqlite:///<workspace>/api_db.sqlite`. Result: `GET /api/v1/healthz` → **200**; `GET /api/v1/client-spec` → `{"version": "1.12.1", ...}`.
- Full round trip against it (`MLRUN_DBPATH=http://127.0.0.1:8080`, run UID `c1487e5149cc4527a0047994d0a748fc`): the run completed **and this time the record carried its artifacts** (`RUN_ARTIFACT_KEYS_RAW: ['dataset', 'model']` — contrast §3/NopDB's `[]`). A separate process then read it back through `HTTPRunDB`:

```
run db class: HTTPRunDB
RUN state: completed
RUN results: {'slope': 2.532960458215284, 'intercept': 0.8454206917321301, 'mse': 0.24895213767453064, ...}
ARTIFACTS: [('model', 'model'), ('dataset', 'dataset')]
MSE from server record: 0.24895213767453064
MATCH mse: True
```

- Durability proven: the server was killed and relaunched against the same SQLite file; the read-back still returned the run and artifacts exactly (exit 0). Server shut down after the test; nothing left running.
- Boundary, stated plainly: this is a hand-assembled from-source server. The supported CE deployment is the `mlrun-api` container image / helm chart — **not** exercised here (no docker/Kubernetes). The HTTP DB's method surface also differs from intuition (`read_run`, not `get_run` — `get_run` doesn't exist on either DB class).

### 5. Serving — PASS at mock level; live endpoint is the boundary

Two graph shapes probed with `fn.to_mock_server()` (in-process `GraphServer`, no endpoint stood up):

- **flow topology + custom storey step:** graph constructs (`steps: ['score']`, class `LinearScorer`), mock server invokes it. Contract found firsthand: storey steps receive the **raw request-body dict**, not a nuclio Event (first attempt died on `'dict' object has no attribute 'body'`). After fixing the step, the mock `test("/", {"x": 4.0})` returns only `{'id': ...}` — the flow topology gives no synchronous response body through the mock; the scored payload is not returned to the caller.
- **router topology + `V2ModelServer` (canonical path): PASS, exact.** `LinRegModel.load()` pulled its coefficients from the training run's actual model artifact via `get_model(suffix=".txt")` on `train-run-1/0/model`; mock infer:

```
model lin was loaded
infer resp: {'id': '21699a8a...', 'model_name': 'lin',
             'outputs': {'outputs': [10.977262524593266, 0.8454206917321301]}, ...}
expected:   [10.977262524593266, 0.8454206917321301]
MATCH outputs: True
```

(x=4.0 → 10.977262524593266, x=0.0 → the intercept itself.) Note the double wrap: a `predict()` returning `{"outputs": [...]}` gets wrapped again by the V2 layer (`outputs.outputs`). Also in 1.12: topology `"sync"` is rejected (`unsupported topology sync, use 'router' or 'flow'`), `add_model` lives on the function not the router step, and mock-server threads are non-daemon — the probe script must exit explicitly.
- **Where local serving stops:** everything above is the in-process mock. A live HTTP endpoint requires deploying the serving function as a nuclio function (docker/Kubernetes) — **UNESTABLISHED here** (no docker, no cluster).

### 6. Full platform (Iguazio / Kubernetes) — UNESTABLISHED, infra-bounded

Exact blockers, all verified in this environment: no docker, no kubectl/kind/helm; the client wheel contains no server code (server lives in the repo's `server/py` tree and ships as the `mlrun-api` container image; there is **no `mlrun-api` distribution on PyPI** — `pip index versions mlrun-api` → `No matching distribution found`). §4 shows the server *can* be hand-run from source, but the platform tier proper — run submission kinds beyond local (`job` on k8s, `spark`, `dask`, nuclio serving deployment, KFP pipelines; the `mlrun-pipelines-kfp-*` adapters are installed but have nothing to run against) and every Iguazio-integrated surface — requires Kubernetes/docker that does not exist here.

## Verified / claimed / unestablished

- **Verified firsthand:** install + version constraint; project/function/local-run mechanics; artifact files + spec YAMLs on disk; exact re-derivation from stored artifacts in a second process; seeded-run reproducibility; router+V2 mock serving with artifact-loaded coefficients, exact outputs; NopDB as the client-only run store; the API server run from source on loopback+SQLite, incl. cross-process run/artifact read-back through HTTPRunDB with exact values and durability across a server restart; the API-drift defects in §2/§5.
- **Claimed by documentation only:** everything past the mock — nuclio deployment, model monitoring, feature store serving, pipelines, alerts, the Iguazio-integrated tiers; the supported (container/helm) CE deployment path.
- **Unestablished:** live HTTP serving endpoint; any Kubernetes runtime kind; the platform tier of §6.

## Research note — MLRun's model, and what our own build does with it

**The model, as observed:** the **function is the unit of everything** — one code artifact (file + handler + kind + image) is what gets run as a job, deployed as a service, or scheduled; a **project** is the namespace that owns functions, runs, and artifacts on disk (`project.yaml` + per-run output trees); an **artifact store** of typed objects (dataset/model/chart), each with a spec YAML carrying producer run URI, hash, metrics, and target path; **serving graphs** compose storey steps or V2 model servers behind a router, with models loaded *from artifacts* at startup. The research-to-production story is genuinely one line: the same function object and the same artifact the training run logged are what the serving layer loads.

| TAKE for our own build | Evidence |
|---|---|
| Function-as-unit: one code+handler+kind descriptor for batch and serving alike | `set_function(kind="job")` and `kind="serving"` over near-identical source files; both executed locally |
| Artifact spec sidecars (producer URI, hash, metrics, target path in a YAML next to the data) | `model_spec.yaml` let a second process — and the serving layer — trust and load the artifact without any DB |
| Load-serving-from-artifact as the default contract (`get_model()` in `load()`) | serving probe loaded coefficients from the training run's artifact, zero hand-copying of numbers into serving code (the flow-step probe, which did hand-copy them, is the anti-pattern) |
| Datastore read API (`get_dataitem().as_df()`) as the cross-process contract | exact float-for-float re-derivation in a separate process |
| Seeded determinism expectations: same seed → identical floats across runs | two executions, identical results to the last bit |

| Deliberately NOT copy | Evidence |
|---|---|
| A run-record layer that silently evaporates without a server (NopDB) | local run "completed" while `list_runs` in any other process returns 0; the failure is a *warning at startup*, not an error at log time |
| Accessors that poll-forever against a missing DB | `run.outputs` looped `waiting for it to complete` every ~3 s indefinitely |
| Silent-swallow execution errors | handler exception → run finished with status `created`, results `null`; the actual error (`log_artifact df=`) appeared once, mid-log |
| Returned objects whose own properties crash | `run.status.artifacts` → `AttributeError` on a `None` entry; run dict's artifact list empty while artifact files exist |
| API drift without deprecation signals (`log_artifact(df=)`, topology `"sync"`, `add_model` placement) | each cost a failed run/probe; error messages only surface at execution time |
| The Python-version ceiling as a deployment assumption (<3.12 while the world ships 3.12+) | §1: current release uninstallable on the host interpreter |
| Server as a container-image-only artifact: its dependency lock buried in a dockerfile, the OSS server's import path pulling vendor SDKs (`igz_mgmt`, `iguazio`), and server/client version coupling tight enough that a current fastapi breaks it | §4: ~12 extra packages + a locked-requirements excavation to import the app; `PydanticV1NotSupportedError` on fastapi 0.162 |

**Gap named as our requirement:** a lab platform needs the run record to be *at least* as durable as its artifact files. MLRun inverts this locally — artifacts persist, records don't, until you hand-assemble a server whose supported form is a container image. §4 proves the architecture *allows* a SQLite-backed local server behind the identical client API; our build should ship exactly that as a first-class, documented local mode, so "run it locally, query it tomorrow from another process" is the default, not an excavation.
