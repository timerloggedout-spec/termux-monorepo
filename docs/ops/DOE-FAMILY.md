# DoE Family — MVT Is One Member, Not the Whole

Owner direction (2026-10-27, issue #1865): DoE becomes a **family**.
MVT is one member, not the whole. This document is the family's
structure record; `docs/ops/MVT-DOE-ATES-SEPARATION.md` remains the
ownership spec for the surfaces.

**Owner definition (2026-10-31, governing ∀ lanes): DoE =
DESIGN OF EXPERIMENTS 🧪.** The repo itself is a continuous
experiment-design surface: randomized mixes (`rnd`), 🧬
evolutionary CULLING toward Top Performance, 🍒⛏️ cherry-picked
slices ∧ features propagated into new additions. DoE names
evaluative experiment campaigns over the living repo — ¬ a
document store. Every use of "DoE" in every lane reads this way;
the mechanisms (randomized mixes, culling, cherry-pick
propagation) are first-class campaign operations, with culls ∧
propagations recorded as design events in the campaign record.

## Members

| Member | Kind | State | Primary home |
|---|---|---|---|
| MVT campaigns | member (existing) | active practice | MVT surface (`mvt.html` / `mvt-feed.json`) — the DoE surface carries a pointer only, never the payload |
| Pilot 1 — context routing × CedrLang compression (#1849) | campaign | admitted (design record committed); executed — see campaign dir | `experiments/doe/pilot-1-context-routing-x-compression/` |
| Pilot 2 — dispatch topology × quota policy (#1850) | campaign candidate | proposal only — **not admitted** (no design record, no run evidence) | issue #1850 |
| FB Pages MVT-1 — copy angle × code-pool split (marketing-channel) | campaign | admitted 2026-10-31 — `executing_partial`: fb-a/fb-b live since 2026-10-27, fb-c `arm_not_started` (deviation recorded in-design); in-repo record post-launch, marked as such | `experiments/marketing/fb-pages-mvt-1/` |
| util-1-provider-rotation — desk rotation bench on live production flow (rule 6 basis; owner USE-THEM-ALL) | live, implementing | window: 24 stamped dispatches ∨ 2026-12-01; auditor weekly | `experiments/doe/util-1-provider-rotation/` |
| cmp-register — standing register of comparison examples evaluated over time (owner order 2026-11-01) | register | open — CMP-1 SKILL.md vs *.skill packaging · CMP-2 new-competition routing (dedicated opportunity channel vs fold-in; first instance .approxination) | `experiments/doe/cmp-register/` |
| nc-1-notation-compliance — notation-drift detection stack (L3 GH classifier ∧ L2 transcript sweep ⇒ L1 main relay-validation) | campaign | admitted 2026-10-31 — design-only, **pre-registered**; owner order via main: the detection TEST is a DoE experiment homed here; Tier-1 builds L3+L2; verdict ↦ main on first runs | `experiments/doe/nc-1-notation-compliance/` |
| live-2-prlane-tuning — classifier rule/threshold tuning (joint w/ tier1-classifiers-steward) | campaign | admitted 2026-10-31 — design-only, **pre-registered**; replay factorial over frozen pr-lane snapshots (live series = non-stationary, steward caveat); phase-2 levels by amendment after rule-file read | `experiments/doe/live-2-prlane-tuning/` |
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

### Test types: live development first, fragment suites are the control (owner, 2026-10-31)

Active development IS the live testing: the primary experimental
mass is real development and review work, run and recorded as
experiments (competing builds, selection decisions, hand-offs —
above). Fragment-style suites (fixed tasks scored on exact
source-fragment recovery, e.g. pilot-1 and lab-1) are a CONTROL
type: they calibrate and sanity-check the measurement machinery
against a deterministic scorer, and their use stays MINIMAL — a
control is run to anchor a comparison, never as the main body of
evidence about production. Campaigns declare `suite_type` in
their design (`control` | `live`); lab-1 is `control`.

### Mandatory provider phrases in experiments (owner, 2026-10-31)

The fleet's provider phrase sets are mandatory prompt content,
not decoration: `harmony_hub/workspace/prompts/prompt_engine.py`
(per-provider PREFIXES / SUFFIXES — the established sets are
DeepSeek-shaped, e.g. "Build the Future Now. Make it so." /
"Show me what you got. GB") and the harmony profiles
`harmony_hub/config/prompts/profiles/*.json` (e.g. `1337.json`:
system prefix incl. its emoji sequence + leet suffixes); the
Grimoire pointer `→cmd:build` ↦ the same build phrase
(`harmony_hub/config/GRIMOIRE_DICTIONARY.md`). Framing of the
work itself follows `docs/ops/DO-PHRASING-FRAMING-FRAMEWORK.md`.

Rule: when a campaign dispatches to a provider/model route with
an established phrase set, the campaign design declares it under
`provider_phrases` (keyed by the model route, verbatim) and the
runner composes prefix + campaign prompt + role line + suffix
into the dispatched system prompt — the phrases are covered by
the prompt hash, so a run without them is a DIFFERENT configured
instance and never pools with phrased runs. Where no set is
established for a route, the design records that (lab-1: none
established for its two OpenRouter routes — NOT ESTABLISHED,
recorded in its DESIGN.json, not silently skipped).

Data home (owner, 2026-10-31): the phrase sets live in their
own SSOT repo — `timerloggedout-spec/provider-phrases`
(`phrases.json`, provider-phrases/v1) — pinned into this repo
as the `ops/phrases` git submodule (a symlink cannot cross
repos; the pin is the link, bumped by PR). The JIT layer is
`scripts/doe/phrase_layer.py`: given the model route it selects
the provider set and composes the phrases between prompt
construction and dispatch, with placement / selection / form
(verbatim | leet) / profile as explicit parameters — i.e. as
design factors. The runner calls it when a design sets
`phrase_layer`; enabled-but-data-missing fails loud at plan
time. The established leet form substitutes ONLY the vowels
(a→4, e→3, i→1, o→0) — read off the 1337 profile's own
suffixes and pinned by test.

**Micro-variable kinds are evaluation dimensions (owner,
2026-10-31).** A single example stands for its whole KIND: the
`d0 > DO > Do > do` ladder was offered as one example of the
kind of micro-decision evaluations must consider — NOT as a
precedence claim to verify. The kinds register, each with
candidate levels a design enumerates and runs rank: casing /
token-form ladders (levels GENERATED by the layer's data-driven
`transform` engine — casing × substitution cross over the SSOT
`char_variants` table; `token_forms` is a manual override only,
never the mechanism); substitution scope (vowels-only —
the established form — | wider consonant sets | full dictionary
tables); substitution depth (first variant | alternates);
placement (prefix | suffix | both); selection (first | hash |
rotated); timing / when-to-use (always | per-role | per-context
| profile-gated); profile composition (lists | named profile);
emoji-sequence inclusion (in | out). Treating any one instance
as a fact to establish-or-refute misses the point: instances
are levels, kinds are factors.

## Binding rules (from #1865 + separation spec)

1. One primary home per record. Cross-surface references are citations
   (pointer + label), never copied payload.
2. The Delphi cycle record's presentation on this surface is REQUIRED
   with full payload + `owner_surface: delphi` — and is never counted
   or relabeled as a DoE campaign result.
3. DoE's own results come only from family campaigns' committed records.
4. Counts are live-derived at report time.
5. **Automation requirement (owner, 2026-10-31): a design is
   implemented WITH its automation.** Every admitted campaign names
   its automation in DESIGN `automation{}` — the runner/workflow
   that executes the design, emits EXPERIMENT-conforming records to
   the campaign's `records/`, and produces SUMMARY — so experiments
   run as repo automation (GitHub Workflows / provider lanes),
   never as manual per-run dispatch by a chat. The loop is:
   automation runs → records land → doe-expert reviews → design
   adjustments land as amendments. A campaign whose automation is
   not yet built is `admitted_design_only`; manual runs taken
   anyway are OBSERVATIONAL, never designed results.
6. **Continuous live production basis (owner, 2026-11-01): design
   experiments around continuous live production.** Provider wiring
   is being updated, so past route censuses go stale: routes are
   re-verified at design time AND at dispatch time, and no design
   may hard-pin a route (parameterize it — a dead route is a datum,
   not a mid-run blocker). The design basis is the continuous live
   production flow; controls are embedded in that flow only, never
   standalone suite executions as experimental mass (strengthens
   the live-first doctrine). Calibration anchors must be live
   production campaigns calibrated in situ.
7. **Dispatch evidence protocol (owner adjustment 2026-11-01, via
   live-builds): n=3 is a FLOOR, dynamically adjusted.** Designed
   dispatch evidence accrues in sets of 3 per trigger — same
   trigger, fresh auto-selected instances per set, every set member
   stamped with its instance_key plus set index and cumulative n so
   every look stays auditable. Stop when conclusive under the
   campaign's decision rule (unanimous or threshold met); a 2-1
   split or spread-in-noise buys exactly one more set. Cap:
   n=12 per trigger (4 pre-registered looks) or the campaign's
   window/budget bound, whichever first — hitting the cap stops as
   an INCONCLUSIVE datum, never a forced verdict. Campaign rules
   may exceed this floor (e.g. live-1's per-cell minimums); none
   may go below it.
8. **Backfill doctrine (owner, 2026-11-01): backfill is a standing
   first-class mechanism, not a fallback.** At EVERY version change
   of a scoring test or definition, historical records are
   re-scored under the new version. The backfill method itself is a
   versioned, improvable artifact, and every backfill is audited
   (records carry their origin: live, or backfill under
   method@version, with from/to versions and deltas). Results are
   compared across versions continuously — version-over-version
   comparison is an ongoing line — until DoE culling retires a
   method version, which ends that version's comparison line.

## Definitions of record

- **Swarm** (owner definition, 2026-11-01): ALL providers' inference
  model endpoints participating in 3L0 DoE. Under DoE the swarm is
  the experiment's *participant population* — every provider
  inference endpoint is enrolled as arms. Seats, apps and workflows
  are the swarm's organs, not the swarm itself. In DoE records and
  designs, "swarm" carries this meaning only; a specific lane, app
  or workflow is named as itself.
- **Dispatch principle** (owner, 2026-11-01; dispatch-side companion
  to the Swarm definition): dispatched work is routed and assigned
  across comparative planes for efficiency learning. Hard-selecting
  a single arm starves the signal — single-arm traces are
  incomparable (no counterfactual, no cross-arm efficiency
  estimate). Designs therefore spread dispatch across arms by
  default (rotation, sets, factorial assignment); a single-arm run
  is observational color, never comparative evidence.

## Method versions (strategy-level, under rule 8)

Registered so backfill version-comparison lines attach: at any
version change, historical results are re-scored under the new
version and compared continuously until culling retires a version.

- **rnd v1** — randomized mixes: the variation operator of the
  generational loop. Mechanisms: DOE-TAXONOMY generators
  (`full_factorial`, `taguchi_l9`); phrase-layer JIT variant
  generation; randomized assignment inside designs. In the loop,
  rnd produces the mixes from which the next generation is drawn —
  including re-mixing the complement (non-carried) cohort.
  Status: active. Comparison line: open.
- **cherry-pick v1** — generational selection operator ⛏️🧬: the
  top-performing **% cohort** of slices/features is carried into
  the next generation (owner definition: cherry-picked slices ∧
  features propagated into new additions); the proportion is a
  recorded per-design parameter. NOT dispatch-time best-arm
  routing — that reading is retracted (correction of record,
  2026-11-01); dispatch-time spread is governed separately by the
  dispatch principle and rule 7. Mechanisms: campaign verdicts
  designating the carried cohort; cull-as-data records what was
  not carried (nc-1 evaluator); evolutionary culling toward Top
  Performance over generations. **Guardrail (generational-%,
  replacing the retracted per-window floor): the carry-over
  proportion stays strictly partial — 0% = no inheritance, 100% =
  no selection; the complement cohort persists and is re-mixed by
  rnd in the next generation, which is what keeps winner estimates
  fresh. Proportion changes are method-definition changes under
  rule 8.** Status: active (restated). Comparison line: open.

- **doe-specialist-methods v1** — the DoE Specialist function,
  registered reflexively: the versioning apparatus applies to the
  specialist's own methods. Embodiments of record (census
  2026-11-01; no artifact literally named "DoE Specialist" exists
  in the repo — the function is embodied, not a single file):
  `.agents/skills/multivariate-doe/SKILL.md` (created 2026-08-27,
  the repo's oldest DoE artifact; enriched 2026-10-28 by mining an
  external Perplexity research export — NIST/SEMATECH e-Handbook +
  Microsoft experimentation sources — into `docs/ops/DOE-TAXONOMY.md`
  and the skill's terminology discipline) ∧ the doe-expert seat
  with its manager tree (operating lane). Methods under version:
  pre-registered design-first intake; configured-instance identity
  (instance_key); automation requirement (rule 5); live-production
  basis (rule 6); dispatch evidence protocol (rule 7); backfill
  (rule 8); method registration, version comparison and culling
  (this section). Existing experiment corpus folded in by citation,
  never duplicated: `experiments/` (doe campaigns apk-1, cb-1,
  cmp-register, lab-1, live-1..4, nc-1, pilot-1, util-1, ww-1..3;
  archwiz-markov-lane; marketing; speculators), `docs/ops/`
  DOE-COMPONENT-REGISTRY + `ops/doe/component-registry.json`,
  DOE-RECON-2026-10-31, DOE-SCORING-INTAKE, MVT-DOE-ATES-SEPARATION,
  and the model-selection-market DSPY-DOE lane (consideration).
  Adjacent research corpus inventoried: ChatGPT proposal set
  (9 blobs: chatgpt-initial / chatgpt-droidapp /
  chatgpt-critical-eval) — contains no DoE-specialist material per
  census search; the Perplexity thread lands via the taxonomy
  mining above; Liner-cited research sits in the notation-sets
  plane (Linguist), cited not absorbed. Status: active.
  Comparison line: open (v1 is the baseline; its own future
  revisions backfill under rule 8).
  Identity state (census 2026-11-01, vs `ops/github-apps/
  PROCESS.json` + `docs/ops/GITHUB-APP-PROCESS.md`, the AppID
  record of record): dedicated AppID = NONE recorded (8 owned apps
  registered — Collector, Publisher, Reviewer, Lifecycle, Gate,
  Swarm, CrossReference, RepoStory; no DoE entry in the register or
  its allocation queue; the record itself notes other
  owner-registered apps are not API-enumerable). Dedicated repo =
  NONE (org repo search `doe` = 0; standing PROCESS.json note: no
  app has its own repo, RepoStory's entry repo being the first
  per-entry exception). Publication (owner aside, 2026-11-01): the
  fleet apps are all published later — publication is a later
  phase, parked (PROCESS.json later_queue carries "Marketplace
  publishing of fleet apps" as parked_owner_later); no publication
  action now.
  Candidate check (owner, 2026-11-01): a DoE AppID repo (per-app
  repo pattern) = ABSENT from the record — the pattern exists only
  as RepoStory's per-entry installation (on the repo-story entry
  repo, not a per-app repo) and as an undecided PROCESS.json
  proposal (`timerloggedout-spec/<app-slug>` per-app repos, never
  executed; no DoE app exists to hold one). A dedicated DoE data
  repo = ABSENT — experiment/scoring data is homed in this repo
  (`experiments/doe/*/records/`, campaign records and logs) with
  lane-events in Neon (a database, not a repo); no record names a
  DoE data repo. Org repo searches (`doe`, `experiment`, `scoring`,
  `doe-data`) all return 0.
  Status change (2026-11-01): the AppID + repo were an owner
  REQUEST all along (main's speculation reading corrected by the
  owner, owned by main); build routed to the AppID lane. The
  absent-state above stands as the pre-build baseline; this record
  updates when the AppID + repo land. Data-homing coordination
  opened with the AppID lane (records keep one primary home —
  family rule 1; no silent migration).

- **chat-intent v1** — Tier-1 rules-tier classification of owner
  chat messages into {request · directive · aside · speculation ·
  question}. Mechanism (cited, homed with Tier-1):
  `scripts/classifiers/chat_intent.py` (PR #3376) — ordered stdlib
  rules R1–R7 over message tokens: ability-form / interrogative /
  imperative forms first, then hedge+artifact => proposed-request
  (R4, the v1 key rule — a hedge with a concrete artifact noun is
  a proposed request, not speculation), action+artifact =>
  request, hedge-only => speculation, default aside; every verdict
  carries evidence {hedges, artifacts, actions}. Evaluation:
  labels = retrospective chat outcomes (weak supervision: built /
  routed vs discussed-only); ESTABLISHED gated at n>=30/class ∧
  minority>=10 ∧ p<.05 (standing gate); accuracy NOT_ESTABLISHED
  at v1. Status: active. Comparison line: open.

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

### ChronoMancer mapping (2026-10-30)

`harmony_hub/workspace/agent/chronomancer.py` (+ CHRONOMANCER_SPEC.md)
is a Time-Loop fork selector/executor: it scans `run_history`
(SQLite: session_id, account, timestamp, validated) for the last
validated run, forks the conversation at the assistant message
preceding it, injects a validated-state summary as the new
session's first prompt, and logs the fork back with a `time_loop`
verdict (feeding the Bidder/ELO system). In DoE terms it is a
sequential selection mechanism: fork-point choice = which arm's
lineage continues; downstream `validated` = the outcome signal.

Mapping: `moniker` = `chronomancer`; `role` = `fork-selector`;
`context` = session_id + account; the fork POLICY is a factor
(levels: fork-from-last-validated | root fork `--root`); the
injected validated-state summary is its prompt artifact (ref =
the injection at fork time; sha256 NOT ESTABLISHED — generated at
runtime, not committed); tools = deepcli `branch_conversation`
surface (`tools:chronomancer:branch`). Gaps named: `run_history`
is local SQLite, never emitted as repo records — ChronoMancer
rows join the experiment record only when a fork's outcome is
written back into a campaign or ledger record; and the forked
session's own producing instance is a separate stamp (the fork
event and the continuation are two records, not one).

### Bets of record

- **Title `archW1z`** (OPERATOR PAT identity) — owner bet,
  2026-11-01: contender = DeepAgent.py, earning the title through
  DoE results. Judged by DoE: campaign records ∧ the standing
  significance gate (ESTABLISHED ⇔ n≥30 ∧ minority≥10 ∧ p<.05),
  never by registration. Until earned, `archW1z` := Owner only.
  (Correction of record: an earlier paste marked ChronoMancer
  itself as the bet — struck; the ChronoMancer mapping above
  stands at its plain identity state.)

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
