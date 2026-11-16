# DVC — Validation Record (glue tier)

**Framing:** research for the lab's own platform build, not an adoption decision.

**Environment (of record):**
- DVC **3.67.1**, installed in an isolated venv (`~/workspace/lab-platforms/dvc/venv`)
- Python 3.12.3 · git 2.43.0
- Test project: `~/workspace/lab-platforms/dvc/proj/` (its own git repo, local DVC cache only, no remote configured)
- Workload: pure-stdlib ridge regression; prepare → train pipeline; no servers, nothing left running

## Per-step verdicts

### 1. Install in isolated venv — PASS
`dvc --version` → `3.67.1`.

### 2. git + dvc init — PASS
`git init` + `dvc init` produced `.dvc/` + `.dvcignore`; commits made under a repo-local identity.

### 3. Data tracking via pointer file (`dvc add data/raw.csv`) — PASS
Git receives a 91-byte data file's *pointer*, not the file:
```yaml
# data/raw.csv.dvc (the only data artifact git tracks)
outs:
- md5: 528cc4c67065211e2a46d7bb91302e7f
  size: 91
  hash: md5
  path: raw.csv
```
`data/.gitignore` gains `/raw.csv`. The bytes live in the sharded cache:
`.dvc/cache/files/md5/52/8cc4c67065211e2a46d7bb91302e7f` (prefix-sharded by hash).

### 4. Pipeline definition — PASS
Two stages declared in `dvc.yaml`: `prepare` (deps: raw.csv, prepare.py; param `prepare.scale`; out: prepared.csv) and `train` (deps: prepared.csv, train.py; param `train.ridge`; out: model.json; metric: metrics.json).

### 5. Cold run (`dvc repro`) — PASS
```
'd data/raw.csv.dvc' didn't change, skipping
Running stage 'prepare':  prepare: wrote data/prepared.csv with scale=1.0
Running stage 'train':    train: ridge=0.1 slope=1.984867 intercept=0.093232 mse=0.035611 r2=0.998908
```

### 6. Independent re-derivation of the headline metric — PASS (exact)
A separate Python process, reading only the stored parts (prepared.csv + model.json),
recomputed the metric:
```
re-derived mse: 0.03561139025848781
stored     mse: 0.03561139025848781
MATCH_EXACT: True
```

### 7. No-change re-run — PASS (full cache hit)
```
Stage 'prepare' didn't change, skipping
Stage 'train' didn't change, skipping
Data and pipelines are up to date.
```

### 8. Param change → selective rebuild — PASS
`train.ridge` 0.1 → 1.0 inside the *shared* `params.yaml`:
```
Stage 'prepare' didn't change, skipping
Running stage 'train':  train: ridge=1.0 ... mse=0.040237 r2=0.998766
```
Prepare's output hash in the new lockfile is byte-identical (`b7f1b45a…`) — change
detection is **per-parameter-key and per-file-hash**, not per-file: editing one key of
a shared params file did not invalidate the stage that consumes a different key.

### 9. Metrics + lockfile state — PASS
```
$ dvc metrics show
Path          mse      r2
metrics.json  0.03561  0.99891        (ridge=0.1 run; 0.04024 / 0.99877 after the change)
```
`dvc.lock` pins every dep, param, and out by md5+size. The stages are **hash-chained**:
prepare's out md5 (`b7f1b45a03a4110e58ba9549b301f599`) appears verbatim as train's dep md5.

### 10. Data version round-trip — PASS (byte-exact, both directions)
Data modified (12 rows, one value changed) → `dvc add` → committed as data v2
(pointer md5 `09ba182761f9587b80527f0a8b599342`, size 111; workspace `md5sum` matched the pointer exactly).
Then:
```
git checkout 8f75951 -- data/raw.csv.dvc   # the v1 pointer from git history
dvc checkout data/raw.csv.dvc
→ md5sum data/raw.csv = 528cc4c67065211e2a46d7bb91302e7f   (v1 bytes, 10 rows, first y back to 2.1)
git checkout HEAD -- data/raw.csv.dvc && dvc checkout
→ md5sum data/raw.csv = 09ba182761f9587b80527f0a8b599342   (v2 bytes restored)
```
Version travel is a git operation on pointers plus a cache materialization — no server involved.

