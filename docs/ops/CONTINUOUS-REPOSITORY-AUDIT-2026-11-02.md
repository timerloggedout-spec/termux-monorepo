# Continuous Repository Audit — 2026-11-02

**Repository:** `timerloggedout-spec/termux-monorepo`  
**Base ref reviewed:** `master`  
**Review mode:** remote, read-oriented evidence audit; this report records confirmed observations and bounded inferences.  
**Prepared:** 2026-11-02  
**Scope:** context-relationship historical backfill, quota dispatcher/admission, ATES telemetry, historical audit/status documentation, and directly related CI evidence.

> **Executive verdict:** automation code exists, but the historical backfill is not proven operational end-to-end. The canonical graph manifest is stale relative to the review date, continuation is still required, checkpoint eligibility is false, and the latest observed backfill execution failed its validation gate. A prior successful run skipped collection, so its green conclusion is not evidence that the corpus advanced. Treat this as an evidence/control-plane problem, not a reason to weaken validation.

## 1. Evidence pin and reproducibility

The audit read the default branch through the connected GitHub repository surface. The current source SHAs for the most material inspected files are:

| Path | Blob SHA on reviewed `master` |
| --- | --- |
| `workspace/llm_map/context_relationships/manifest.json` | `bcd13129b3ebd283df920ae18cf1426fb0d8ba85` |
| `.github/workflows/context-relationship-backfill.yml` | `f273cbd8615d28cb11beb27753dde0aad36e6c6d` |
| `.github/workflows/context-relationship-backfill-watcher.yml` | `e7250bece70998d0c2236dc4cf74a49b5a005903` |
| `.github/workflows/quota-dispatch-tree.yml` | `5c172e366787dbf02312dd848f6ae4b3310e3da5` |
| `.github/workflows/agent-throughput-evidence.yml` | reviewed; emitter is present on master |
| `she/metrics/agent_throughput.py` | `48b87817829836892aae3929831b19c65b1ff590` |
| `docs/ops/AGENT-THROUGHPUT-EVENT.schema.json` | `6c55f1c90f517a89d81636a073660b81f0f89450` |
| `docs/ops/AUDIT-FINDINGS-PR523.md` | `4d26675aaaf8793924600350c9e01fffc78d99a1` |

Runtime observations are time-bounded. In particular, `scripts/dashboards/dispatch_tree_observation.json` declares `read_at=2026-11-02T11:07:27Z`; it is an observation artifact, not a guarantee of current state at every later moment.

## 2. Current canonical corpus state

The canonical manifest was last observed at **2026-10-26T13:04:26.270236Z**, not on the audit date.

| Metric | Canonical manifest value | Interpretation |
| --- | ---: | --- |
| Nodes | 35,221 | Corpus size, not completeness |
| Edges | 57,358 | Corpus size, not completeness |
| Verified edges | 52,416 | Classified as verified |
| Candidate edges | 4,942 | Still require evidence/triage |
| Unresolved internal references | 120 | Outstanding reconciliation work |
| Source parser failures | 12 | Parser coverage is incomplete |
| Excluded source files | 1,392 | Exclusions need a documented disposition policy |
| History start page | 1 | Current recorded window begins at page 1 |
| Next start page | 2 | More history is required |
| Issues complete | false | Pagination not exhausted |
| Pull requests complete | false | Pagination not exhausted |
| History coverage | `PARTIAL_CONTINUATION_REQUIRED` | Do not report complete |
| Checkpoint eligible | false | Promotion/checkpoint gate remains closed |
| Last observation | 2026-10-26T13:04:26Z | Four-plus days old on the audit date |

**Decision:** do not mark the corpus complete, checkpoint-eligible, or promoted. Node/edge growth is not a completion signal. Preserve the distinction between pagination completion, data-quality validation, and promotion eligibility.

## 3. Historical backfill runtime — confirmed execution evidence

The observation feed lists these relevant runs:

- [Run 40058473861](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/40058473861), created 2026-10-24T03:28:59Z: **failed** in “Validate backfill corpus before promotion.”
- [Run 39962654795](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39962654795), created 2026-10-23T13:36:45Z: overall **success**, but the “Build one historical relationship-index window” step was **skipped**; “Publish backfill coverage summary” was also skipped. The completion-state step ran. This is a successful no-op, not proof of page advancement.
- Runs 39919627953, 39885212422, and 39865360257 also appear as successful scheduled runs in the observation artifact, but their presence alone does not establish that any window was collected or committed.

### Failure detail from run 40058473861

