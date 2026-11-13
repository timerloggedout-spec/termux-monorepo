# SYNTHESIS — The Lab's Own ML Platform, Designed from Validated Research

**Date:** 2026-11-03 · **Method:** every platform below was installed, run on a real
workload, and read back by an independent process before any claim here was written
(`lab_platform_validation` skill). Each design decision cites the platform whose
*observed evidence* supports it — PASSes, FAILs, and the gaps in between.

Evidence base (all in `~/workspace/lab-platforms/<name>/VALIDATION.md`):
MLflow 3.17.2 · Metaflow 2.19.40 · ClearML SDK 2.1.12 · ZenML 0.98.0 ·
flytekit 1.16.31 · MLRun 1.12.1 · kfp (Kubeflow Pipelines) 2.18.0 ·
Dagster 1.13.28 · Kedro 1.7.0 · DVC 3.67.1.

**Working title: `labbook`** *(provisional — a name is a decision, and this one
has not been taken yet; everything below works under any name).*

---

## 1. THE CONSOLIDATED LEDGER

One table. Each row: the decision · what we **take** (platform + observed
evidence) · what we **refuse** (platform + observed evidence).

| # | Decision | Take — platform + evidence | Refuse — platform + evidence |
|---|---|---|---|
| 1 | **Storage & content addressing**: artifacts live in a content-addressed store (hash-sharded), referenced from a thin append-only record tree; bytes never enter git — small, diffable **pointer records** do. | **Metaflow**: pickled blobs under `.metaflow/<Flow>/data/<2-hex>/<sha1>` + reference tree; dedup and exact history fell out, and a separate process re-derived every headline number from stored parts (fold MSEs averaging *exactly* to the recorded train MSE, 0.178230). **DVC**: git holds a 91-byte pointer (md5+size) while bytes sit prefix-sharded in the cache; byte-exact version travel both directions via `git checkout` of the pointer + cache materialization. | **Flyte**: local `FlyteFile` is a path passthrough — no hash, no dedup, no registry; nothing a second process can trust. **DVC (hash choice)**: md5 everywhere — fine for change detection, wrong default for a multi-year integrity record; we default to SHA-256. |
| 2 | **Artifact formats & self-description**: native, inspectable formats declared *explicitly* in the record (CSV stays CSV, arrays stay `.npz`, metrics stay JSON); every artifact version names the code that reads it. | **ClearML**: offline bundle artifacts in native formats; winner coefficients reproduced **bit-exactly** from the bundle alone. **ZenML**: each artifact version records its materializer as a source path (module+attribute); a foreign process `.load()`-ed the stored model and recomputed accuracy to an *exact* match (0.926666…, `MATCH_EXACT=True`). | **Metaflow + Dagster**: pickle as the default format — opaque, unsafe, Python-locked (both records flag it as the top lock-in). **ZenML (the silent half)**: materializer chosen silently by Python type, nothing declares "this is a pickle-family blob"; we take the self-description, refuse the silence — format is a declared field, pickle-class formats are flagged exceptions. **MLflow**: skops trust gate broke the *stock* RandomForest path (`sklearn.tree._tree.Tree` "untrusted") — a safe format whose default path fails is still a broken default. |
| 3 | **The run record & local ledger**: an append-only, **queryable local ledger is the default**, server-free — one store (SQLite) behind the API; runs, steps, artifacts, materializations all readable from a cold process with nothing running. | **Dagster**: persistent local instance (sqlite history + per-run event shards, ~560K total) answered run records, per-asset materialization history, and latest-per-asset from a cold process with **zero servers started**; three independent reads agreed bit-for-bit. **Metaflow**: local mode is a genuine first-class citizen (full branch/foreach/resume/Client locally). **MLRun §4**: a SQLite-backed local server behind the *identical* client API worked and survived a restart — the architecture allows it; it just isn't shipped. | **Flyte**: local execution registers *no* metadata anywhere (no `~/.flyte`, empty scratch, nothing to bind `FlyteRemote` to) — "local-mode amnesia." **MLRun**: client-only mode silently uses `NopDB` — a run "completed" while any other process's `list_runs` returns 0; a warning at startup is not a record. **ClearML**: offline records cannot be searched or compared without importing into the 6-service server. **Kedro**: readable logs, no queryable execution store at all. |
| 4 | **Asset-first modeling, runs as producers**: the durable unit is the **asset** (dataset/model/metric-set) with an append-only materialization history; a run is a disposable producer event. Cross-run history is a primary query, not a reconstruction. | **Dagster**: both materializing runs were literally `__ephemeral_asset_job__` — the platform itself treats runs as throwaway and per-asset materialization history as the record; metadata *accumulates* (2 runs ⇒ 2 events per asset, latest in one call) instead of overwriting. | **Metaflow / Flyte / Kubeflow** (all run-centric): history must be reconstructed *from* runs; Metaflow's record states the consequence plainly — comparing arms and picking winners was entirely hand-rolled user code. |
| 5 | **Cross-run comparison is a platform primitive**, server-free: diff any two runs/assets over params, metrics, and artifact hashes in one call. | **DVC**: `dvc metrics diff <ref> <ref>` compared two experiments' mse/r² as a pure git-ref operation — because metrics + lockfiles are git objects, comparison costs zero infrastructure. **Dagster**: per-asset history across runs is one query (see row 4). | **Metaflow**: "no built-in notion of experiment comparison" — the lab's *core workload* left to every user. **ClearML**: comparison is server-only; offline, the zip is the only read interface and `Task.get_task` without a server raises `MissingConfigError`. A category pattern across two independent platforms — now a stated requirement, not a hope. |
| 6 | **Compile-to-IR + graph-semantics honesty**: pipelines compile to a static, versioned IR (diffable, assertable, archivable); every executor runs the full compiled semantics **or fails loudly, by name**; every run verdict enumerates every graph node with an explicit state (ran / skipped-by-gate / not-supported). | **Kubeflow**: IR schemaVersion 2.1.0 separated authoring from execution; a third-party parser asserted **20/20 structural claims** (typed edges, `taskOutputArtifact` wiring, gate as `triggerPolicy.condition` data) with zero infrastructure. **Metaflow**: `merge_artifacts` hard-fails on conflicting branch values rather than guessing — the same honesty at join time; one line to fix, zero silent merges. | **Kubeflow (the sharpest finding of the program)**: the local runner **silently dropped the entire condition group** — gate condition *true* (0.995 > 0.8), gated task never ran, no trace in the log, pipeline still reported **SUCCESS**. A verdict that omits part of the graph manufactures false evidence. **Flyte**: the decisive exception arrived buried in repeated asyncio "exception was never retrieved" noise plus an unrelated shutdown ImportError. |
| 7 | **Error surfacing**: one primary exception, cleanly presented, that names the offending value, the expected contract, and the fix. Execution errors are never swallowed into a plausible-looking state. | **Flyte (the good half)**: the type engine failed *before compute* and printed the offending literal next to `Expected Python type: typing.List[FlyteFile]` — a real wiring error caught at the boundary. **Kedro**: both catalog failures named the dataset (`Dataset 'PickleDataset' not found in 'pickle'`). **Metaflow**: the merge error named the conflicting artifacts and the remedy. | **MLRun**: handler exception ⇒ run finished with status `created` and `null` results (error visible once, mid-log); `run.outputs` **polled forever** against a missing DB; `run.status.artifacts` crashed on its own `None` entry. **ClearML**: a *completed* task's record carries **no status field at all**, and single values hide under a magic `"Summary"` metric with sentinel iteration −2147483648. **Flyte (the bad half)**: see row 6. |
| 8 | **Stack/catalog composition**: infrastructure bindings are **data** — a named catalog (dataset name → format + location + reader) and a named stack (orchestrator + artifact store + metadata store) — resolved per run and **stamped on the run record**. Experiment code holds zero infrastructure references. | **Kedro**: nodes name datasets; one YAML decides what each name physically is; part-runs (`--from-nodes`) resolved against the catalog across processes, and any dataset's type/location is a one-line edit with zero node changes. **ZenML**: registering an alternate artifact store + stack moved **all** artifact I/O (14 files) to a new root with zero pipeline-code changes; the stack is stamped on the run (`run.stack.name`). | **Kedro (the tax)**: dataset classes moved to a separate package (`kedro-datasets`) while documented short names still parse; bare class names rejected with an after-you-know-the-answer error; no `kedro catalog list` verb exists. **ZenML**: bare `pip install zenml` *cannot run locally* (working core behind the `[local]` extra); the default local stack drags in a deployer, log store, and image builder nobody asked for. Composition yes; sprawl and core-behind-extras no. |
| 9 | **Caching semantics, stated explicitly**: cache keys are (code identity + input hashes + declared params); a fully cached run still writes a run record pointing at the reused artifacts; **cache scope is declared** (per artifact store? per project?) in the design and echoed in every run record. | **ZenML**: identical second run — "All steps of the pipeline run were cached" — *and still wrote its own run row*; cache key doubles as a reproducibility fingerprint. **DVC**: no-change re-run skipped both stages; a one-key param change (`train.ridge` 0.1→1.0 in a *shared* params file) rebuilt only `train` — per-key invalidation, demonstrated. **Kubeflow**: metrics persisted as first-class parts made exact read-back possible. | **Kubeflow**: `enableCache: true` is compiled into every task **by default, invisibly** at the DSL level — a stale-result hazard the author never chose. **ZenML**: cache silently does **not** cross artifact stores — defensible, undiscoverable; a semantic users must be told, not taught by surprise. |
| 10 | **Promotion = aliases**: model versions are immutable; promotion is one mutable named pointer per purpose (`champion`) over them; deployments reference the pointer; audits record what it resolved to at the time. | **MLflow**: stage transitions are *gone* in 3.x; `set_registered_model_alias("lab-smoke-model","champion","1")` resolved and read back cleanly, with tags/descriptions at both model and version level. Also MLflow's **Logged Model** seam — "a model was produced" (`models:/m-<id>`) decoupled from "a model is blessed" (registry version) — matches a lab that produces far more models than it promotes. | Stage state machines generally (MLflow removed theirs — the market's own verdict). **Kubeflow**: `system.Model` typing is a *label only* — the "model" was a JSON of two centroids and nothing validated it; a type that promises must carry a checkable validation hook, or be named as a label. |
| 11 | **The small, frozen API principle**: a small versioned JSON/REST contract is specified **first**; any client (Python or otherwise) is one consumer of it. The read surface is deliberately tiny: run records · per-asset materializations · latest-per-asset · compare. | **MLflow (the seam)**: one client works unchanged against file store, sqlite, or HTTP server — the store abstraction is the portability seam. **Dagster**: the three queries above are exactly what its read-back needed (they exist — under churning names). **ZenML**: one Client API read local and service tiers alike (Metaflow shows the same boundary working). | **MLflow**: legacy REST returns 404 inside the same major version; `experiment_ids` deprecated for `locations` mid-version — "in practice the Python client *is* the API," and the client drags two web frameworks. **ZenML**: three first-contact breakages in one session (import path, `name=` vs `pipeline_name=`, outputs-as-lists). **Dagster**: three first-contact API misses in one small test (`get_latest_materialization` doesn't exist; deprecated `get_event_records`; payload nesting). **MLRun**: `get_run` exists on *neither* DB class (`read_run` does). Four platforms, one lesson: an unfrozen surface taxes every consumer forever. |
| 12 | **Environment capture is automatic**: every run and every model artifact carries its environment (requirements / python-env spec) and code identity **without being asked**; provenance (code SHA + data hashes + env) is a mandatory structured field, not a tag convention. | **MLflow**: every logged model ships `requirements.txt` / `python_env.yaml` / `conda.yaml` by default. **ClearML**: full script source + pip requirements snapshot captured automatically ("provenance you must remember to log doesn't get logged" — so it isn't left to memory). **Metaflow**: parameters stored as artifacts on a `_parameters` task + automatic system tags (runtime/python/user) — the run is self-describing. | **MLflow (the gap inside the take)**: git SHA and dataset identity are *tag conventions*, not enforced fields — for a science lab this is the deepest single gap in the record. **DVC**: the stage's bare command string froze a machine-relative path (`../venv/bin/python`) into the definition — a command string is not an environment. **Dagster**: no content hash or code version stamped on a materialization unless opted in. |
| 13 | **Lifecycle stamping**: every record carries its lifecycle state, stamped by the system at each transition (created → running → completed / failed / skipped-by-gate), with timestamps — in the record itself, not inferable only from a server's view. | **Dagster**: run records carry `DagsterRunStatus.SUCCESS` queryable from the event log; materialization events are themselves the stamped transitions. **Metaflow**: failed runs remain inspectable in the Client (run `1793700346305271` readable after failure) — failure is a state in the record, not an erasure. **DVC**: the lockfile pins the completed state's full hash chain, checkable offline. | **ClearML**: `mark_completed()` leaves the stored record's status `None` (see row 7). **MLRun**: the swallowed-error run sat at status `created` forever — a lifecycle that can strand is a lifecycle that lies. |

---

## 2. THE DESIGN — `labbook` v1 (provisional name)

### 2.1 Architecture at v1 scope

Five components, deliberately few. Python throughout; no server required for
any v1 operation; no Docker assumed anywhere (two of ten platforms were
infra-blocked precisely there — ClearML's server, Flyte's cluster tier).

```
 AUTHORING            COMPILATION           EXECUTION              STORES
 ─────────            ───────────           ─────────              ──────
 pipeline.py    ──►   labbook compile ──►   labbook run      ──►   Ledger (SQLite, append-only)
 (functions +          │  emits IR            (local runner;        Artifact store (CAS, SHA-256)
  catalog names)       │  (YAML, v1)           Actions runner        Pointer records (git)
                       ▼                      in CI)                 Bundle export (zip)
                  graph.json/IR  ──►  labbook verify / compare / promote (cold-process reads)
```

1. **Catalog** (Kedro's contract, ZenML's registry): a `catalog.yml` in the
   project maps every dataset/model name → {format, location, reader}.
   Nodes name datasets; they never touch a path or a format. Fully-qualified
   names accepted everywhere; `labbook catalog list` exists from day one
   (Kedro's missing verb is our day-one verb).
2. **Compiler**: pipeline definitions (plain Python functions wired by
   catalog names + a *declared* graph — not edges hidden in method bodies,
   Metaflow's do-not-copy #2) compile to a static **IR YAML, schemaVersion
   labbook/1**: components, typed edges (with optional validation hooks,
   Kubeflow row 10), parameters with types + defaults, gates as condition
   *data* over named outputs, and **cache policy declared in the definition**
   — never a compiler default (Kubeflow row 9).
3. **Runner**: executes the IR (local subprocesses in v1; GitHub Actions jobs
   as the scale-out executor — see hooks, §2.4). Semantics-faithful or
   refuses by name: any IR construct the runner cannot execute is a hard
   error listing the construct, before anything runs (Kubeflow row 6). Every
   run's verdict enumerates **every** node: `ran | cached | skipped-by-gate |
   failed`, with the gate expression and its evaluated inputs for any skip.
   Parallel arms broadcast scalar co-inputs natively (Flyte row 6's fan-out
   boilerplate is refused), and joins refuse to merge conflicting artifact
   values without an explicit exclusion (Metaflow row 6).
4. **Ledger + artifact store**: one SQLite database (append-only event
   tables) + a SHA-256 content-addressed file store, prefix-sharded
   (Metaflow/DVC row 1). Git holds pointer records only (DVC row 1).
5. **Read/verify surface**: `compare`, `verify`, `promote`, `export-bundle`
   as cold-process operations over the ledger + store — no server, ever,
   for reads (Dagster row 3, ClearML row 5).

### 2.2 Data model (entities + fields)

Mutability classes follow MLflow's proven three-way split (row: params
write-once / metrics append-only / tags mutable — survived a decade unchanged).

**Run** — one execution of a compiled pipeline.
`run_id (uuid)` · `ir_hash (sha256 of the compiled IR)` · `pipeline_name` ·
`stack_name` (composition stamped per run, ZenML) · `lifecycle`
(created/running/completed/failed — stamped at every transition, row 13) ·
`started_at / finished_at` · `code_sha (git, mandatory)` · `env_spec`
(requirements lock, mandatory, row 12) · `params` (typed, write-once) ·
`actor` (fleet attribution stamp, §2.4) · `cache_policy_declared`.

**NodeRun** — one node of one run. `run_id` · `node_name` · `state`
(ran/cached/skipped-by-gate/failed/not-supported) · `gate_expression` +
`gate_inputs` (present iff skipped-by-gate) · `error` (the single primary
exception, verbatim, iff failed) · `duration_ms`.

**Asset** — the durable unit (Dagster row 4). `asset_id` · `name` (catalog
name) · `kind` (dataset/model/metrics/report) · `format` (**declared**:
csv/npz/json/parquet/text/…; `pickle-class` is an explicit flagged value,
never a silent default, rows 2/8).

**Materialization** — one production of one asset by one run (append-only).
`materialization_id` · `asset_id` · `run_id` · `node_name` ·
`content_hash (sha256, unconditional — Dagster row 12's opt-in refused)` ·
`size_bytes` · `store_path` · `reader` (materializer as module+attribute,
ZenML row 2) · `typed_metadata` (headline values stamped on the event
itself — accuracy, rows, n — readable *without loading the value*, Dagster)
· `input_hashes[]` (the hash chain: this materialization's inputs are other
materializations' hashes, DVC's lockfile chain as data) · `created_at`.

**MetricEvent** — append-only series point. `run_id` · `asset_id?` ·
`name` (**named what it is** — no magic "Summary", ClearML row 7) ·
`value` · `step` · `at`. Aggregates are *derived by query*, never stored
under sentinel iterations.

**Promotion** — an alias over asset versions (MLflow row 10).
`asset_name` · `alias` (e.g. `champion`) · `materialization_id` ·
`set_by` (attribution stamp) · `set_at`. Resolution is a query; audits
record the resolution *at the time of use* in the consuming run's record.

**Bundle** — the portable interchange object (ClearML row 2/5): one zip =
run record (JSON) + metric events (JSONL) + artifacts in native formats +
env spec + IR. Self-sufficient: `labbook verify` on an exported bundle,
on a machine with nothing else, must reproduce the headline results
bit-exactly or say which check failed (ClearML's bundle closed this test;
it's our acceptance test, §3).

### 2.3 Storage shape

- **Bytes**: CAS directory `store/<sha256[0:2]>/<sha256>` (Metaflow's
  2-hex sharding, DVC's cache layout — both validated), on the local
  filesystem in v1; the store interface is a path-mapping so an object
  store can replace it without semantic change (Metaflow's tier
  abstraction, row 3 take).
- **Records**: one SQLite file, append-only event tables mirroring §2.2
  (Dagster proved ~560K serves a whole validation; MLRun §4 proved SQLite
  behind the same API survives restarts). **Git is the distribution and
  backup substrate for records**: pointer files + exported ledger snapshots
  are git objects, so history, review, and cross-machine travel are PR
  operations (DVC row 5: comparison as a git-ref operation is the model).
- **Durability rule** (DVC's do-not-copy): the CAS is a first-class backed-up
  store, not a cache directory that looks disposable; a pointer whose bytes
  are missing must fail *loudly* on read, by hash.

### 2.4 API surface — small, versioned, frozen on purpose

Contract first (`labbook/1`), JSON over a Python client that is *one
consumer* (MLflow row 11). The entire v1 surface:

| Operation | Shape |
|---|---|
| `POST /runs` (or `labbook.run(ir, params)`) | compile-check + execute; returns run_id |
| `GET /runs/{id}` | full run record incl. every NodeRun state |
| `GET /assets/{name}/materializations` | append-only history, newest first |
| `GET /assets/{name}/latest` | latest materialization + typed metadata (no value load) |
| `GET /compare?a=<run>&b=<run>` | param diff · metric diff · artifact-hash diff |
| `POST /assets/{name}/promote` | set alias → materialization (attribution-stamped) |
| `labbook verify <run|bundle>` | re-derive headline metrics from stored parts; PASS/FAIL per check, named |
| `labbook export <run>` | the §2.2 bundle |

That's all. Anything else is a new version of the contract, not a quiet
addition (ZenML/Dagster/MLRun churn, row 11, is the evidence for freezing).

### 2.5 Execution model

- **Local-first**: a run is a Python process tree over subprocesses
  (Kubeflow's SubprocessRunner proved the unconditional DAG runs fine this
  way); the ledger write is part of the run path, never a post-hoc scrape
  (Flyte/MLRun rows 3/7 are what happens otherwise).
- **Actions as the execution home**: the same IR compiles to a GitHub
  Actions workflow (one job per node, artifacts passed via the CAS
  snapshot committed/pushed as pointers + bundle upload). This is not a
  new bet for the fleet: Temporal-integration already migrated its
  engagement home to Actions (stages 3–4 landed and passed in-job), and
  CodeRoad's credited runs are Actions-native. Local and Actions
  executions write the *same* ledger schema; an Actions run exports its
  ledger delta + bundle as workflow artifacts and a follow-up job/PR
  merges them into the repo's ledger — records travel through git, the
  substrate the fleet already reviews.
- **No standing server, no daemons** (the VM is sandbox-only by standing
  rule; two platform servers in this program were Docker/Kubernetes-bound
  and unvalidatable here — ClearML, Flyte cluster tier).

### 2.6 Where each choice hooks into what already exists in termux-monorepo

| Design choice | Existing fleet surface it hooks |
|---|---|
| Git as records substrate (pointers, ledger snapshots, PR-reviewed history) | DVC's validated model + the repo's own PR/merge discipline; bundles + pointers land as ordinary repo files under the lab package (e.g. `ml/labbook/` beside `ml/pipelines/`, where MLRun's record already files MLRun as "library + one production lane"). |
| GitHub Actions as executor | The fleet's standing execution layers of record (Actions first, per the owner's own layering) + temporal-integration's completed Actions migration + CodeRoad's Actions-native driver — same runner, same receipts pattern. |
| Attribution on every record (`actor`, `set_by`) | The fleet's provenance layer: `[MUSEai]@{role:{moniker}}` stamps, attribution/1.5's corroborated-transport rule (245 corroborated / transport-stratum-only — labbook records inherit the discipline: a record proves *transport and execution*, authorship weight is a separate claim), and `ops/telemetry/session-history.jsonl` (614 records) as the existing append-only JSONL precedent. |
| Append-only JSONL event exports | HindSight's published record shape (`ops/telemetry/hindsight-*.jsonl`) and the lane-events store on Neon (lane-events project, already the wired ledger store for fleet events) — labbook's SQLite is local-first, but its export format is JSONL from day one so the Neon lane-events path stays open without redesign. |
| Bundle as the interchange object | ClearML's validated bundle + the fleet's existing export/backup plane (workspace backup repo already moves content-addressed-ish exports on a cadence) — bundles are the unit the backup plane carries. |
| Honest-verdict discipline (enumerate every node; fail loudly by name) | The repo gate (`scripts/ci/repo_gate.py`, HARD + RATCHET) and the DoE rule-9 truth bar (≥2 legs ⇒ TRUE, single-leg ⇒ HELD, self-asserted ⇒ CLAIM) — `labbook verify` output is written to be consumed as rule-9 evidence, not as a green checkmark. |
| Study/certification tie-in | The lab-platforms program itself is D-adjacent lab work; the platform's own build doubles as certification-lane *derived-artifact* material (the lane's rule: each rung's completion package includes derived {skill, KB} — this synthesis + the ten validation records are exactly that shape). |

---

## 3. V1 BUILD SCOPE — the smallest build that embodies the proven requirements

**Build (in this order — each step is usable without the next):**

1. **Ledger + CAS + pointer records.** SQLite schema per §2.2; CAS writer/
   reader with SHA-256 verify-on-read; git pointer export. *Embodying
   rows 1, 3, 13.*
2. **Catalog + declared graph + compiler to IR.** `catalog.yml`, pipeline
   definition with declared edges, `labbook compile` emitting
   `labbook/1` IR with cache policy and gates as data. *Rows 6, 8, 9.*
3. **Local runner with honest verdicts.** Subprocess execution; per-node
   state enumeration; merge-refusal at joins; scalar broadcast in
   parallel steps; lifecycle stamping; env + code-SHA capture on every
   run, automatically. *Rows 6, 7, 12, 13.*
4. **Asset-first reads: materializations, latest, compare.** The three
   frozen read operations + `compare`. *Rows 4, 5, 11.*
5. **Aliases/promotion + bundle export + `verify`.** *Rows 2, 10, and the
   ClearML acceptance property.*

Explicitly **not** in v1: any server; any UI; scheduling; serving/
deployment of models (MLRun's function-as-unit and load-from-artifact
contract is the *v2* seam — validated at mock level only, and v1 does not
pretend otherwise); multi-tenancy or auth (Kubeflow's platform weight,
refused until it is a real requirement); hyperparameter search (Katib is
claimed-only evidence).

**Validation plan for the build itself** (the `lab_platform_validation`
skill, applied to our own thing — same bar the ten platforms were held to):

- **Round-trip test**: the program's canonical workload (branch + 5-fold
  foreach + join + gate — the shape Metaflow/Kubeflow/Flyte all ran)
  executed on labbook; a *separate cold process* re-derives the headline
  metric from stored parts; PASS requires exact agreement (the check
  Metaflow, ClearML, ZenML, Dagster, DVC, MLRun, Kubeflow all closed).
- **Gate-honesty test**: the Kubeflow trap, replayed against ourselves —
  a pipeline whose gate condition is true and whose gated node is made
  to fail/skip; PASS requires the verdict to enumerate the node by name
  with its state. A bare SUCCESS is an automatic FAIL of the build.
- **Amnesia test**: kill the runner mid-run; PASS requires the ledger to
  show the run, its lifecycle state, and every completed node's
  materializations from a cold process (the Flyte/MLRun failure, inverted
  into an acceptance test).
- **Bundle self-sufficiency test**: export a run, delete the local store,
  `verify` from the bundle alone; PASS requires bit-exact reproduction
  (ClearML's bar).
- **Cache-semantics test**: identical re-run (all cached, run record still
  written) + one-key param change (only dependent nodes rebuild) —
  ZenML's and DVC's demonstrated behaviors, asserted.
- **Format test**: every artifact in the test run carries a declared
  format; a pickle-class artifact must appear in the record flagged as
  such, or the test fails.
- Each test lands as a `VALIDATION.md`-style record beside the build —
  evidence first, and any FAIL is reported as a FAIL with its evidence,
  per the program's own rule.

---

## 4. OPEN DECISIONS — what the evidence does not settle

Stated for owner/main. Each carries the options the evidence supports;
none blocks steps 1–2 of the v1 build except #1.

1. **Name.** `labbook` is a placeholder. Owner naming pass (the fleet has
   done this before — Commit Replay's engine name is still an open
   owner item; Repo Replay's `Rev-wRight` is explicitly provisional).
   *Options:* keep a descriptive working title permanently, or run the
   naming pass before the first repo landing so history starts clean.
2. **Ledger home at scale.** SQLite local-first is proven at lab scale by
   Dagster + MLRun §4; the fleet *also* has a wired Postgres-class store
   (Neon lane-events). *Options:* (a) SQLite + git snapshots forever
   (simplest; git is the sync), (b) SQLite local + Neon as the shared
   query tier later (JSONL export already keeps this open), (c) Postgres
   from day one (MLflow's record warns against mistaking sqlite for the
   production shape — but Dagster's evidence says the local ledger is the
   product, and no evidence in this program exercises multi-writer load).
   *Recommendation from evidence:* (a) now, (b) when a second writer
   appears.
3. **IR: own schema vs adopting KFP IR.** Kubeflow's IR is validated,
   assertable, and carries the gate-as-data model. *Options:* (a) adopt
   KFP IR 2.1.0 wholesale (inherit its executor ecosystem *and* its
   nominal typing + silent cache default, both refused above), (b) own
   `labbook/1` schema borrowing the structure (typed edges, trigger
   policy as data) with our cache/format/lifecycle fields mandatory.
   *Evidence leans (b)* — the two KFP defaults we refuse are *in* its IR —
   but (a) is the faster path and the decision is reversible only before
   records accumulate.
4. **Pickle-class artifacts: flagged exception or banned in v1?** ZenML
   proved a raw sklearn model crosses boundaries via a bundled
   materializer with zero extra packages; Metaflow/ClearML evidence says
   native formats are what made records inspectable and bit-exact.
   *Options:* (a) allow `pickle-class` as a declared, flagged format
   (pragmatic; models are the common case), (b) v1 requires a native or
   spec'd format per asset kind, models included (skops/ONNX-class),
   accepting the friction MLflow's F1 showed. Evidence supports the
   *declaration* either way; it does not settle the ban.
5. **Serving in scope for v2, or never ours?** MLRun validated
   load-serving-from-artifact at mock level (live endpoint
   unestablished — nuclio/docker-bound). *Options:* (a) v2 adds the
   function-as-unit serving seam, (b) labbook stays an evidence platform
   and serving belongs to whatever deploys (aliases already give a
   deployer its contract). No firsthand evidence of a live endpoint
   exists in this program; deciding (a) needs a serving validation wave
   first.
6. **Where the build lands.** *Options:* (a) `ml/labbook/` inside
   termux-monorepo (hooks in §2.6 all assume this; the registry's
   Domino entry and the integrations program already live there),
   (b) a dedicated repo under the AppID-at-build-start rule (that rule
   governs *competition entries*; this is lab infrastructure, and the
   monorepo-first placement rule from the certifications lane points the
   other way). *Evidence/process leans (a)*; stated because the fleet's
   build-start rule makes it a decision, not a default.
7. **DOMINO row interaction.** The lab platform is the FOSS answer to the
   Domino question, and the DOMINO opportunity row is live with
   state-triggered tiers. *Options:* (a) labbook's v1 landing is the
   evidence that steps the DOMINO row's BASE tier (research complete →
   build exists), (b) the two tracks stay formally separate (partner/
   self-host filings judged on their own merits). The state-trigger spec
   already names validation PASSes as tier evidence; whether a *build*
   counts is main's call.

---

*Every claim above traces to a named platform's VALIDATION.md. Where the
evidence ran out, §4 says so instead of designing past it.*
