# Dagster — Validation Record (glue tier, lighter pass)

Framing: research for the lab's own platform build, not an adoption decision.
This platform is the program's **contrast case for the local ledger**: wave 3 found
Flyte's local mode keeps no queryable execution record at all; Dagster was tested
specifically on whether its local event log is a real, queryable ledger.

## Environment (verified firsthand)

- dagster **1.13.28** (dagster-pipes / dagster-shared 1.13.28) · scikit-learn 1.9.1 · pandas 3.1.0
- Python 3.12.3, isolated venv at `~/workspace/lab-platforms/dagster/venv/`, install ~90s, clean.
- Fully local: persistent instance under `DAGSTER_HOME=~/workspace/lab-platforms/dagster/dagster_home/`
  (sqlite history + per-run event DBs). **No server was ever started** — no webserver,
  no daemon; nothing left running after the test.

## Steps and verdicts

### 1. Install — PASS
`pip install dagster pandas scikit-learn` → `Successfully installed … dagster-1.13.28 …`
Version read back from the installed package: `dagster 1.13.28`.

### 2. Asset graph definition — PASS
Three software-defined assets in `assets_lab.py`, dependencies declared by argument name:
`raw_data` (iris DataFrame) → `features` (standardized X/y dict) → `model_metrics`
(LogisticRegression accuracy dict). Each asset stamps typed output metadata
(`rows`, `n_samples`, `accuracy`, …) at production time.

### 3. Materialize locally — PASS (one authoring nit, see gaps)
```
success: True
materialized: raw_data       run: 04368915-7195-4ff2-acbb-025dbb880844
materialized: features       run: 04368915-7195-4ff2-acbb-025dbb880844
materialized: model_metrics  run: 04368915-7195-4ff2-acbb-025dbb880844
```
Materialized twice (two runs in the log: `388ae06d…` and `04368915…`, both SUCCESS) —
deliberately, so the read-back could prove history *accumulates* per asset.
Instance on disk: `history/runs.db` + per-run `<run_id>.db` event shards + asset
values under `storage/{raw_data,features,model_metrics}` (560K total).

### 4. Separate-process read-back via the instance API — PASS
`readback.py` (cold process, imports no asset code paths for its queries) used
`DagsterInstance.get()` + run records + event-log queries + latest-materialization lookup:
```
RUN_RECORDS count=2
  run 04368915 status=DagsterRunStatus.SUCCESS job=__ephemeral_asset_job__
  run 388ae06d status=DagsterRunStatus.SUCCESS job=__ephemeral_asset_job__
ASSET raw_data:      materialization_events=2 latest_run=04368915 metadata={'rows': 150, 'cols': 5, 'target_classes': 3, 'path': '…/storage/raw_data'}
ASSET features:      materialization_events=2 latest_run=04368915 metadata={'n_samples': 150, 'n_features': 4, 'mean_abs_after_scaling': 0.8407246215984789, 'path': '…/storage/features'}
ASSET model_metrics: materialization_events=2 latest_run=04368915 metadata={'accuracy': 0.9733333333333334, 'model': 'LogisticRegression(max_iter=1000)', 'path': '…/storage/model_metrics'}
STORED raw_data shape=(150, 5)
STORED features X.shape=(150, 4) y.shape=(150,)
STORED model_metrics={'accuracy': 0.9733333333333334, 'n': 150, 'classes': 3}
```

### 5. Re-derive the headline number from stored parts — PASS, exact
Retrained the same model in the read-back process on the **stored** `features` value only:
```
RE-DERIVED accuracy=0.9733333333333334
STORED-VALUE accuracy=0.9733333333333334  EVENT-LOG accuracy=0.9733333333333334
MATCH value==event: True   value==rederived: True
```
Three independent reads — event-log metadata, stored asset value, fresh recompute —
agree bit-for-bit.

## Verified vs claimed vs unestablished

- **Verified firsthand:** install; asset-graph materialization on a persistent local
  instance; run records queryable; **per-asset materialization history queryable across
  runs with zero servers running**; typed metadata readable from the event log without
  loading values; exact re-derivation.
- **Claimed (docs, not tested):** schedules/sensors, partitions, asset checks, the
  webserver UI, Dagster Cloud, non-local IO managers and compute providers.
- **Unestablished:** multi-process/daemon execution (`dagster dev`), data-version /
  code-version stamping behaviour (not enabled here), behaviour at event-log scale.

## Gaps hit (candidate requirements for the own-build)

- **Instance query API churns inside one version line.** `get_latest_materialization`
  does not exist (it is `get_latest_materialization_event`, returning an entry whose
  payload nests under `.materialization`, not `.asset_materialization`); `get_event_records`
  works but is deprecated with a warning steering to `fetch_materializations`; a
  `DagsterEvent.run_id` assumption broke the first driver script. Three first-contact
  API misses in one small test — the ledger is excellent, the surface over it is a moving target.
- **No content hash on the materialization by default.** Metadata carried rows/cols/path —
  no data version or checksum was stamped unless opted in. Provenance is event-based
  (who/when/what-metadata), not content-addressed, out of the box.
- **First-run telemetry nag.** A fresh instance prints a telemetry welcome/opt-out banner;
  a lab ledger should not phone-home-conceptually by default.

## Research note — take / do-not-copy

**TAKE**

- **The asset is the durable unit; the run is disposable.** Both materializing runs were
  `__ephemeral_asset_job__` — Dagster itself treats the run as a throwaway producer and the
  asset's materialization history as the record. Every earlier wave (Metaflow, Flyte, Kubeflow)
  is run-centric: history is something you reconstruct *from* runs. Here the cross-run,
  per-asset history is the *primary* query — which is exactly the comparison substrate
  Metaflow and ClearML both lacked. Our build should be asset-first with runs as producers.
- **An append-only event log as the one ledger, local-first.** Sqlite shards + index under
  one instance directory, fully queryable from any cold process with nothing running.
  This is the direct refutation of Flyte's local amnesia: local mode can keep a real ledger
  at ~560K for a whole test. Requirement for our build: the local ledger is the default,
  not a backend tier.
- **Typed metadata stamped on the materialization event itself** (`MetadataValue.float`
  accuracy, row counts), *plus* the IO manager automatically adding the value's storage
  `path` to that same event. The event tells you the headline number and where the value
  lives, without unpickling anything — audit first, load on demand.
- **Metadata accumulates; it does not overwrite.** Two runs ⇒ two materialization events
  per asset, latest resolvable in one call. History-as-append is what makes the
  re-derivation check (step 5) meaningful at all.

**DO-NOT-COPY**

- **Pickle as the default value format.** The default IO manager stores bare pickles —
  the same opaque, Python-locked choice Metaflow made. Dagster partially redeems it with
  typed event metadata, but the value itself stays uninspectable. Our build: native/typed
  formats (ClearML's lesson) *and* the typed event metadata (Dagster's lesson).
- **The sprawling, shifting query surface.** A ledger this good deserves a small frozen
  read API (the recurring MLflow/ZenML conclusion, now thirded): run records, per-asset
  materializations, latest-per-asset — three calls, versioned, done.
- **Opt-in content identity.** Hashes/versions exist in the platform but are not stamped
  by default; silent absence invites exactly the Kubeflow-style "SUCCESS with missing
  parts" failure. Our build stamps content hash + code identity on every materialization,
  unconditionally.
- **Telemetry-on-first-run defaults.**

## Verdict

**PASS** — Dagster 1.13.28: the local event log is a real ledger (queryable, append-only,
server-free), the asset-first model inverts the run-centric design of every prior wave in
the right direction for a lab, and the headline metric re-derives exactly from stored parts.
