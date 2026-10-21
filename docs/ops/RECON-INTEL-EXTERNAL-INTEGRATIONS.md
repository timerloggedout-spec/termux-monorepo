# RECON Intel: Existing Integrations, Research Leads, and BIUDL Plan

**Repository:** `timerloggedout-spec/termux-monorepo`  
**Prepared:** 2026-10-21  
**Related work:** [Issue #1450](https://github.com/timerloggedout-spec/termux-monorepo/issues/1450), [draft PR #740](https://github.com/timerloggedout-spec/termux-monorepo/pull/740)  
**Evidence rule:** this is an inventory of inspected repository paths and source links, not a claim that every referenced external service is connected, licensed for every use, or operational in production.

## Executive finding

The repository is not starting from zero. Master already contains an evidence/telemetry architecture, an internal tournament module, blind-agent-evaluation and adaptive-wait skills, a SWE reference evaluation lane, advisory CodeQL and OpenSSF Scorecard workflows, and documentation that explicitly positions Langfuse and Arize Phoenix as optional consumers of a neutral event schema.

The highest-value move is **integration and contract reconciliation**, not duplicating those components. The current PR's offline `scripts/eval_tournament.py` should be treated as a small deterministic test/reference utility until reconciled with the existing `deepcli/deepcli/observatory/tournament.py`, leaderboard, MoneyBall contract, and existing result schemas. Do not introduce parallel competing authorities.

## 1. Repository evidence inventory

| Capability | Evidence found in repository | Status interpretation | Next action |
|---|---|---|---|
| Blind model/agent comparison | `.agents/skills/blind-agent-evaluation/SKILL.md` | Existing procedure covers opaque treatment IDs, correctness-first scoring, leakage, uncertainty, replication, unblinding and MoneyBall/3L0 | Extend with judge calibration and tournament result schema; avoid replacing it |
| Adaptive wait/reconciliation | `.agents/skills/adaptive-wait/SKILL.md` | Existing mandatory loop re-fetches SHA, workflows, jobs, steps/logs/artifacts, reviews/comments and resulting state | Use as execution protocol for every PR change; only current-SHA evidence counts |
| Context graph | `.agents/skills/context-relationship-graph/SKILL.md` | Existing relationship graph skill | Connect issue → PR → commit → workflow → artifact → claim nodes and preserve edge confidence |
| Evidence envelope | `docs/ops/EVIDENCE-ENVELOPE.schema.json`, `.github/skills/evidence-envelope/SKILL.md` | Existing schema/skill; should be canonical candidate for evidence envelopes | Reuse after checking schema compatibility; do not invent a second envelope without migration |
| MoneyBall/3L0 | `docs/ops/HEX-MONEYBALL-INTEGRATION.md`, `docs/ops/ACTION-EFFECT-EVENT.schema.json`, `docs/ops/MANAGER-TOURNAMENT.schema.json` | Existing multi-agent telemetry and manager decision contract | Make new tournament outputs map to current run/attempt/call/score/decision keys |
| Internal tournament | `deepcli/deepcli/observatory/tournament.py` | Existing campaign-level ranking records trials to a leaderboard and returns winners/losers | Reconcile with new offline scorer; prefer one shared result schema and no duplicate leaderboard truth |
| SHE integration ledger | `docs/ops/SHE-INTEGRATION-FINDINGS.md` | Explicitly describes GitHub Actions + repository corpus as durable evidence; Hex as consumer | Update this ledger when a connector or adapter is actually verified |
| Langfuse / Phoenix | Existing project notes in `docs/ops/SHE-INTEGRATION-FINDINGS.md` and the Notation Registry proposal describe neutral event schema, Langfuse optional rich-trace experiment, Phoenix optional local/open experiment | Architecturally documented, not proof either is currently connected/live | Add exporters behind an opt-in adapter; preserve metadata-only privacy contract |
| SWE evaluation | `docs/evaluations/swe-performance/README.md`, `scripts/ci/swe_evaluation_contract.py`, `.github/workflows/swe-reference-evaluation.yml` | Existing manual, bounded, redacted reference adapter; completed run is not confirmed issue resolution | Keep repository lifecycle metrics primary; use SWE as separate context signal |
| CodeQL | `.github/workflows/codeql-advisory.yml` | Existing scheduled/PR/manual advisory scan for Actions, JS/TS and Python; no merge gate in inspected workflow | Track findings and workflow result; do not silently convert advisory to blocking gate |
| OpenSSF Scorecard | `.github/workflows/scorecard-advisory.yml` | Existing advisory workflow with image digest preflight and SARIF publication | Preserve pinned/digest-verified supply chain and advisory boundary |
| Performance/complexity | Existing ATES/WTCV discussion, complexity fallback and candidate AST providers in project notes | Metric design exists; providers and longitudinal comparability require validation | Compare Tree-sitter/Lizard/Radon as versioned measurement providers; don't gate merges on throughput alone |
| Taxonomy/classifier | Current PR's classifier registry/question bank and versioned taxonomy | Partial implementation plus proposed taxonomy | Measure coverage from executed case IDs, not taxonomy row counts |

## 2. External inspiration: adopt the mechanism, not the dependency by default

| Project / standard | Useful pattern | Integration recommendation | Primary source |
|---|---|---|---|
| DSPy | Typed LM modules, metric-driven optimization and optimizers | Research/optional adapter. Optimize on train/validation only; hold out regression and safety sets; store prompt/program/config hashes. No direct DSPy path was found in the inspected master tree. | https://github.com/stanfordnlp/dspy ; https://dspy.ai/ |
| Langfuse | Tracing, evaluation, datasets and feedback | Optional exporter/consumer for the canonical event envelope; avoid making it the source of truth. Existing docs mention the architecture, but current live connection is not established by this inventory. | https://github.com/langfuse/langfuse ; https://langfuse.com/docs |
| Arize Phoenix | Local/open AI tracing and evaluation workflows | Parallel optional consumer for controlled comparison with Langfuse; same sanitized events and same evaluation IDs. Current live connection is not established. | https://github.com/Arize-ai/phoenix ; https://arize.com/docs/phoenix |
| SWE-bench | Issue-grounded patch evaluation | Existing local reference adapter is the entry point; keep external benchmark resolution separate from repo lifecycle metrics. | https://github.com/swe-bench/SWE-bench ; https://www.swebench.com/SWE-bench/ |
| CodeQL | Semantic static analysis | Already integrated as advisory workflow; preserve pinned actions, minimal permissions and result provenance. Review GitHub product/usage terms for intended deployment. | https://codeql.github.com/docs/ ; https://docs.github.com/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning-with-codeql |
| OpenTelemetry GenAI | Vendor-neutral trace attributes and event semantics | Align common fields, then write optional Langfuse/Phoenix exporters. Avoid storing raw prompts, completions, secrets or repository payloads by default. | https://opentelemetry.io/docs/specs/semconv/gen-ai/ |
| OpenSSF Scorecard | Repository supply-chain posture signals | Already integrated as advisory; use individual findings with context, not a single score as a security guarantee. | https://github.com/ossf/scorecard ; https://openssf.org/blog/2024/04/17/beyond-scores-with-openssf-scorecard-granular-structured-results-for-custom-policy-enforcement/ |
| Inspect AI | Composable task/solver/scorer evaluation | Evaluate as a potential adapter to the question bank; do not run a second dataset of truth without explicit mapping. | https://github.com/UKGovernmentBEIS/inspect_ai ; https://inspect.aisi.org.uk/ |
| Promptfoo | Prompt/agent scenario tests and red-team tests | Optional security/regression adapter, using sanitized fixtures and bounded provider calls. | https://github.com/promptfoo/promptfoo ; https://www.promptfoo.dev/docs/ |
| MLflow / DVC | Experiment and dataset lineage | Defer dependency until GitHub Actions + JSONL receipts demonstrably fail to meet scale needs. Could be read-only consumers first. | https://github.com/mlflow/mlflow ; https://github.com/iterative/dvc |
| CodeCarbon | Energy/emissions estimates | Optional measurement provider for controlled benchmark runs; record hardware, region/grid assumptions and estimator version. Never treat estimate as precise meter data. | https://github.com/mlco2/codecarbon ; https://docs.codecarbon.io/ |
| Tree-sitter / Lizard / Radon | Structural complexity measurements | Treat as competing versioned providers. Record provider/version/language and compare variance before using in longitudinal scoring. | https://tree-sitter.github.io/ ; https://github.com/terryyin/lizard ; https://github.com/rubik/radon |
| GitHub REST/GraphQL | Issues, comments, reviews, commits, checks and artifacts | Build claim/evidence relationships from canonical IDs/URLs and SHA; preserve event authorship/time; never infer quality from reactions or commit messages. | https://docs.github.com/en/rest ; https://docs.github.com/rest/pulls/pulls |

External repositories, datasets, models, weights, hosted APIs, and documentation each have separate terms. Verify the exact revision and license/terms before copying or integrating; the table is a research map, not legal clearance.

## 3. System One vs System One: evaluation protocol

Use the existing blind-agent-evaluation skill as the policy owner and the MoneyBall/evidence envelope as the data contract.

1. Freeze task definition, rubric, dataset split, allowed tools, timeout and resource budget.
2. Assign opaque candidate IDs; preserve protected model/runtime/adapter provenance separately.
3. Run the same cases and constraints against each candidate. Keep provider errors, timeouts, throttling, invalid output and task failures as different outcome classes.
4. Score objective ground truth first. Candidate-to-candidate or LLM-as-judge scores are additional signals, never ground truth by default.
5. Blind pairwise outputs; randomize left/right order; include reversed repeats and known control pairs.
6. Calibrate judges against human/adjudicated controls; report agreement, position bias, self-preference, variance and abstention. Quarantine uncalibrated judges.
7. Report correctness, safety, schema validity, abstention/coverage, regression severity, p50/p95/p99 latency, throughput, cost and resource use as separate dimensions.
8. Use paired bootstrap or suitable confidence intervals; preserve per-case results and missingness. Do not rank a candidate on a tiny or non-comparable sample.
9. Promote only against versioned minimum evidence and safety gates; use held-out regression sets and replicate promising outcomes.
10. Freeze receipts and hashes before unblinding, then reconcile the results into MoneyBall/3L0 and the relationship graph.

**Do not optimize speed before quality.** Existing project notes explicitly reject a hard `MIN_ATES_THRESHOLD` merge gate because it can reward task splitting or fast low-quality output. ATES is a throughput observation combined with quality/evidence dimensions, not a merge condition on its own.

## 4. Claim ledger: commits, issues, PRs, comments, checks and artifacts

Each claim needs a stable ID, exact statement, type, scope, current status, author/source, timestamps, commit SHA, relevant file/line, test name, run ID/attempt, artifact digest, and superseding evidence links.

Allowed states: `SUPPORTED`, `PARTIALLY_SUPPORTED`, `CONTRADICTED`, `UNVERIFIED`, `STALE`, `NOT_APPLICABLE`.

Rules:
- Commit/PR text establishes intent, not behavior.
- A test proves only the exercised contract.
- An HTTP success proves reachability, not semantic correctness.
- A completed SWE adapter run is not confirmed benchmark resolution unless a reviewed scorer proves it.
- Provider throttling or missing output is an infrastructure/observation result, not a model-quality score.
- A green job on an old SHA is historical evidence, not proof for a newer head.
- PR comments and bot triage are attributed observations; do not silently promote them into verified facts.
- Relationship edges should be typed and confidence-scored: issue `IMPLEMENTS_IN` PR, PR `CONTAINS` commit, commit `CHANGES` file, workflow `VALIDATES` SHA, artifact `EVIDENCES` claim, comment `ASSERTS` claim.

## 5. Privacy and supply-chain requirements

- Use metadata-first telemetry; no raw prompts/completions, arbitrary tool payloads, repository content, credentials or free-form logs in shared analytics by default.
- Hash sensitive rationale/message material before export when a fingerprint is sufficient.
- Pin actions and dependencies; preserve source SHA, adapter version, model identifier and config/prompt hashes.
- Separate provider terms, repository code licenses, dataset licenses, model/weight licenses and generated-output terms.
- Require a recorded license/terms review before adopting copied code or datasets. Clean-room reimplementation is not automatic clearance for copied expression, data, model weights, patents, trademarks or service terms.
- Keep optional integrations optional: the durable GitHub Actions/repository corpus remains authoritative; analytics tools consume evidence.

## 6. Prioritized implementation plan

### P0 — reconcile before adding more
- Compare `scripts/eval_tournament.py` with `deepcli/deepcli/observatory/tournament.py`, leaderboard APIs, `MANAGER-TOURNAMENT.schema.json`, `EVIDENCE-ENVELOPE.schema.json` and `3l0.moneyball.v1`.
- Select one canonical result schema; retain the simple script only as an offline fixture/CLI if it maps exactly.
- Add an integration inventory generator or test that detects key workflow/doc paths so documentation doesn't drift.
- Add explicit run SHA + run attempt + candidate/task IDs to every evaluation receipt.

### P1 — improve evidence quality
- Add blinded pairwise evaluation, order reversal, judge controls, abstention and confidence interval reporting.
- Add a claim ledger linking issue/PR/comment/commit/check/artifact with typed relationships and stale evidence detection.
- Ensure the classifier bank has measurable coverage for all task families before calling it representative.

### P2 — instrument performance and messages
- Emit sanitized OpenTelemetry-compatible spans and per-hop metrics from existing runtime boundaries.
- Add optional Langfuse and Phoenix exporters behind configuration; verify each with a no-secret smoke test.
- Benchmark concurrency and latency under matched conditions. Add CodeCarbon only if energy measurement has a defined decision use.

### P3 — research adapters behind opt-in gates
- Evaluate DSPy as a training/optimization adapter with strict split hygiene.
- Expand the existing SWE reference adapter only after scorer and redaction contracts remain intact.
- Evaluate Inspect AI and Promptfoo against the canonical bank before introducing either dependency.
- Keep CodeQL and Scorecard advisory until explicit policy, false-positive handling and authorized branch-protection requirements justify a blocking gate.

## 7. Verification status

This inventory was based on inspecting the `master` tree and these repository sources:
- `docs/ops/SHE-INTEGRATION-FINDINGS.md`
- `docs/ops/HEX-MONEYBALL-INTEGRATION.md`
- `.agents/skills/blind-agent-evaluation/SKILL.md`
- `.agents/skills/adaptive-wait/SKILL.md`
- `deepcli/deepcli/observatory/tournament.py`
- `docs/evaluations/swe-performance/README.md`
- `.github/workflows/swe-reference-evaluation.yml`
- `.github/workflows/codeql-advisory.yml`
- `.github/workflows/scorecard-advisory.yml`

The inspected master tree contains **9,178 paths**. No direct DSPy integration path was found in the targeted path search; that does not prove the dependency is absent from every lockfile or indirect code path. Langfuse/Phoenix are documented as optional architecture, not verified live services. CodeQL, Scorecard, and SWE reference artifacts have explicit repository files/workflows.

Research sources from Liner:
- https://github.com/stanfordnlp/dspy
- https://github.com/langfuse/langfuse
- https://github.com/Arize-ai/phoenix
- https://github.com/swe-bench/SWE-bench
- https://github.com/UKGovernmentBEIS/inspect_ai
- https://github.com/promptfoo/promptfoo
- https://opentelemetry.io/docs/specs/semconv/gen-ai/
- https://codeql.github.com/docs/
- https://github.com/ossf/scorecard
- https://github.com/mlco2/codecarbon
- https://github.com/terryyin/lizard
- https://github.com/rubik/radon