### 11. Cross-run metrics comparison — PASS (server-free)
```
$ dvc metrics diff 2c48ca0 a28aa5a
Path          Metric    2c48ca0    a28aa5a    Change
metrics.json  mse       0.03561    0.04024    0.00463
metrics.json  r2        0.99891    0.99877    -0.00014
```
Because metrics and lockfiles live in git history, comparing two experiments is a git-ref operation.

### 12. Remote push/pull (S3/SSH/shared-dir remotes) — UNESTABLISHED
Not tested: this validation was local-cache only by design. Remote sync is documented DVC behavior, claimed not verified here.

## Verified vs claimed vs unestablished
- **Verified firsthand:** pointer-file data versioning; sharded content-addressed cache; hash-chained lockfile; per-key param invalidation; selective rebuild; byte-exact version round-trip in both directions; exact metric re-derivation from stored parts; server-free metrics diff across commits.
- **Claimed (docs, not exercised):** remote storage sync, `dvc exp` experiment queue, plots, directory-level tracking at scale.
- **Unestablished:** anything involving a DVC remote or a second machine.

## Research note — git-native content-addressed versioning as an artifact-store model

### Take
- **The two-layer split is the design.** Git holds tiny, diffable, reviewable *pointers* (`.dvc` files + `dvc.lock` — all hashes, sizes, params); a content-addressed cache holds the bytes, prefix-sharded by hash. The artifact reference fits in a pull request; the artifact itself never enters the code store. This is the cleanest artifact-store model in the glue tier and it composes with tooling the lab already runs (git itself).
- **Hash-chained pipeline provenance.** Each stage's output hash is recorded as the next stage's input hash in the lockfile, so the whole run's provenance graph is itself content-addressed and checkable offline — re-derivation closed exactly (step 6) using nothing but stored parts.
- **Per-key parameter invalidation.** Change detection resolves params at key granularity (`train.ridge` vs `prepare.scale`), so a shared params file doesn't cause rebuild storms. Selective rebuild correctness was demonstrated, not assumed (steps 7–8).
- **Comparison falls out of the storage model.** Because metrics + lockfiles are git objects, cross-run comparison (`metrics diff`) is a ref-to-ref operation with zero infrastructure — precisely the capability whose absence was the headline gap in the ClearML offline validation.

### Do not copy
- **MD5 as the default hash.** Observed everywhere above: pointers and lockfile pin md5. Fine for change detection, wrong default for an integrity/provenance record a lab will lean on for years. Take the model, default to a collision-resistant hash.
- **Two-store durability with no redundancy story.** The record is only as durable as *both* stores: lose the cache and every pointer is a reference to nothing. Our build needs the cache treated as a first-class backed-up store (or pointers that carry enough to detect the loss loudly), not a `.dvc/cache` directory that looks disposable.
- **Opaque command strings as the reproducibility contract.** `dvc.yaml` records the stage command verbatim — in this very validation it froze a machine-relative path (`../venv/bin/python`) into the pipeline definition. The lockfile proves *what ran on what inputs*; the command string does not prove the environment. Our build should pair the hash record with the environment capture the MLflow wave showed (requirements/env spec inside the artifact), not a bare shell string.
- **Metrics as unprotected workspace files.** metrics.json/model.json sit in the working tree as ordinary files (their hashes are pinned in the lock, so tampering is *detectable* via `dvc status`, but the files themselves are not in the cache unless declared as outs). A lab record should make the evidence artifacts cache-resident by default.

### Gap named as a requirement
- DVC versions *files and pipeline state*; it has no run *ledger* — no queryable store of "all runs with their params/metrics" beyond what git history + lockfiles imply. For the lab's platform, the artifact store (this model) and the run ledger (per the Metaflow/Flyte findings) are two separate components; DVC validates the first and, by its absence, specifies the second.
