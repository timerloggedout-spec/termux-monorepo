# ClearML — Hands-on Validation Record

**Purpose:** research for building our own lab platform, not adoption.
**Environment:** Linux x86_64 VM · Python 3.12.3 · isolated venv (`~/workspace/lab-platforms/clearml/venv`) · **local-only** (offline mode; no account, no cloud, no server) · nothing left running.
**Version under test:** ClearML Python SDK **2.1.12** (`pip install clearml`, clean install, 24 packages).

## Verdict summary

| Step | Verdict |
|---|---|
| SDK install | **PASS** |
| Local/offline operation mode exists and works | **PASS** |
| Experiment: task init, parameters, scalars, single values, artifacts | **PASS** |
| Independent read-back + exact re-derivation + artifact reproduction | **PASS** |
| Server-backed API (query/read-back against a backend) | **UNESTABLISHED — infra-blocked** (no Docker in this VM) |
| Agents/queues, pipelines against a backend, datasets, serving | **UNESTABLISHED** (server required) |

## Step evidence

**1. Install — PASS**

```
Successfully installed ... clearml-2.1.12 ...
$ python -c "import clearml; print(clearml.__version__)"
2.1.12
```

**2. Server feasibility check — BLOCKED BY INFRA, exact blocker recorded**

```
$ docker info
/bin/bash: line 1: docker: command not found
```

ClearML Server is a Docker Compose stack; with no Docker runtime in this VM it cannot stand up here. Per the brief, this was recorded, not fought. All SDK-provable surface was validated via the supported offline mode instead.

**3. Offline experiment — PASS** (`experiment.py`, run with `CLEARML_OFFLINE_MODE=1`)

```
ClearML running in offline mode, session stored in .../home/.clearml/cache/offline/offline-d35a254544a940b1b3ad256dd87a1f7a
No repository found, storing script code instead
linear:    folds=[1.565, 2.1929, 1.7071, 1.9382, 1.5722]  mean=1.795088
quadratic: folds=[0.1092, 0.1721, 0.1825, 0.1919, 0.1659] mean=0.164337
WINNER: quadratic
ClearML Task: Offline session stored in .../offline-d35a254544a940b1b3ad256dd87a1f7a.zip
```

Exercised: `Task.init` (training type), `task.connect()` hyperparameters, `logger.report_scalar` (per-fold MSE, both models), `logger.report_single_value` (aggregate means), `task.upload_artifact` ×3 (numpy coefficients `.npz`, text, CSV file), `mark_completed()`.

**4. Read-back, separate process (`readback.py`) — PASS**

The offline session is a 4,550-byte zip: `task.json`, `log.jsonl`, `metrics.jsonl`, and artifacts as **plain files in native formats** (`.csv`, `.txt`, `.npz`). The stored record was parsed back and checked:

```
recorded params (typed): {'folds': 5, 'models': 'linear,quadratic', 'n_samples': 200, 'noise': 0.4, 'seed': 42}
artifact metadata entries: ['winner_coefficients', 'winner_name', 'fold_results_csv']
linear:    recomputed mean=1.7950881310 recorded=1.7950881310318187 exact_match=True
quadratic: recomputed mean=0.1643372285 recorded=0.16433722849660112 exact_match=True
stored coefficients:     [0.50210794 1.04408851 0.00216288]
reproduced coefficients: [0.50210794 1.04408851 0.00216288]
coefficients bit-exact reproduction: True
provenance captured: entry_point=experiment.py | script source stored=True | pip requirements snapshot=146 chars
READBACK: PASS
```

Two reproducibility checks close **exactly**: (a) both aggregate means re-derived from the recorded per-fold scalars match the stored aggregates; (b) the winner model's coefficients were **reproduced bit-exactly** by re-running the fit using *only the hyperparameters stored in the record* — the record is self-sufficient.

**5. Server API without a server — confirmed negative**

```
Task.get_task(...) → MissingConfigError: It seems ClearML is not configured on this machine!
setup your own 'clearml-server' or create a free account at https://app.clear.ml
```

There is no local query API in offline mode: the zip *is* the read interface (`Task.import_offline_session` exists but imports into a server). Cross-task comparison/search is a server-only capability.

