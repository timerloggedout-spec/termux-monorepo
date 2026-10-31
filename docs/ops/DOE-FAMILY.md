# DoE Family — MVT Is One Member, Not the Whole

Owner direction (2026-10-27, issue #1865): DoE becomes a **family**.
MVT is one member, not the whole. This document is the family's
structure record; `docs/ops/MVT-DOE-ATES-SEPARATION.md` remains the
ownership spec for the surfaces.

## Members

| Member | Kind | State | Primary home |
|---|---|---|---|
| MVT campaigns | member (existing) | active practice | MVT surface (`mvt.html` / `mvt-feed.json`) — the DoE surface carries a pointer only, never the payload |
| Pilot 1 — context routing × CedrLang compression (#1849) | campaign | admitted (design record committed); executed — see campaign dir | `experiments/doe/pilot-1-context-routing-x-compression/` |
| Pilot 2 — dispatch topology × quota policy (#1850) | campaign candidate | proposal only — **not admitted** (no design record, no run evidence) | issue #1850 |
| Future design classes | campaign types | taxonomy in `docs/ops/DOE-TAXONOMY.md`: implemented generators today = full factorial + Taguchi L9 (fractional orthogonal array); fractional factorial, Plackett–Burman, sequential = skill-named, no generator; foldover, central composite, Box–Behnken, RSM, mixture, split-plot, Latin hypercube = candidates. Randomized assignment (`mvt_shuffle`) is an assignment mechanism, not a design class | DoE surface |

## Family-level shared

- **Experiment record schema** — `docs/ops/corpus/EXPERIMENT.schema.json`
  ("DOE/MVT Experiment Record", schema_version 1.0). Primary home is the
  MVT surface per the separation spec; the family **adopts** it: every
  family campaign run emits one record conforming to it, validated in
  tests (`tests/test_doe_family.py`). One dispatched/executed run = one
  record = one observation.
- **Feed sections** — `doe-feed.json` carries, per member: designs /
  campaigns / results. A member with no results renders its state
  exactly (design-only, proposal-only), never a borrowed result.
- **Intake rule** — a campaign joins the family only with a committed
  **design record + run evidence** (EXPERIMENT-conforming records).
  Proposals alone don't count.
- **Evaluation doctrine** — parallel lanes under a shared capability
  contract; scoring distinguishes execution status → task outcome →
  correctness → integration → regression → resource cost (multivariate-doe
  skill outcome model); 🍒-pick customizations are recorded as new
  cohort/version, never silently folded into a running design (skill
  rule 12).

## Configured-instance identity (recorded 2026-10-30; true since init)

Correction of framing (owner, 2026-10-30): configured instances
have been the case since init — the lag was in our records/spec,
not in the setup. This section records what was always true.

`model@version` is NOT a sufficient identity under the DoE. One
provider model@version runs as DIFFERENT configured instances —
distinct system prompts, distinct tools, per role/context. Every
DoE record keys the executing instance by its configuration, in
`treatment.instance` (EXPERIMENT.schema.json):

```
{provider, model@version (verbatim), system_prompt {ref, sha256},
 tools {ref, sha256}, role, moniker, context, instance_key}
```

**Ref scheme (named by this lane — the refs as they exist; the fleet stamps the same refs):**
a ref is a repo-relative **path** when the artifact lives in the
repo (a prompt file, a tool manifest); otherwise a **scoped id** —
`prompt:<moniker>:<slug>` or `tools:<moniker>:<slug>`. Every ref
travels with the **full SHA-256** of the exact content as
dispatched: prompt text for prompts; manifest bytes for tools when
a manifest exists, else the canonical tool set (sorted tool names
joined by `\n`). Compact stamp form: `<ref>#<sha256[:12]>`.
`instance_key` = SHA-256 of the canonical tuple JSON (helper:
`scripts/doe/instance_key.py`). Aggregation, comparison, and quota
attribution group by `instance_key` — never by model alone; two
instances sharing a model@version are different experimental units
and their results are never pooled.

Pilot-1 retro-identification (records are immutable evidence and
are NOT rewritten): its executing instance was the offline harness —
provider `local`, model `offline-harness@1`, system_prompt and
tools both ref `scripts/doe/run_pilot1.py` (sha256
`7931ec226e8ea1a4694a548d326269d4528513ba36b14469687f43586fc42bcd`),
role `extractor`, moniker `doe-expert`, context
`pilot-1 offline-deterministic`. New campaigns stamp
`treatment.instance` at run time.

### Provider-schema mappings (2026-10-30)

Standing rule: EVERY surface carrying its own provider/model
config schema adds a mapping row here (or in its own doc, cited
here) BEFORE its results join attribution or comparison. A field
the surface does not carry is recorded NOT ESTABLISHED — never
silently collapsed into a model-only key. Mapped so far:
HindSight (below), DSPy-DoE, the SWE evaluation contract. Census
continues (same treatment owed): `.github/connectors/llm_providers.yaml`,
`ops/delphi/panel.json`, `.github/agentic/provider-command-library.json`,
the quota registry's model lane — rows land with their owning
lanes.

### HindSight provider-schema mapping (2026-10-30)

HindSight carries its own provider schema — per function role:
`HINDSIGHT_API_{LLM|EMBEDDINGS|RERANKER}_{PROVIDER|MODEL}` (set by
the deploy workflows). A mapping IS needed, at exactly one seam:
whenever HindSight activity is attributed or compared (quota
attribution, DoE records, dispatch stamps), its rows must translate
into configured-instance terms — HindSight's schema has no
prompt/tools fields and its role axis is the function, so an
unmapped join collapses distinct instances. The need is proven on
master today: two deployments share the schema with different
values (Fly `hindsight-termux`: LLM openrouter /
`openai/gpt-4o-mini`, embeddings google / `text-embedding-004`;
Koyeb: LLM openrouter / `meta-llama/llama-3.1-8b-instruct:free`,
embeddings google / `gemini-embedding-001`; reranker `rrf` in
both).

| HindSight schema | instance field |
|---|---|
| `HINDSIGHT_API_<ROLE>_PROVIDER` | `provider` |
| `HINDSIGHT_API_<ROLE>_MODEL` | `model` (verbatim) |
| function role (LLM / EMBEDDINGS / RERANKER) | `role` = `hindsight-llm` / `hindsight-embeddings` / `hindsight-reranker` |
| deployment + bank (e.g. `fly:hindsight-termux`, bank id) | `context` |
| — (the service itself) | `moniker` = `hindsight` |
| — (upstream server-internal) | `system_prompt` ref `prompt:hindsight:server-internal`, `tools` ref `tools:hindsight:server-internal`; sha256 **NOT ESTABLISHED** (upstream vectorize-io internals, not in this repo — never invented) |

Edges: the `rrf` reranker has no model — its `model` is `rrf`
(the algorithm is the engine). HindSight's memory-content schema
(world facts / experiences / observations / mental models) is
unrelated to provider identity and needs no mapping. The deploy
configs themselves are unchanged by this mapping.

## The entire repo is the experiment (owner, 2026-10-30)

Correction of the "lab still to build" framing: there is no
separate lab coming. The repo in production IS the experiment
floor, and it is already running. Every selection a Scout,
Manager, Orchestrator, or Operator surface makes among configured
instances is a selection experiment; every model-flow hand-off
(instance A → instance B mid-task) is a treatment transition —
the hand-off policy is itself a factor; every Chronomancer code
comparison is outcome measurement over time; every set of
concurrent parallel competing builds is a set of arms. Production
code is the task suite and the environment.

The DoE discipline over this floor is instrumentation + design,
not construction:

- **Designed where deliberate:** a choice made on purpose gets
  the campaign treatment (DESIGN record, factors, pre-registered
  threshold) before it runs.
- **Stamped always:** every run keys its configured instance
  (`treatment.instance` / instance_key); hand-off transitions
  stamp BOTH instances and the transition point.
- **Recorded honestly:** designed runs emit EXPERIMENT-conforming
  records; undesigned production runs are recorded as
  OBSERVATIONAL (schema `provenance`/`confidence` carry that
  status) — never retroactively dressed as designed.
- **Verdicts stay disciplined:** comparisons (Chronomancer rows,
  cohort results, selection outcomes) judge against
  pre-registered thresholds where they exist, and report
  descriptively where they don't.

Instrumentation gaps — the actual remaining work, named: most
production surfaces emit no experiment record today (hand-off
transitions unstamped; Chronomancer comparisons not emitted as
records; selection decisions logged as prose, not rows). Closing
them is per-surface record emission under the provider-schema
mapping rule above — surface by surface, not a new platform.

## Binding rules (from #1865 + separation spec)

1. One primary home per record. Cross-surface references are citations
   (pointer + label), never copied payload.
2. The Delphi cycle record's presentation on this surface is REQUIRED
   with full payload + `owner_surface: delphi` — and is never counted
   or relabeled as a DoE campaign result.
3. DoE's own results come only from family campaigns' committed records.
4. Counts are live-derived at report time.

## Campaign layout

```text
experiments/doe/<campaign-id>/
  DESIGN.json    # design record: hypothesis, factors/levels, blocks,
                 # outcomes, execution environment, quota note
  records/       # one EXPERIMENT.schema.json-conforming JSON per run
  SUMMARY.json   # aggregates + factorial effects, produced by the runner
  README.md      # method, honesty limits, how to re-run
```

Runner: `scripts/doe/run_pilot1.py` (deterministic, offline; re-running
regenerates records + summary — `observed_at`/elapsed are run stamps).

### DSPy-DoE mapping (2026-10-30)

The DSPy-DoE stub (`scripts/model_selection_market/dspy_doe.py`)
records arms as {lane, arm_id, signature, model_id, role} — keyed
by `model_id` alone (default `stealth/ox-alpha`). In DSPy the
Signature IS the program/prompt spec, so: `signature` →
`system_prompt` ref (the signature's code path; sha256 over its
source at run time); `model_id` → provider/model split at the
first `/` (prefix = provider, remainder = model@version);
`role` → `role` verbatim; the arm's module/tools (DSPy modules +
tool calls) → `tools` (NOT ESTABLISHED in the stub today — records
carry no tool field); `arm_id` + lane → `context`. Until the stub
stamps `treatment.instance`, its rows join comparisons by
(signature, model_id, role) — never by model_id alone.

### SWE evaluation-contract mapping (2026-10-30)

The SWE contract (`scripts/ci/swe_evaluation_contract.py`) keys
result manifests by bare `model_id` — but the manifest already
carries the configuration in other fields: `reference`
(`mini-swe-agent` | `swe-agent`) + `reference_revision` (40-hex)
identify the configured harness — its prompts and tools live in
that revision. Mapping: `reference@reference_revision` →
`system_prompt` + `tools` refs (one artifact: the harness
revision; sha256 NOT ESTABLISHED — the revision sha is the pin);
`model_id` → provider/model split at the first `/`; `benchmark` +
`split` + `slice` → `context`; `reference` → `role`
(`swe-agent-runner` class); the running lane → `moniker` (NOT in
the manifest — NOT ESTABLISHED gap, named for the SWE lane).
Cohort comparisons (`docs/evaluations/swe-performance/COHORTS.md`)
must group by (reference@revision, model_id), never model_id
alone: the same model under mini-swe-agent vs swe-agent is two
configured instances.
