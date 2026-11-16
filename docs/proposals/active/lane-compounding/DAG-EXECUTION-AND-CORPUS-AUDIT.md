# DAG Execution and Historical Corpus Audit Dossier

**Status:** active; last reviewed 2026-10-21  
**Work item:** [LC-005](ITEMS.md)  
**Execution DAG:** [Issue #1443](https://github.com/timerloggedout-spec/termux-monorepo/issues/1443)  
**Historical corpus:** [Issue #522](https://github.com/timerloggedout-spec/termux-monorepo/issues/522)  
**Decision/evidence routing:** [Issue #923](https://github.com/timerloggedout-spec/termux-monorepo/issues/923)  
**Quota admission:** [PR #1441](https://github.com/timerloggedout-spec/termux-monorepo/pull/1441)

## Executive summary

The repository already has a deterministic dependency-phase engine. Extend and test the existing implementation; do not create a duplicate scheduler or a second source of truth.

Keep three control planes distinct:

1. **Execution DAG:** explicit prerequisites, topological ordering, readiness, lifecycle state, idempotent claims, and deterministic waves.
2. **Historical relationship corpus:** verified/candidate relationships, collection bounds, parser diagnostics, unresolved references, and its own checkpoint-eligibility gate.
3. **Decision/evidence and quota policy:** uncertainty-aware routing and provider admission. Probabilities must never override prerequisite, approval, safety, or quota gates.

The committed corpus manifest inspected for this dossier records 30,978 nodes, 52,624 edges, 47,845 verified edges, 4,779 candidate edges, 14 parser failures, one unresolved internal reference, and `checkpoint_eligible: false`. Its observation timestamp is 2026-10-15T19:16:02.945529Z. This is a bounded snapshot, not proof of complete all-time history or a production-valid checkpoint.

## 1. Source-of-truth inventory

| Concern | Canonical source | Establishes | Does not establish |
|---|---|---|---|
| Dependency plan | `docs/agentic/dependency-phases.json` + schema | Declared dependencies, approvals, completion policy | Live task success |
| Offline engine | `scripts/agentic/dependency_phase_engine.py` | Plan validation, topological order, waves, evidence-based lifecycle evaluation | Distributed scheduler or probability engine |
| Live adapter | `scripts/agentic/dependency_phases.py`, `github_phase_adapter.py` | Live evidence reads and explicit-apply operations | API success equals desired effect |
| Tests | `tests/test_dependency_phase_engine.py` | Fixture-level contracts | Live GitHub/provider behavior |
| Corpus | `workspace/llm_map/context_relationships/manifest.json`, JSONL artifacts and reports | Versioned bounded observation and diagnostics | Complete all-time history |
| Corpus builder | `archwiz/context_relationships/build_index.py` and compiler/collectors | Artifact build/publish path | Independent runtime validation |
| Quota | `ops/quota/registry.json`, `scripts/quota_poll.py`, [PR #1441](https://github.com/timerloggedout-spec/termux-monorepo/pull/1441) | Documented limits and supported live readings | Every per-minute limit or atomic cross-job reservations |

Historical relationship edges are not execution dependencies. Only explicit, validated dependency declarations can establish execution order.

## 2. Existing DAG engine — code inspection

The current engine already implements:

- `topological_order()` with dependency lists, outgoing adjacency, and a ready queue;
- cycle rejection if not every phase can be emitted;
- schema validation for duplicate phase IDs, invalid dependency types, duplicate/self/unknown dependencies, and cycles;
- `compute_waves()`, placing a phase one wave after its latest prerequisite;
- lifecycle evaluation that blocks downstream work until predecessors are complete;
- approval, merged-PR, required-check, Project-status, and idempotent-claim gates;
- deterministic rendering and a stable plan digest.

This is a reference evaluator, not proof of a general production scheduler. The engine is offline and side-effect free; live GitHub operations belong in adapters.

### Canonical semantics

- A phase declares prerequisites in `depends_on`.
- The conceptual edge direction is **prerequisite → dependent**.
- Ready nodes have no unmet prerequisites.
- Operational execution additionally requires completion evidence and all applicable approval, safety, policy, and quota gates.
- Disconnected components are valid; never infer dependencies between them.
- A topological order proves ordering constraints, not successful execution.

The current queue is repeatable for a fixed graph because initial ready nodes and each adjacency set are sorted. It is not documented as the globally lexicographically smallest topological ordering. Tests should assert repeatability and prerequisite-before-dependent invariants, not an incidental total order unless a stronger tie-break contract is adopted.

### Required test coverage

1. Chain, diamond/fan-in, fan-out, disconnected components, and a single node.
2. For every edge, assert prerequisite index is lower than dependent index.
3. Deterministic repeatability on the same graph; input-order variation if canonical ordering is intended.
4. Duplicate prerequisites rejected by validation; unknown endpoints and self-dependencies fail closed.
5. Cyclic graphs emit no accepted partial order; diagnostics identify residual blocked nodes and, ideally, a concrete cycle.
6. Downstream work remains blocked until all required predecessors satisfy policy.
7. Failed, skipped, blocked, unknown, and succeeded states remain distinct.
8. Approval and merged-PR/check evidence cannot be bypassed by a Project status.
9. Duplicate active claims prevent duplicate dispatch.
10. Topology mutations trigger coherent recomputation; no mixed-snapshot evaluation is accepted.

### Merge semantics must remain distinct

- **Graph merge:** validate explicit dependencies, endpoints, duplicates, and cycles.
- **Execution merge:** release a dependent only when all required predecessors satisfy completion policy.
- **Evidence merge:** reconcile stable IDs, SHA/ref, timestamps, and provenance; missing evidence remains unknown, not zero.
- **Probability merge:** specify assumptions and evidence identity independently. Never multiply branch probabilities naively or allow confidence scores to bypass hard gates.

## 3. Research findings

### Kahn example: edge-direction trap

The supplied DEV article says each key lists its dependencies, but its sample increments the indegree of those listed dependency values. Under that stated representation, the sample appears to invert the intended order. Do not copy it without a chain test proving every prerequisite precedes its dependent.

Source: https://dev.to/leopfeiffer/topological-sort-with-kahns-algorithm-3dl1

### NetworkX: fully consume the generator

The official NetworkX API says topological sorting applies to directed acyclic graphs and returns a generator. Cycle-related errors can occur during iteration. Oracle tests must materialize the entire order inside the expected-exception boundary; accepting a yielded prefix can falsely validate a cyclic graph. Keep the graph immutable while consuming the generator.

Source: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.dag.topological_sort.html

### FalkorDB: benchmark hypothesis, not a dependency

The article motivates evaluating server-side readiness/frontier computation for large graphs. It does not prove the repository fork has a ready-made topological-sort primitive or that DB-side computation is faster for this workload. Targeted GitHub code searches found no indexed matches for the queried terms, but this is not proof of absence; no full local clone/source audit was performed.

Before adopting the fork, inspect upstream delta, procedure registration, tests, license, maintenance, and actual semantics. Benchmark against the existing in-memory implementation first.

Source: https://www.falkordb.com/blog/topological-sort-algorithm-2/

## 4. Historical corpus audit

Manifest fields observed:

- `node_count`: 30,978
- `edge_count`: 52,624
- `verified_edge_count`: 47,845
- `candidate_edge_count`: 4,779
- `source_report.scanned_files`: 7,271
- `source_report.source_files`: 1,213
- `source_report.excluded_files`: 1,383
- `source_report.unsupported_files`: 4,630
- `source_report.parser_failures`: 14
- `github_report.unresolved_internal_reference_count`: 1
- `github_report.checkpoint_eligible`: false
- `history_window.next_start_page`: null
- observed at: `2026-10-15T19:16:02.945529Z`

`next_start_page: null` only describes the recorded collection window; it is not an all-time completeness proof. Compiler success or JSON validity does not prove source correctness, full coverage, runtime validation, or checkpoint eligibility. Keep verified and candidate edges distinct.

### The 14 parser failures recorded in the manifest

| # | Path | Reported error |
|---:|---|---|
| 1 | `_1-Projects/a/yobitrageswap/api/indodax_api.py` | unexpected indent, line 5 |
| 2 | `_1-Projects/a/yobitrageswap/api/polygon_api.py` | unexpected indent, line 5 |
| 3 | `_1-Projects/a/yobitrageswap/api/pumpfun_api.py` | unexpected indent, line 5 |
| 4 | `_1-Projects/a/yobitrageswap/api/solana_api.py` | unexpected indent, line 4 |
| 5 | `_1-Projects/a/yobitrageswap/api/tastytrade_api.py` | unexpected indent, line 5 |
| 6 | `_1-Projects/a/yobitrageswap/api/uniswap_api.py` | unexpected indent, line 14 |
| 7 | `_1-Projects/a/yobitrageswap/api/yobit_api.py` | unexpected indent, line 15 |
| 8 | `archwiz/dangle_detector.py` | expected indented block after if, line 65 |
| 9 | `archwiz/manifest_to_cache.py` | unterminated f-string, line 17 |
| 10 | `cli-synthegration/workspace/compression_sandbox/generate_loop.py` | expected except/finally, line 109 |
| 11 | `cli-synthegration/workspace/staging/reconstructed_msg596.py` | invalid syntax, line 2 |
| 12 | `deepcli/agent.py` | unexpected character after line continuation, line 364 |
| 13 | `deepcli/deepagent.py` | unexpected character after line continuation, line 925 |
| 14 | `harmony_hub/utility_belt/recover-session.py` | unexpected indent, line 20 |

Disposition each path as: valid source needing parser support; intentional/historical artifact to exclude with a documented reason; invalid source to repair in its own lane; or unsupported format. Do not blindly rewrite legacy source just to satisfy the collector. Record path, source SHA/ref, parser version, disposition, reason, and validation evidence. Investigate the single unresolved internal reference and retain it as unresolved until evidence closes it.

### Initial source spot-check (current master, 2026-10-21)

A targeted fetch of the listed files confirms that at least several manifest findings correspond to visibly malformed or non-source content in the current branch snapshot: multiple `yobitrageswap/api/*_api.py` files begin with module imports followed by indented method definitions without a visible enclosing class; `archwiz/dangle_detector.py` has an incorrectly nested `if`; `archwiz/manifest_to_cache.py` contains a multiline code-fence string written as an ordinary quoted f-string; `cli-synthegration/workspace/compression_sandbox/generate_loop.py` contains duplicated/nested fragments; `cli-synthegration/workspace/staging/reconstructed_msg596.py` contains a shell `grep` command rather than Python source; and `harmony_hub/utility_belt/recover-session.py` has a visibly misindented block.

This is a targeted sample, not a full syntax audit. The manifest was collected on 2026-10-15, so each reported path must be re-read and parsed at the exact candidate SHA before its current disposition is decided. The spot-check does **not** authorize bulk repair: some paths may be generated, archival, intentionally incomplete, or outside the supported source scope.

## 5. Quota admission and scheduling

PR #1441 describes reconciling OpenRouter's official daily free-model counter with local reservations, fail-closed handling of missing/stale daily evidence, cooldowns, and telemetry. Its stated limits are important: the endpoint does not expose all per-minute capacity; cache-backed reservations are not a distributed atomic lock; 429s can still occur; same-run fallback is not implemented in that change; and that change did not make live provider requests.

Recommended flow: resolve eligible candidates → obtain fresh official quota evidence where supported → fail closed when required evidence is unknown/stale → apply conservative local reservation margin → check dependency/approval/safety/quota gates → dispatch → record actual response and task outcome → classify quota/timeout as provider/admission failures, not model-quality failures.

The observed HTTP 429 bot comment on #1443 proves quota risk is real, not that PR #1441 is merged or validated. Do not claim that races or 429s are eliminated.

## 6. Provenance and validation receipt

Where applicable, record repository/ref/source SHA; plan/graph schema and algorithm versions; input digest; node/edge counts; workflow/run/job/step/artifact/attempt IDs; topological order and wave/frontier transitions; validation command and exit status; cycle/blocked/unknown-endpoint findings; corpus collection window, parser failures, unresolved references and checkpoint result; quota evidence source/timestamp, provider/model, HTTP status and retry/cooldown; observed outcome separate from execution state and promotion decision.

Missing evidence must be `unknown`, not zero. Do not put secrets, tokens, session state, browser profiles, credentials, or private discussion bodies in receipts. A `VALIDATED` label means only what its named validator actually checked.

## 7. Benchmark plan

Compare the existing Python engine with any proposed FalkorDB frontier approach on frozen, reproducible fixtures:

- 100, 1,000, 10,000, and 30,000+ nodes;
- sparse, dense-ish, and repository-like edge distributions;
- fan-in/fan-out and skewed graphs;
- no, low, bursty, and concurrent mutations;
- frontier rounds, wall time, p50/p95, CPU/memory, query count, transferred bytes, recovery, snapshot consistency, and operational cost.

Record generator parameters, seeds, runtime/database versions, repetitions, warm/cold runs, and confidence intervals. Do not adopt a database implementation based on an article or one benchmark.

## 8. Delivery gates

| Stage | Deliverable | Exit evidence |
|---|---|---|
| A. Document | This dossier and linked work-item updates | Reviewable commit and cross-links |
| B. Test | Ordering invariants and adversarial fixtures | Unit tests pass on exact candidate SHA |
| C. Corpus | Dispositions for 14 parser failures and one unresolved reference | Rebuilt manifest, reconciled counts/hashes, independent checkpoint gate |
| D. Quota | Validate PR #1441 and any bounded follow-up | Current-SHA CI and race/fallback tests; provider evidence only if available |
| E. Benchmark | Python vs DB frontier report | Reproducible measurements justify adoption |
| F. Integrate | DAG, quota, and evidence gates | State-machine tests prove no bypass or duplicate authority |
| G. Promote | Repository dual gates and effect verification | `python3 scripts/ci/repo_gate.py`, `python3 scripts/ci/termux_smoke.py`, required CI green, and re-fetched current-SHA evidence |

## 9. Status / non-claims

- [x] Existing engine and tests inspected.
- [x] Manifest/source-report diagnostics inspected.
- [x] Kahn, NetworkX, and FalkorDB findings recorded in #1443.
- [ ] New invariant tests committed and run.
- [ ] Dual gates run on final candidate SHA.
- [ ] All parser failures dispositioned and unresolved reference investigated.
- [ ] Corpus rebuilt and checkpoint eligibility independently verified.
- [ ] FalkorDB fork fully audited or benchmarked.
- [ ] Live provider behavior validated.

No claim is made that the corpus is complete, Hex import succeeded, the fork contains a ready-made topo primitive, quota races are eliminated, or production validation passed.

## References

- [Issue #1443](https://github.com/timerloggedout-spec/termux-monorepo/issues/1443)
- [Issue #522](https://github.com/timerloggedout-spec/termux-monorepo/issues/522)
- [Issue #923](https://github.com/timerloggedout-spec/termux-monorepo/issues/923)
- [PR #1441](https://github.com/timerloggedout-spec/termux-monorepo/pull/1441)
- [Native Orchestration Contracts](../../ops/ORCHESTRATION-CONTRACTS.md)
- [Historical Evidence Corpus operations](../../ops/corpus/README.md)
- [Dependency-phase automation](../../agentic/README.md)
- [NetworkX API](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.dag.topological_sort.html)
- [Kahn article](https://dev.to/leopfeiffer/topological-sort-with-kahns-algorithm-3dl1)
- [FalkorDB article](https://www.falkordb.com/blog/topological-sort-algorithm-2/)
