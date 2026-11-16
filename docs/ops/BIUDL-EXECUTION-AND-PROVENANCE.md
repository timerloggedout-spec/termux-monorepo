# BIUDL: execution, attribution, evidence, and source curation

**Status:** implementation program and acceptance contract.  
**Parent:** [initiative #1241](https://github.com/timerloggedout-spec/termux-monorepo/issues/1241).  
**Canonical implementation slice:** [PR #1243](https://github.com/timerloggedout-spec/termux-monorepo/pull/1243) (briefing contract validation); this document adds cross-lane provenance and citation curation.

## Operating rule

Reuse existing control planes. The repo already has the [Agent Evidence Substrate](AGENT-EVIDENCE-SUBSTRATE.md), [Agent Team Orchestration](AGENT-TEAM-ORCHESTRATION.md), [Agent Team Roster](AGENT-TEAM-ROSTER.md), [Agent Monikers SSOT](AGENT-MONIKERS.md), [Agent Evaluation Framework](../architecture/AGENT-EVALUATION-FRAMEWORK.md), [Foresight Evidence Spine](FORESIGHT-EVIDENCE-SPINE.md), closed ATES event schema/reducer, the read-only `agent-throughput-evidence` observer, provider catalog (`../schemas/agent-roster.yaml`), Scout missions, manager MVT/continuous evaluation, Hindsight integration, and Pinggy/bridge publishing. The existing MCP admission, edge inference, and manager tournament schemas remain the domain contracts. Do not create a competing orchestrator, telemetry store, or source-of-truth. Extend these contracts at their existing boundaries.

The execution loop is:

`RECON → PLAN/MEASURE → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT`

Committed, executed, validated, and promoted are separate states. Queued is not complete; cancelled is not success; a failed check is not automatically rerun to make the board green.

## Cross-lane implementation phases

| Phase | Integrated work | Acceptance evidence |
|---|---|---|
| P0 Baseline | Existing repo gate + ATES quality lane + closed schemas | Tests run on current head; exact SHA and run attempt recorded |
| P1 Research | Daily digest, ingest, Foresight Radar, source registry, citation ledger | Every extracted URL keeps source document/item context; claims retain evidence status, horizon, confidence, unresolved questions |
| P2 Procurement | Inspectable FOSS matrix, tested target claims, runtime/evidence lock-in | No adoption claim without source/version and tested-target evidence |
| P3 Orchestration safety | Manager/Scout/Orchestrator roles and execution adapter provenance | Scouts propose; managers decide; route and run identity recorded; no PAT-based model attribution |
| P4 Telemetry/evaluation | Extend ATES with `author` provenance and GitHub actor metadata | Provider/model only when evidenced; missing model/settings/context remain null; quality > throughput |
| P5 Engineering integrity | Deterministic citation extraction, closed author schema, tests | Offline, stable JSONL; malformed source data fails loudly; no secrets/raw prompts/context |
| P6 Edge/bridge | Retain ARM/Android/Termux/offline test claims and Pinggy runtime receipts as separate infrastructure evidence | Device/transport status is observed, TTL-bounded, opaque device IDs only; no hardware identifiers or credentials |

This is one integrated delivery surface, not a claim that all existing downstream runtime experiments have already executed.

## Contributor/author provenance

GitHub identity is not agent identity. A PAT can make a human, workflow, or agent-mediated commit appear as `timerloggedout-spec`. Do not infer provider/model from that account name, commit author, or commit message.

Every normalized ATES event may carry a closed `author` object:

- `provider`, `model`, `adapter`, `role`, `identity_kind`
- `settings_fingerprint`, `context_fingerprint`: SHA-256 only, never raw settings, prompt, context, secrets, or session text
- `attribution_method`, `confidence`, `evidence_refs`

The observer can map a known workflow name to a provider/role. This is **workflow-level attribution**, not proof that the provider generated every line of a commit. Model identity remains null until an invocation boundary provides trusted evidence. A workflow-level manager/scout label does not imply a provider/model identity. GitHub `actor` and `triggering_actor` are retained separately from `author`.

Confidence is not truth: preserve evidence references and the attribution method. Historical attribution from commits, reviews, comments, session exports, or PAT use remains inferred unless tied to invocation/run evidence. Do not ingest prompts, completions, raw tool arguments, credentials, browser profiles, or arbitrary comment text into canonical telemetry.

## Source curation and citations

`scripts/ci/curate_briefing_sources.py` extracts HTTP(S) citation instances from dated briefing JSON, Markdown, and the existing JSONL resource/procurement/radar records. Its output is deterministic and offline:

```sh
python3 scripts/ci/curate_briefing_sources.py --output data/briefing/source-citations.jsonl
python3 -m unittest tests.test_curate_briefing_sources -v
```

Each citation records the URL, source file, item identifier/headline when present, source type, version, publication/observation date, evidence status, horizon, confidence, and a stable citation ID. The same URL cited in different documents/items remains separately traceable. Exact duplicate citation instances are deduplicated. The extractor is not a web fetcher and does not certify that a cited claim is true.

The curated corpus covers the standing digest contracts and source registry plus the existing briefing snapshots and integration material, including:

- `data/briefing/briefings/2026-09-30.json`
- `docs/briefing/2026-10-04-collaborator-ingest.json`
- `docs/briefing/CONTRIBUTOR-INTEGRATION-2026-09-30.md`
- `data/briefing/resources.jsonl`, `data/briefing/procurement.jsonl`, `data/briefing/radar.jsonl`
- agent orchestration, scout missions, ATES metrics, evidence spine, Hindsight integration, Actions metrics, and Pinggy bridge documentation

Canonical source discipline remains defined by:
- `docs/briefing/DAILY-DIGEST-SPEC.md`
- `docs/research/BRIEFING-INGEST.md`
- `docs/research/FOSS-PROCUREMENT-MATRIX.md`
- `docs/research/FORESIGHT-RADAR.md`
- `config/foresight_digest_sources.json`
- `docs/ops/FORESIGHT-EVIDENCE-SPINE.md`

The dated brief is a snapshot; source/resource/radar JSONL is append-oriented evidence. Corrections should append new observations rather than erase historical provenance. Images are contextual enrichment, never evidence.

## Collaborator management and evaluation

Use the existing team roles and workflows:

- **Scout**: discovers providers, sources, candidates, regressions, and experiments; emits proposals, never authority.
- **Manager**: chooses task cohort, policy, sequencing, concurrency, escalation, and culling; owns integrated outcome.
- **Orchestrator/conductor**: prevents duplicate work and conflicting writes, waits on dependencies, records routing envelopes and outcomes.
- **Specialists/reviewers**: implement or critique bounded slices; findings need disposition and verification.
- **Evidence collector**: records workflow/run attempt, job/step, SHA, PR/issue, provider/model when available, artifact hash, outcome, and attribution confidence.
- **Pinggy/bridge publisher**: infrastructure evidence only; status and TTL do not establish agent identity or successful task execution.

Evaluate manager policies on comparable tasks and cohorts using correctness, integration, test evidence, review findings, retries, conflicts, human intervention, time, context/token cost when actually measured, provider failures, and attribution confidence. ATES/WTCV is observational; it is not a speed-only merge gate. Do not crown a manager on one successful run. Preserve failures and cancellations as observations.

## Security and authority

- No secret values, PATs, cookies, prompts, completions, raw settings, or raw context in logs/artifacts/citations.
- Use SHA-256 fingerprints for settings/context; missing fingerprints stay null.
- Keep workflow permissions least-privilege and evidence observers read-only.
- No blind retries after ambiguous outcomes; reconcile state or use idempotency.
- No automatic production adoption or merge based solely on vendor claims, inferred attribution, speed, or one benchmark.
- Test target-specific portability separately for ARM64 Linux, x86_64 Linux, Android, Termux, and offline/air-gapped use.