## Verified / claimed / unestablished

- **Verified firsthand:** SDK 2.1.12 installs and runs on Python 3.12; a first-class offline mode stores complete, self-contained sessions locally; parameter/scalar/single-value/artifact capture all persist; artifacts land in native, inspectable formats; provenance (full script source + pip requirements snapshot) is captured automatically; the record reproduces the result bit-exactly.
- **Claimed by vendor/docs (not exercised):** the server compose stack = **6 services** — apiserver (8008), webserver (8080), fileserver (8081), Elasticsearch, MongoDB, Redis — plus a host kernel prerequisite (`vm.max_map_count=262144` for Elasticsearch) and per-store persistent volumes (per the clearml-server compose file). SDK classes for the wider platform import cleanly (`Dataset`, `OutputModel`, `PipelineController`, `StorageManager`) but importability is surface, not behavior.
- **Unestablished:** everything server-backed — agents/queues remote execution, pipeline orchestration against a backend, dataset versioning against a server, model serving, multi-user/Web UI, cross-task query. Also noted: SDK is Apache-2.0; the *server's* license terms differ from the SDK's and would need checking before any reuse — unverified here.
- **Small defects found:** the offline `task.json` carries **no final status field** (`mark_completed()` leaves top-level status `None` in the stored record), and single-value reports are stored under metric `"Summary"` with the name in the `variant` field and a sentinel iteration (−2147483648) — discoverable only by inspecting the raw events.

## Research note — for our own build

**ClearML's concepts.** The unit is the **Task** (one experiment execution: code snapshot, typed hyperparameters, scalar event streams, artifacts, output models), grouped into projects. Around it: **agents + queues** (workers that pull tasks for remote/reproducible execution), **Datasets** (versioned data objects), **Models** (input/output registry entries), **Pipelines** (tasks composed into DAGs), and **Serving** (model endpoints). The architecture splits into a thin client SDK and a heavy central server; the SDK's event model (JSONL batches) is the real contract between them.

**Take:**
- **The self-contained session bundle.** One zip holding task record + metric events + native-format artifacts, sufficient to reproduce the headline artifact bit-exactly. This is the strongest single idea in ClearML: a lab record that travels and verifies itself. Our platform should make the bundle the primary object, not a by-product.
- **Automatic provenance capture.** Script source and environment snapshot recorded without being asked. Provenance you must remember to log doesn't get logged.
- **Typed hyperparameters in the record** (each value stored with its declared type), so a reader doesn't guess whether `"5"` was a count or a label.
- **Artifacts in native formats** (CSV stays CSV, arrays stay `.npz`) — inspectable with generic tools, unlike opaque serialized blobs.
- **Offline-first client semantics.** The experiment never blocks on infrastructure; sync is a separate, explicit act.

**Deliberately do not copy:**
- **The 6-service server.** apiserver + webserver + fileserver + Elasticsearch + MongoDB + Redis — three separate datastores — plus kernel tuning on the host, is an operations burden sized for a hosted multi-tenant product, not for a lab's own platform. *The weight is the finding:* ClearML's full feature set is inseparable from this stack; there is no light server. Our build should put the session bundle + a single queryable store (one database) behind the API and let the bundle format, not the server, be the portability layer.
- **The server as the only query surface.** Offline records can't be searched or compared without importing them into the heavy stack. A lab platform needs cross-run comparison over local records as a first-class, server-free operation (the same gap Metaflow showed — now confirmed as a category pattern, not one vendor's omission).
- **Quirks that leak storage mechanics into the record:** aggregates filed under a magic `"Summary"` metric with sentinel iterations, and a completed task with no status stamped. A record format should name things what they are.
- **Breadth-before-depth surface area:** agents, queues, datasets, hyperdatasets, serving, and automation all hang off one SDK — the concepts blur (Task vs Dataset vs Model boundaries are conventions, not enforced shapes). Our build should keep fewer, harder-edged primitives.

**Gaps hit → candidate requirements for our build:** (1) local cross-record comparison/query without a server; (2) status/lifecycle stamped into the record itself; (3) one datastore behind the API, with the portable bundle as the interchange format; (4) a server light enough to run where Docker doesn't exist.
