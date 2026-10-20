# Historical Evidence Corpus

**Status:** canonical architecture and coverage contract  
**Role:** longitudinal evidence substrate for PR/issue history, DOE/MVT, Moneyball/3L0, and manager evolution.

## What this is

The historical corpus is the durable record of what happened across the repository:

```text
GitHub commits / PRs / issues / reviews / comments / checks / workflow telemetry
        │
        ▼
context-relationship corpus
        │
        ├── PR / issue observations
        ├── action → effect evidence
        ├── attribution + provenance
        └── verified / candidate relationships
                │
                ▼
        DOE / MVT experiment cohorts
                │
                ▼
          Moneyball / 3L0
                │
                ▼
       learning + manager evolution
```

The corpus is **not** a collection of prose receipts. A receipt is a projection of one observation or promotion event. Historical learning must come from the longitudinal corpus.

## Canonical storage

The repository-native relationship corpus lives under:

`workspace/llm_map/context_relationships/`

The canonical artifacts are:

- `manifest.json` — schema, source/ref, collection bounds, counts, parser failures, retention state.
- `nodes.jsonl` — metadata-only entities.
- `edges.jsonl` — verified/candidate relationships with evidence URLs.
- `matrix.json` — compiled evidence matrix.
- `github-report.json` / `source-report.json` / `merge-report.json` — collection diagnostics.
- `checkpoint.json` — incremental high-water mark when a collection is complete enough to advance.
- `build-summary.json` — machine-readable coverage summary.

No discussion body, credential, browser/session state, or secret belongs in the corpus.

## Historical backfill

Backfill is deliberately **page-bounded and resumable**.

Run the operator-controlled workflow:

`.github/workflows/context-relationship-backfill.yml`

Start at page `1`. The collector reports `history_window.next_start_page`. Continue with that exact value until it becomes `null`.

A page is not global completion. The corpus must retain the page/window and collection timestamp so a later observer can distinguish:

- `COMPLETE` — the requested history window has no next page.
- `PARTIAL_CONTINUATION_REQUIRED` — more pages exist.
- `PARTIAL_BOUNDARY` — collection stopped because another explicit limit was reached.
- `FAILED` — collection could not establish a trustworthy observation.

## PR/issue observation rule

Every PR and issue encountered by the collector is an **observation candidate**, regardless of whether it merged, failed, was superseded, or became stale.

Not every PR needs a Markdown receipt.

Use compact machine-readable observations for the full population; create human-readable receipts only for important promotion/effectiveness events or when an operator needs a durable narrative.

## Attribution

GitHub actor identity is not agent identity.

Attribution should use the evidence chain:

`workflow run/job/step → triggering event → PR/issue → SHA → timestamps → comment/review markers → provider/model/session provenance → confidence`

Unknown attribution remains `unknown` or `low-confidence`; it must not be silently assigned to a human, Jules, Gemini, OpenRouter, or another provider.

## DOE / MVT

The corpus supplies the historical substrate. Experiments add a frozen comparison layer:

- stable `experiment_id`;
- baseline SHA;
- candidate SHA;
- treatment / orchestration policy;
- fixed validation suite;
- observation timestamp;
- outcome;
- provenance;
- confidence.

Promotion is separate from measurement.

PR #390 is a calibration/stress-test cohort for control-plane behavior. It is not a special exception to the corpus and is not a canonical SWE-bench task.

## Moneyball / 3L0

Moneyball/3L0 measures integrated orchestration outcomes, not activity:

- outcome;
- integration;
- time;
- useful cycles;
- context efficiency;
- retries;
- conflicts;
- human intervention;
- attribution confidence.

The optimization target is:

`correct integrated outcome / (effort + time + context consumption + feedback cycles + conflicts + retries + human intervention)`

Managers/orchestration policies compete on comparable cohorts. Learning records retain experiment history and inform subsequent manager policy; they do not rewrite historical evidence.

## Receipts

`receipt != corpus`

A receipt can say that a promotion happened. It cannot establish that the historical corpus is complete, that a provider executed, or that a workflow was validated unless the underlying evidence is present.

Receipts should link back to stable PR/SHA/evidence identifiers and should never be the only durable record of an event.

## Current known coverage

The committed relationship index is a **historical seed, not yet the complete all-time corpus**. Its manifest is authoritative for its actual page/window and counts.

As of the current committed snapshot, the manifest records a retained historical index on `master-staging` with `next_start_page = 2`; therefore additional backfill pages are still required before describing the relationship corpus as complete.

Do not “fill” missing history by inference. Continue the explicit backfill and record each window.

## Acceptance invariant

A future corpus release is complete only when:

1. all declared history pages have been traversed;
2. every page's bounds and continuation state are retained;
3. PR/issue/commit/review/comment/check/action metadata is SHA/time bound;
4. bodies and secrets remain excluded;
5. verified and candidate relationships remain distinct;
6. attribution confidence is explicit;
7. experiments consume frozen corpus observations;
8. learning records reference the observations that produced them.
