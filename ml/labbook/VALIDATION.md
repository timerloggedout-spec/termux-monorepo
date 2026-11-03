# VALIDATION — labbook v1 build

The build held to the program's own bar (`lab_platform_validation`:
install → real workload → independent read-back → verdict with evidence).
Every verdict below cites the test or run that produced it.

**Environment:** Python 3.12.3, stdlib-only package, local VM.
**Suite:** `python -m unittest discover -s tests` — **28 tests, OK**
(22.5–28.0 s across runs): `tests/test_units.py` (16) +
`tests/test_acceptance.py` (12).

## Acceptance criteria (from SYNTHESIS.md §3 + the build order)

### 1. Gate honesty — the Kubeflow trap replayed against ourselves

- **Gate true + gated node made to fail** (`test_gate_honesty`):
  verdict lifecycle `failed`, node `gated` enumerated **by name** with
  state `failed` and its error verbatim (`RuntimeError: boom-gate-marker`),
  downstream node enumerated `not-run`. No bare SUCCESS. **PASS**
- **Gate condition true ⇒ gated node executes** (demo run): node
  `report` (gate `cv_mean_quad < 1.0`, evaluated inputs true) has state
  `ran` in the verdict — a silently vanished branch is impossible by
  construction and asserted by test. **PASS**
- **Gate false** ⇒ `skipped-by-gate` with the gate expression and its
  evaluated inputs (`{"score": 2.0}`) in the record; downstream consumer
  also enumerated `skipped-by-gate` with the reason. **PASS**
- **Unsupported construct** (hand-edited IR, node kind `quantum`):
  refused by name in a `LabbookError` **before anything runs**; the
  ledger holds zero runs afterwards. **PASS**

### 2. Round trip — cold process re-derives the headline exactly

Demo run (canonical workload: branch × 5-fold foreach + join + gate):
headline `cv_mean_quad = 0.28977123932188514`,
`cv_mean_linear = 0.8045681303545672` (quadratic arm wins, as the true
model is quadratic). A **separate cold process**, API only, recomputed
each fold's MSE from the stored dataset artifact + stored model
artifacts and matched: the 5 recorded fold metrics exactly, the stamped
headline exactly, and the metrics asset's stamped value exactly
(`verify` checks `fold-metrics-match-stored-parts`,
`headline-recompute`, `metrics-asset-headline` — all PASS, 8/8 checks).
**PASS** — `test_round_trip`, plus the CLI run below reproducing the
identical headline in a fresh project directory.

### 3. Comparison — two runs, server-free, computed deltas

`compare(run ridge=0.1, run ridge=5.0)`: param diff names `ridge`
changed (0.1 → 5.0) and `seed` unchanged; artifact diff: `dataset`
same hash (cache-reused), `fold_models_quad` different; metric diff for
`cv_mean_quad` carries a computed `delta == b - a ≠ 0`. **PASS** —
`test_compare_two_runs_server_free`.

### 4. Cache semantics (synthesis §3 plan)

Identical re-run: **every** node instance `cached`, and the cached run
still wrote its own complete run record with the same headline.
One-key param change (`ridge` 0.1 → 2.0): `load` stayed `cached`
(it does not consume `ridge`); both train arms, `join`, and dependents
rebuilt (`ran`). **PASS** — `test_identical_rerun_all_cached_and_param_change_partial`.

### 5. Amnesia (synthesis §3 plan)

Runner subprocess killed with SIGKILL mid-run (second node sleeping):
a cold process then read the ledger and found the run present with
lifecycle **`running`** (never falsely completed), node `first` state
`ran`, its materialization present, and its bytes readable and exact
from the CAS. **PASS** — `test_killed_runner_leaves_true_record`.

### 6. Bundle self-sufficiency (synthesis §3 plan)

Exported bundle verified **alone** in a fresh process (no project, no
ledger): manifest hashes, artifact hashes, pickle-class flag, and the
fold/headline recompute — 6/6 checks PASS. A copy with one artifact byte
flipped **fails** verification (manifest + hash checks name it), it does
not crash or pass. **PASS** — `test_bundle_verifies_alone_and_tamper_fails`.

### 7. Formats (synthesis §3 plan)

Every materialization of the canonical run carries a declared format
and a reader path; the run's deliberate `pickle-class` artifact
(`legacy_blob`) is recorded with format `pickle-class` and
`typed_metadata.pickle_class == true`, and `verify`'s
`pickle-class-flagged` check passes. **PASS** — `test_pickle_class_flagged_in_record`,
`verify` check `formats-declared`.

## CLI end-to-end (shipped surface, not just the API)

Fresh directory + demo files: `compile` → `run` (exit 0, lifecycle
completed, headline identical to the test-suite run:
`cv_mean_quad 0.28977123932188514`) → `verify` (exit 0, 8 checks PASS)
→ `export` → `verify-bundle` (exit 0, 6 checks PASS) → `catalog list`
(8 assets). Deterministic across processes and directories.

## Notes / honest bounds

- Node execution is subprocess-per-node on the local machine; the
  Actions executor (synthesis §2.5) is designed, not built in v1.
- The IR YAML reader/writer is a documented subset (`yamlmini`), not
  general YAML — outside constructs are refused with a named error.
- `npz` support is a stdlib subset (.npy v1.0, 1-D float64 arrays) —
  enough for declared array artifacts without a numpy dependency.
- First implementation of `run_materializations` missed cache-reused
  outputs (a run's outputs are its `run_outputs` links, not only rows
  it originated); caught by the compare acceptance test and fixed
  before landing — recorded here because the record is the product.