The log shows:
1. The collector began building page 1.
2. The builder deferred collection after an HTTP 403 response for the issues endpoint and emitted a JSON object with `deferred=true` while returning exit code 0.
3. The six validation unit tests passed.
4. Because the workflow did not inspect the builder result, validation continued against the checked-out corpus artifacts and failed with: `temporal.source_sha does not match the independently captured expected source SHA`.
5. The publish-summary and commit steps were skipped.

**Root cause confirmed:** the builder's rate-limit path is a successful process exit that does not publish a fresh corpus; the workflow treated that exit code as a successful build and validated stale artifacts. The SHA mismatch is the guard correctly detecting stale provenance, not a reason to weaken validation. The workflow fix in this branch captures the builder JSON result and fails immediately on a deferred or incomplete result, before validation can read stale artifacts.

### Required runtime fix

- [Implemented in this branch] Capture the builder JSON separately and reject `deferred=true`, malformed JSON, or missing build-receipt fields before the validator runs.
- [Remaining] Make source identity deterministic for a run: pin the collected source to the event/checkout commit, or explicitly resolve and capture the intended ref SHA once and use that same immutable SHA throughout build and validation.
- [Remaining] Record expected SHA, actual SHA, source ref, build status, run ID, attempt, and the exact deferral reason in the job summary/artifact.
- Rerun a bounded page only after the source-identity issue is fixed; verify that the manifest observation time and history window change as expected. Do not manually force page 2 merely to make the counter move.

## 4. Workflow/control-plane review

### Backfill workflow

The current `.github/workflows/context-relationship-backfill.yml` checks out canonical `master`, reads `history_coverage.next_start_page`, invokes the builder, validates the output, and only then attempts a canonical corpus commit. This is a materially safer design than writing to a diverged staging branch.

However, observed run history proves the complete path is not healthy yet: one recent attempt deferred and failed validation; a prior green run skipped collection. The workflow file being present, a green run, or an artifact existing is insufficient by itself. The success criterion must include a validated fresh build and evidence that the canonical manifest advanced (or an explicit, validated “already complete/no-op” state).

### Dispatcher admission pressure

The latest checked-in dispatch observation reports **126 queued + 36 in-progress = 162 live workflow runs** at 2026-11-02T11:07:27Z. The current `quota-dispatch-tree.yml` calculates `paused = busy >= 6 && !force`, where `busy` is the repository-wide queued plus in-progress count. With a repo-wide count of 162 in that observation, most outputs guarded by `!paused` are suppressed for that cycle.

This is a **confirmed design risk**, not proof that every lane is permanently starved: the observation is time-bound, some outputs intentionally bypass the pause, and the dispatcher has lane-specific stale-age paths. Nevertheless, the global count mixes unrelated workloads and can make admission effectively closed during broad backlogs. The dispatcher should use lane-aware admission and a bounded critical-lane exception rather than treating all repository runs as interchangeable pressure.

Recommended repair:
1. Separate queued/in-progress counts by workflow/lane and count only the workloads that consume the constrained resource.
2. Preserve a hard global safety cap, but add a documented recovery path for stale critical lanes (including the historical backfill) with strict per-lane concurrency and no unbounded fan-out.
3. Emit an explicit `paused_reason`, measured counts, affected lanes, and which override was used in the summary/observation record.
4. Add deterministic tests for: no backlog, unrelated backlog, target-lane backlog, global hard cap, stale critical lane, and explicit force.
5. Verify the dispatch tree's actual output for the backfill lane and the downstream workflow's `event`/run ID; do not infer dispatch from the decision workflow concluding success.

## 5. ATES / agent-throughput evidence

### What exists

- A pure reducer at `she/metrics/agent_throughput.py`.
- An event contract at `docs/ops/AGENT-THROUGHPUT-EVENT.schema.json`.
- An evidence workflow at `.github/workflows/agent-throughput-evidence.yml` using `workflow_run` for selected workflows, read-only repository/action permissions, run/job metadata, optional task-boundary artifacts, and explicit receipts for skip/defer paths.
- The reducer intentionally leaves several metrics unknown when complexity or a sequential baseline is missing. That is correct: missing evidence should not become a fabricated zero or an assumed baseline.

### What is not established by this audit

The implementation files alone do not prove complete runtime coverage. The checked-in dispatch observation lists five live/in-flight Agent Throughput Evidence runs at its observation time, but that is not a verified count of emitted, valid, deduplicated receipts. A complete end-to-end ATES sign-off still needs to reconcile source run + attempt + head SHA against each receipt, validate schema and provenance, and measure missing attribution/task-boundary/complexity rates.

### Required ATES completion gate

