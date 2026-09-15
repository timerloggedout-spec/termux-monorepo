# Agent Observability & Complexity Research Matrix

## Decision principle

**Quality > time.** Time-to-integration and wait latency are performance dimensions; they are not substitutes for correctness, integration quality, validation, or attribution confidence.

The research candidates should be compared as **parallel adapters/providers against the same evidence contract**, not adopted as mutually exclusive architecture.

## Priority matrix

| Candidate | Primary contribution | Integration target | Priority | Promotion stance |
|---|---|---|---|---|
| OpenTelemetry | neutral trace/span transport | GitHub Actions + agent invocation boundary | P0 | canonical interoperability layer |
| Langfuse | traces, datasets, experiments, scores | optional experiment/eval adapter | P1 | observational; no source-of-truth authority |
| Phoenix | open-source tracing, evals, datasets, experiments | optional experiment/eval adapter; Docker-friendly lab | P1 | observational; no source-of-truth authority |
| Tree-sitter | structural syntax trees | complexity feature provider | P1 | measurement only |
| Lizard | multi-language NLOC/CCN/token/parameter metrics | fast baseline complexity provider | P1 | measurement only |
| Radon | Python CCN/Halstead/maintainability metrics | Python-specific complexity provider | P1 | measurement only |
| Docker | reproducible local/CI experiment environment | instrument/eval parity harness | P1 | environment, not evidence source |
| Codespaces | reproducible interactive developer/agent environment | operator/agent reproduction lane | P2 | environment, not evidence source |
| MASEval / agent benchmark suites | multi-agent evaluation patterns | future manager tournament cohorts | P2 | research input; adopt only after local evidence schema mapping |
| Langfuse/Phoenix external adapters | vendor-specific persistence/UX | adapters over canonical JSONL/OTEL events | P2 | never replace canonical corpus |

## Why Langfuse deserves attention

Langfuse supports datasets, experiments, scores, live traces, and OpenTelemetry-based experiment ingestion. Its experiment model is especially relevant to manager tournaments because the same dataset can be replayed across conditions and evaluated consistently.

Research links: https://langfuse.com/docs/evaluation/overview · https://langfuse.com/docs/evaluation/experiments/experiments-via-opentelemetry · https://langfuse.com/docs/evaluation/experiments/data-model

**Best fit here:** export the sanitized agent execution event stream into an adapter that can associate a cohort/experiment ID with traces and scores. Keep GitHub corpus/receipts authoritative and treat Langfuse as a research surface.

## Why Phoenix deserves a parallel lane

Phoenix is open source, uses OpenTelemetry/OpenInference, and combines tracing, evaluations, datasets, and experiments. Its experiment workflow explicitly compares versions against the same dataset and evaluation criteria; it also supports repetitions and dataset splits, which are useful for variance/consistency analysis in manager tournaments.

Research links: https://arize.com/docs/phoenix · https://arize.com/docs/phoenix/get-started/get-started-datasets-and-experiments · https://arize.com/docs/phoenix/datasets-and-experiments/how-to-experiments

**Best fit here:** a Docker/self-hostable research lane that consumes the same sanitized events and cohort definitions as the Langfuse adapter. Do not choose between Phoenix and Langfuse before a like-for-like comparison exists.

## Complexity scoring track

The first implementation should preserve the existing structural fallback:

```text
C_structural = ln(1 + additions + deletions) × sqrt(files_changed)
```

Then add optional providers without changing the base metric contract:

```text
C_explicit       = declared task complexity when available
C_structural     = churn/files fallback
C_ast            = Tree-sitter structural features
C_ccn_multilang  = Lizard CCN/NLOC/token/parameter features
C_python         = Radon CCN/Halstead/maintainability features
```

Lizard provides NLOC, cyclomatic complexity, token count, and parameter count across many languages. Radon provides Python cyclomatic complexity plus raw, Halstead, and maintainability metrics. Tree-sitter provides concrete syntax trees suitable for structural analysis.

Research links: https://github.com/terryyin/lizard · https://radon.readthedocs.io/en/latest/ · https://tree-sitter.github.io/tree-sitter/using-parsers/2-basic-parsing.html

These are **feature providers**, not competing truth sources. The reducer should preserve provider name, version, raw features, derived complexity, and confidence so future formulas can be compared without rewriting history.

## Parallel experiment design

For a bounded comparable task cohort:

```text
                    SAME TASK COHORT
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
       GitHub JSONL     Langfuse          Phoenix
       canonical        adapter           adapter
          │                │                │
          └────────────┬───┴───────┬────────┘
                       ▼           ▼
                 SAME EVIDENCE  SAME EVALS
                       │           │
                       └─────┬─────┘
                             ▼
                    3L0 / Moneyball reducer
```

Compare:

- task completion and final acceptance;
- time-to-integration;
- feedback cycles;
- useful vs duplicate actions/tokens;
- retries and conflicts;
- human intervention;
- provider/model failures;
- attribution confidence;
- validation/check outcomes;
- realization ratio / Action→Effect follow-through;
- TCV/WTCV/TPV/RPI/action density/parallel yield/ATES;
- complexity-adjusted variants;
- variance across repetitions.

A provider wins an experiment only when it improves **evidence quality or decision quality** at acceptable operational cost. Convenience or dashboard polish is not sufficient.

## Docker + Codespaces

Docker and Codespaces should form the environment-parity track:

1. define the same sanitized event contract;
2. run the same bounded task cohort in reproducible environments;
3. capture identical lifecycle events;
4. compare environment-induced failures separately from model/provider failures;
5. preserve the environment fingerprint with the observation.

Credentials remain external to the image/workspace. Broad PAT/connector scope is not a reason to embed secrets in source, telemetry, or artifacts. The dangerous-operation boundary remains explicit.

## Phase gates

### Phase A — instrument

Canonical JSONL event schema + runtime watcher + immutable SHA/run linkage.

### Phase B — complexity

Structural fallback + Lizard/Radon providers; Tree-sitter as the language-neutral structural expansion.

### Phase C — parallel evaluation

Run equivalent cohorts through GitHub-only, Langfuse-adapter, and Phoenix-adapter paths.

### Phase D — environment parity

Docker and Codespaces reproduction lanes; classify environment failures independently.

### Phase E — manager tournament

Compare orchestration policies, not isolated model leaderboard scores. Retain experiment history, cull weak policies, and preserve useful behaviors.

## Non-goals

- no speed-only merge gate;
- no vendor becomes the canonical evidence source;
- no synthetic zeroes for missing complexity/telemetry;
- no causal attribution from trace timing alone;
- no benchmark score treated as universal model quality;
- no secret/PAT material in telemetry or artifacts.
