# labbook (working title, provisional)

The lab's own ML platform, v1 — built from validated research, not adopted.
Every design decision below cites the row of the consolidated ledger in
`SYNTHESIS.md` (the design record produced by the lab-platforms validation
program: ten platforms installed, run on a real workload, and read back by
an independent process before any claim was written). Where the evidence
ran out, the synthesis says so in its §4; v1 does not design past it.

**Status:** v1 build, steps 1–5 of synthesis §3 complete. Serving is
deliberately out of scope (the alias contract is the v2 seam, §4.5).

## What v1 is

```
pipeline.py  ──► labbook compile ──► IR (labbook/1)  ──► labbook run ──► SQLite ledger (append-only)
 (declared graph,      (gates + cache policy                (subprocess      + SHA-256 CAS
  catalog names)        as data)                             per node)       + git pointer records
                                                                            │
        labbook verify / compare / promote / export  ◄──────────────────────┘
        (cold-process reads — no server, ever)
```

Five components, deliberately few: **catalog**, **compiler**, **runner**,
**ledger + CAS**, **read/verify surface**. Python, stdlib-only, no server
required for any v1 operation, no Docker assumed.

## Design decisions → ledger rows

| Decision | Row | Where |
|---|---|---|
| SHA-256 content-addressed artifacts, prefix-sharded; bytes never enter git — small pointer records do (`Ledger.export_pointers`) | 1 | `labbook/cas.py`, `labbook/ledger.py` |
| Native inspectable formats, **declared** per asset; every materialization names its reader (module+attribute). `pickle-class` allowed only as a flagged exception, stamped in the record and checked by `verify` | 2 | `labbook/formats.py`, runner stamping |
| One SQLite ledger behind the API; append-only event tables; every read works cold with nothing running | 3 | `labbook/ledger.py` |
| Asset-first: the durable unit is the asset with an append-only materialization history; a run is a producer event. A run's output set follows `run_outputs` links, so cache-reused materializations count as the run's outputs (origin run stays recorded) | 4 | ledger schema + `run_materializations` |
| `compare` is a primitive: param diff, metric diff **with computed deltas**, artifact-hash diff — server-free | 5 | `labbook/api.py:compare` |
| Compile-to-IR (`labbook/1`, our own schema — synthesis §4.3 option (b)); gates are condition *data*; the runner runs the full compiled semantics or refuses by name **before anything runs**; every verdict enumerates every node instance (`ran / cached / skipped-by-gate / failed / not-run / not-supported`) with gate expression + evaluated inputs on any skip | 6 | `labbook/compiler.py`, `labbook/runner.py:precheck`, `labbook/gates.py` |
| One primary exception naming value · expected contract · fix; a node failure is recorded verbatim, downstream nodes are enumerated `not-run`, the run is `failed` — never a plausible-looking state | 7 | `labbook/errors.py`, runner |
| Catalog: name → {kind, format, location, reader}; nodes name assets only; `labbook catalog list` exists from day one; stack name stamped on every run | 8 | `labbook/catalog.py` |
| Cache key = code identity + input hashes + declared params; cache policy is **declared in the pipeline definition** (the compiler refuses its absence); a fully cached run still writes its own run record; scope is the declared policy, echoed on the run | 9 | compiler + runner |
| Promotion = aliases over immutable versions, attribution-stamped; resolution is a query (`resolve`) | 10 | `ledger.promote`, `api.promote` |
| Small, versioned, frozen API (`labbook/1`); the Python client and the CLI are two consumers of the same contract | 11 | `labbook/api.py`, `labbook/cli.py` |
| Environment (python, platform, installed distributions) + code identity (git SHA, else content hash of node sources) captured automatically on **every** run — mandatory fields, not tag conventions | 12 | `runner.capture_env`, `runner.capture_code_sha` |
| Lifecycle stamped at every transition (`created → running → completed/failed`) in the record itself; a killed runner leaves a truthful `running` record with completed nodes' materializations readable cold | 13 | `ledger.stamp_lifecycle`, amnesia test |

## The contract (`labbook/1`)

| Operation | Shape |
|---|---|
| `Labbook.run(ir, params)` | compile-check + execute; returns the verdict (every node enumerated) |
| `Labbook.get_run(run_id)` | full run record incl. every node state |
| `Labbook.materializations(asset)` | append-only history, newest first |
| `Labbook.latest(asset)` | latest materialization + typed metadata (no value load) |
| `Labbook.compare(a, b)` | param · metric (with deltas) · artifact-hash diff |
| `Labbook.promote(asset, alias, materialization_id, actor)` | set alias (attribution-stamped) |
| `Labbook.verify(run_id)` | per-check PASS/FAIL, named — re-derives the headline from stored parts |
| `Labbook.export_bundle(run_id, path)` / `Labbook.verify_bundle(path)` | the portable zip; verifies **alone**, bit-exact or naming the failed check |

Anything else is a new version of the contract, not a quiet addition.

## Layout

- `labbook/` — the package (`cas`, `formats`, `yamlmini`, `catalog`,
  `compiler`, `gates`, `ledger`, `runner`, `node_exec`, `api`, `cli`,
  `verify`, `errors`).
- `demo/` — the canonical workload (branch × 5-fold foreach + join +
  gate) every researched platform also ran: `catalog.yml`, `pipeline.py`.
- `tests/` — unit tests + the acceptance suite (synthesis §3's
  validation plan applied to this build). `VALIDATION.md` is the
  build's own evidence record.

## Quickstart

```bash
cd demo-project            # a dir holding catalog.yml + pipeline.py
python -m labbook --project . compile pipeline:PIPELINE -o ir.yml
python -m labbook --project . run ir.yml
python -m labbook --project . verify <run_id>
python -m labbook --project . compare <run_a> <run_b>
python -m labbook --project . export <run_id> run.zip
python -m labbook verify-bundle run.zip     # on any machine, alone
```

Project state lives in `<project>/.labbook/` (`ledger.db`, `store/`,
`ir/`). The demo in `demo/` is a ready-made project: copy its two files
anywhere and run the commands above.

## Not in v1 (deliberate)

Any server; any UI; scheduling; **serving/deployment of models** — aliases
give a future deployer its contract, and the seam is left open (§4.5);
multi-tenancy/auth; hyperparameter search. Actions as a second executor
(same IR, same ledger schema) is designed in synthesis §2.5 and lands
after v1's local proof.