- Inventory every eligible source workflow and compare it with the emitter allowlist.
- For successful, failed, skipped, rate-limited, and unmapped source runs, verify that the outcome is represented honestly; note that the current workflow trigger and success-only job condition mean non-success source runs are not processed by the main emitter job.
- Validate receipt schema, required provenance, source run/attempt/SHA identity, artifact retention, and duplicate handling.
- Publish coverage denominators and missingness (identity, provider/model, task boundary, complexity, timestamps), rather than only aggregate throughput.
- Keep throughput observational; do not make speed-only merge gates.

## 6. Documentation drift and corrections required

The following are confirmed documentation problems:

1. `docs/ops/HISTORICAL-CORPUS-BACKFILL-STATUS.md` is titled “Live Status” but its leading canonical-master table describes 2026-08-19. A later addendum cites 2026-10-15, while the current manifest was observed on 2026-10-26. The historical data may remain useful, but it must be explicitly labeled as dated observations and the current canonical snapshot must lead the document.
2. `docs/ops/AUDIT-FINDINGS-PR523.md` includes old claims that the backfill had zero runs ever and that the Phase B emitter did not exist. Current master has `.github/workflows/agent-throughput-evidence.yml`, and the observation artifact lists multiple backfill runs. The original audit must remain preserved as historical evidence, but its current applicability must be annotated.
3. A successful workflow conclusion is described too easily as operational success in some evidence surfaces. For this lane, success must distinguish **collected + validated + committed**, **validated no-op/already complete**, **deferred/rate-limited**, and **failed validation**.

## 7. Severity-ranked remediation register

| Priority | Finding | Required action | Acceptance evidence |
| --- | --- | --- | --- |
| **P0** | Backfill run fails source-SHA validation after a deferred build | Pin source identity and isolate fresh staging artifacts; preserve fail-closed validation | A fresh run has matching expected/actual SHA, a non-deferred build, and a valid receipt |
| **P0** | Corpus is stale and continuation is still required | Run one bounded page after P0 fix; reconcile and publish only if all gates pass | Manifest timestamp/page bounds advance; validator passes; canonical commit is visible |
| **P0** | Repo-wide dispatcher busy count can suppress most lanes | Implement lane-aware admission plus explicit safe recovery path | Unit tests cover admission cases; dispatch summary names paused lanes and reason |
| **P1** | 120 unresolved references, 4,942 candidate edges, 12 parser failures, 1,392 excluded files | Triage by type/impact and preserve explicit dispositions | Every item is resolved, accepted as candidate/excluded with reason, or remains visibly unresolved |
| **P1** | ATES runtime coverage not signed off | Reconcile source runs and receipts; measure missingness and deduplication | Auditable receipt inventory with coverage denominators and schema/provenance validation |
| **P1** | Status/audit documents have stale “live” or implementation claims | Add current snapshot and supersession notes while preserving historical records | Docs name observation times and link the canonical evidence |
| **P2** | No single regression gate for report/status drift | Add machine-checkable checks for manifest-to-status metrics and stale claim markers | CI fails when a “live” snapshot is older than policy or when known stale claims remain unannotated |

## 8. Acceptance checklist for continuous closure

- [ ] Re-fetch the canonical manifest immediately before each run; capture its SHA and `latest_observed_at`.
- [ ] Run one bounded continuation only after deterministic source identity and fresh-output isolation are fixed.
- [ ] Confirm the builder produced a non-deferred receipt for the intended page.
- [ ] Confirm validator receipt binds repo, canonical ref, source SHA, graph counts, hashes, and page bounds.
- [ ] Confirm the resulting commit is based on the then-current canonical branch; if a concurrent push wins, retry only the single intended delta and revalidate.
- [ ] Confirm the manifest reflects the new observation and `next_start_page` advances or becomes null only with complete evidence.
- [ ] Keep `checkpoint_eligible=false` until its own gates pass; pagination completion alone is not sufficient.
- [ ] Confirm dispatcher admission and downstream dispatch with run IDs and attempts.
- [ ] Validate ATES receipts end-to-end and publish missingness/coverage metrics.
- [ ] Update status docs only from fresh canonical evidence; preserve dated historical observations.
- [ ] Re-run relevant unit tests and CI; record actual results, never implied results.

## 9. Scope and limitations

This was a remote audit of the named repository surfaces and selected run evidence, not a full checkout, complete security review, or execution of the repository-wide test suite. The backfill validator's six unit tests were observed passing inside run 40058473861; the subsequent integration validation failed as described. No claim is made that the full repository tests were run in this audit.

The next audit pass should begin with **RE-FETCH → RECONCILE → EXECUTE → OBSERVE → VALIDATE → COMPARE → RECORD → REPEAT**. Preserve evidence identity on every iteration: repository/ref, source SHA, workflow/run ID, attempt, artifact, observed timestamp, and final conclusion.
