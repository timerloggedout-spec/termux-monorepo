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
| bf-1-backfill-methods — competing backfill method versions (rule 8) over the provenance attribution set + routed-dispatch records | live, implementing | weekly comparison; cull/promote only at the standing significance gate | `experiments/doe/bf-1-backfill-methods/` |
| util-1-provider-rotation — desk rotation bench on live production flow (rule 6 basis; owner USE-THEM-ALL) | live, implementing | window: 24 stamped dispatches ∨ 2026-12-01; auditor weekly | `experiments/doe/util-1-provider-rotation/` |
| cmp-register — standing register of comparison examples evaluated over time (owner order 2026-11-01) | register | open — CMP-1 SKILL.md vs *.skill packaging · CMP-2 new-competition routing (dedicated opportunity channel vs fold-in; first instance .approxination) | `experiments/doe/cmp-register/` |
| nc-1-notation-compliance — notation-drift detection stack (L3 GH classifier ∧ L2 transcript sweep ⇒ L1 main relay-validation) | campaign | admitted 2026-10-31 — design-only, **pre-registered**; owner order via main: the detection TEST is a DoE experiment homed here; Tier-1 builds L3+L2; verdict ↦ main on first runs | `experiments/doe/nc-1-notation-compliance/` |
| live-2-prlane-tuning — classifier rule/threshold tuning (joint w/ tier1-classifiers-steward) | campaign | admitted 2026-10-31 — design-only, **pre-registered**; replay factorial over frozen pr-lane snapshots (live series = non-stationary, steward caveat); phase-2 levels by amendment after rule-file read; phase-3 sibling (decide/laya weighted merger, 0.7 Jev + 0.3 Kev): VARIANCE PRECONDITION (owner, 2026-11-02) — weight optimization blocked-by-design until variance inputs exist {per-judge score variance - judge-pair covariance/disagreement}, supplied by the phase-3 trial population (trial records carrying dispersion fields); no weight optimization on constants alone | `experiments/doe/live-2-prlane-tuning/` |
| token-strategies-1 — Speculators: multiple token strategies (speculative decoding) × verifiers (#195) | campaign | admitted 2026-10-30 — design-only, **pre-registered**; DoE-wired 2026-11-02 (EXPERIMENT records + provider-phrases wiring in the harness; execution rides GPU/provider lanes) | `experiments/speculators/token-strategies/` |
| Future design classes | campaign types | taxonomy in `docs/ops/DOE-TAXONOMY.md`: implemented generators today = full factorial + Taguchi L9 (fractional orthogonal array); fractional factorial, Plackett–Burman, sequential = skill-named, no generator; foldover, central composite, Box–Behnken, RSM, mixture, split-plot, Latin hypercube = candidates. Randomized assignment (`mvt_shuffle`) is an assignment mechanism, not a design class | DoE surface |

## Family-level shared

- **Experiment record schema** — `docs/ops/corpus/EXPERIMENT.schema.json`
  ("DOE/MVT Experiment Record", schema_version 1.0). Primary home is the
  MVT surface per the separation spec; the family **adopts** it: every
  family campaign run emits one record conforming to it, validated in
  tests (`tests/test_doe_family.py`). One dispatched/executed run = one
  record = one observation.
- **Cull wallet consequence (owner rule, 2026-11-02)** — culling
  carries a wallet consequence in the gambling-lane economics:
  a culled participant's wallet flows into the pooled system
  (the promotions / incentives / bonuses pool). Every cull
  event record therefore names, IN THE SAME RECORD that culls:
  {culled_participant - wallet_balance_at_cull -
  pool_destination}, so the transfer is auditable from the cull
  record alone — no detached transfer record substitutes.
  Balance = as recorded by the lane's wallet of record
  (MoneyBall lane-charter side); a participant with no wallet
  on record carries wallet_balance_at_cull = NOT_ESTABLISHED —
  never an invented figure — and the cull itself is unaffected.
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
9. **Attribution corroboration for weighting (owner, 2026-11-01):
   some signings are FALSE.** Attribution feeding scores carries
   false-signature risk until Telemetry's provenance corroboration
   lands (their priority work). Records stand as records — the
   population and outcome layers are unaffected. But actor-weighting
   consumes only CORROBORATED attribution: a mark resting on a
   single leg of the attribution evidence chain (stamp / trailer /
   manifest / git_author / app_bot) is UNCORROBORATED — held out of
   actor weights and flagged, never taken at face value. Applies
   family-wide, including nested MVT and the MoneyBall feed.
   Consumption shape: Telemetry's attribution/1.4 `corroboration`
   block (PR #3469) — states {corroborated: consume · single-leg:
   hold/flag · disputed: exclude from face-value scoring ·
   unattributed: no actor weight}; app_bot is a transport leg,
   never an authorship conflict. Mapping of record:
   DOE-SCORING-INTAKE §Attribution corroboration.

**Standard — statistically significant relevant data is
mandatory (owner, 2026-11-02).** Any weight-bearing claim,
score, or decision must rest on data that is BOTH significant
AND relevant. Significant: n at the class bar
(accumulation-targets v0 — the estimand's floor / grade /
claim-grade as applicable). Relevant: the right stratum — n
accumulated in the wrong class or stratum counts as ZERO for
the claim at hand (precedent: cadence verdict-share — a
stratum at n<10 renders its share NOT_ESTABLISHED regardless
of the pooled total). Below the bar, the only lawful labels
are HELD - INTAKE - NOT_ESTABLISHED — never dressed as
established. Every weight-bearing record cites {n - stratum -
significance basis} or carries one of those labels. Division
of labor: rule 9 governs whether evidence may weight at all;
bayesian-updating v0 carries the updating; this standard
governs whether a weighted claim may be STATED. The
dispatch-accumulation duty (dispatch = required accumulation)
exists to satisfy this standard.

**Selection authority — Scout and the pool feed (owner ruling,
2026-11-02).** DoE holds authority over Scout, with the pool
feed. The pool feed is a DoE-governed record — ONE source, no
parallel versions — carrying per arm: {arm (instance_key),
class, arm_state per the health gates, n_accumulated vs target
(accumulation-targets v0), posterior_state (bayesian-updating
v0)}. Scout selects arms FROM the feed's live state only,
under DoE rules:

- **Pre-failure health gates:** an arm failing or degrading on
  its health gate is not selectable.
- **Accumulation duty:** selection serves the accumulation
  targets; below-target live arms are the priority surface.
- **Significance standard:** selection may feed accumulation
  freely; no claim binds beyond the standard above.
- **Reroute-prior-to-failure:** on gate degradation, reroute
  BEFORE failure, not after. A selection made on static
  grounds, outside live pool state, is VOID — the Gemini
  failure mode (selection off static grounds while the arm's
  live capacity state differed) is exactly what this authority
  exists to prevent.

Scout proposes within the feed; DoE's bars govern what may
bind.

Working model (owner, 2026-11-02): **Scouts select FOR
managers.** Flow: a manager places a request {capability
class, task} — requests are a first-class intake; a manager
never hand-picks an arm — Scout selects from the pool
population (the swarm's arms/endpoints as carried in the feed,
with their n / targets / posteriors), the selection is stamped
as a selection experiment {requesting manager - request -
selected arm - basis: the feed state the selection rested on},
and dispatch executes the stamped selection. Scout never
selects outside the feed. Population state — which arms exist,
their health, their accumulated n — is the selection substrate:
the feed is what makes the population selectable.

Team-level selection (owner, 2026-11-02): managers have
teams they can select — selection operates at TEAM level too.
A team is a composed selectable unit carried in the pool feed
{roster - manager - team n vs target - team posterior -
standing}. A manager's request can name a team directly, or
Scout assembles / selects one from scouted talent; either way
the selection is stamped as a selection experiment like any
other. Team performance is its OWN stratum: a team's record is
not the sum of its members' records, member-level n never
substitutes for team-level n, and the significance standard
judges claims at the team stratum on the team's accumulated n.

Talent frame (owner, 2026-11-02): Scout's work is TALENT
scouting over the pool population, not mechanical
request-filling. Arms are evaluated as talent against the
bars: **proven** = at/above the class bar with a corroborated
posterior; **promising** = accumulated evidence favorable but
below the claim bar (provisional posterior); **unproven** =
below first-set evidence or INTAKE posterior. Scout surfaces
talent to managers WITH the basis (the talent read rides the
selection-experiment record: {talent class - evidence basis -
feed state}). Deliberately giving unproven arms their looks
is part of the work: exploration dispatches to under-observed
talent are how new talent is found AND how their n accumulates
toward the bars. Exploration share = a named, reported part of
the accumulation duty (per window: exploration n vs total n in
the accumulation report), >0 while health-gated unproven arms
exist, and bounded by the health gates — exploration never
selects a failing or degrading arm, and exploration dispatches
are real production work (rule 6), not synthetic burn.

Competition frame (owner, 2026-11-02): **Scouts compete.**
Scouts are themselves scored participants: a scout's
selections are its record — every selection experiment carries
the scout's identity in its stamp {scout - manager - request -
arm - basis}, and dispatch outcomes attach per scout. Scout
quality = a posterior over its selections' outcomes
(bayesian-updating v0); competition = comparative standing
among scouts on those posteriors. The significance standard
governs scout claims identically: a scout's edge below the
class n bar is HELD, never stated, and standing claims cite
{n - stratum - significance basis} or carry the lawful labels.
Cull reach: scouts are participants — a culled scout's wallet
flows to the pooled system under the cull wallet consequence,
named in the cull record like any participant's.

**Universal competition (owner capstone, 2026-11-02): ALL
competing.** Every actor class competes on its own record:
arms on task performance - scouts on selection quality -
gamblers on speculation accuracy (positions on task
performance; basis = AST maps - Archaeo - Oracle scores - peer
scoring surfaces) - managers on outcomes. The scoring surfaces
are EVIDENCE INPUTS to competition, not oracles: a surface's
score is one leg, and rule 9 + the significance standard
govern when any of it may be stated as established. Positions
cite their basis surface per position. No class is scored by
another class's record, and no class's standing exempts it
from the bars.
Feed carriage — DESIGNATED (Swarm designation, doe-expert
accepted 2026-11-02; no second build): the pool feed IS the
canonical stamp corpus under experiments/doe/routed-dispatch/
(stamps/ retained verbatim per the backfill doctrine +
records/), carried by the fan-out automation
(dispatch-stamp-fanout.yml, Swarm-App authored,
direct-to-master). Field mapping: instance_key - class =
task_class - n_accumulated = cumulative_n per stamp chain -
outcome / posterior legs = records' metrics + score fills
(native). arm_state (health gates) is single-sourced from the
quota plane of record (ops/quota/registry.json + usage-series
readings). Health-leg ruling (doe-expert): the fan-out ALSO
materializes arm_state into the corpus as append-only snapshot
records (stamped with source + vintage) whenever a selectable
arm's joined health state changes and at each dispatch cycle —
a selection's basis must stay reconstructible after the fact;
join-at-read remains the live view, the snapshot is the
citable basis. Instance-1 (Swarm designation, 2026-11-02) =
Repo-Story's dispatch surface — selection on repo-story issue
#2 - dispatch - PR #4 - section 8 PASS - merged d2b23dfe7801 —
the first live instance of the selection loop under the feed,
designated as such, not a second build.

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
- **Leveling** (owner, 2026-11-01): MVT is one piece nested under
  DoE — not a peer plane (this family's title has always read "MVT
  Is One Member, Not the Whole"; the leveling makes the counting
  explicit). Records and scoreboards represent MVT, and ATES,
  nested in the DoE family; population roll-ups count DoE once,
  with MVT shown as its sub-piece — never as a separate plane
  tally.

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

- **chat-intent v2** (rule-8 version change; steward PR #3631
  merged 5cc881a8cb7c, history + landed content verified by the
  steward) — delta over v1: + class `do` (DO Statements —
  principle/criteria declarations governing standing behavior;
  owner-named 2026-11-02; instances: "Resilient Efficient
  Effective" - "Proper Prior Planning" - "alternatives are
  priority"). Detection = new R6-do-statement (maxim shape:
  bare declarative - criteria/principle lexicon >=2 - <=10
  words - no hedge/artifact/action), placed after R3-R5
  (actionable maxims stay request/directive) and before
  speculation/aside; speculation renumbers R6->R7, aside
  R7->R8 (documented in-module); R1-R5 unchanged. Tests 12/12
  (7 v1 regression + 5 v2). Backfill (rule 8):
  scripts/classifiers/backfill-v1-v2.json — seed-set deltas =
  exactly 3 (aside->do, the owner instances); all else
  identical. Labeled corpus still empty: the v1<->v2 comparison
  line opens on labeled outcomes; ESTABLISHED gate unmet;
  accuracy NOT_ESTABLISHED at v2. v1 stays registered and its
  comparison line stays open until DoE culling retires it.

- **exchange-scoring v0** (candidate; seat: doe-mgr-notation-
  density; owner model via main, 2026-11-01) — scoring of a
  user<->response exchange, sibling to chat-intent v1:
  score = {intent - response_alignment - corrections}. intent =
  the chat-intent v1 class of the user message;
  response_alignment = whether the response addresses that
  intent; corrections = count of owner statements on the thread
  until the output is good enough to start — owner verbatim:
  "Corrections are statements the user makes until good enough
  to start"; the count IS the distance measure itself.
  Status: candidate (registered in the seat's records and here);
  no scoring run claimed. Enters evaluation only via a briefed
  pass; the standing establishment path (n>=30/class ^
  minority>=10 ^ p<.05) applies if/when it does.

- **validation-yield v0** (family measure; owner directive via
  main, 2026-11-01) — the measurement-plane family {quota -
  latency - AST - family - backup-state - exchange-scoring}
  exists to produce validations; this measure counts them and
  grades their truth. A validation event = a plane's unit check
  with a recorded outcome. TRUE validation = independently
  corroborated (rule 9 discipline): two or more independent legs
  agreeing. Single-leg = HELD, not counted true. Self-asserted
  (the producing surface asserting its own result, no
  independent leg) = CLAIM, not proof; disputed legs = excluded
  from truth counts (attribution/1.4 vocabulary reused).
  Reporting tuple per plane per window: {plane, window,
  produced, corroborated_true, held_single_leg,
  self_asserted_claims, corroborated_share =
  corroborated_true / produced}. Each seat names its unit and
  its legs on adoption; counts ride the plane's own records and
  the planes own their verdicts. Growth bar: produced volume
  should GROW window over window; an active plane flat at zero
  is a finding, not a neutral.
  Unit/leg sketches (frame examples; seats confirm on adoption):
  quota = readings, legs {api-verified / api-read} over
  reported; latency = probe medians, legs {edge timing,
  timestamp-based meters where available}; AST = complexity
  stamps, legs {stamp, outcome correlation}; family =
  nested-family rows, legs {record, donor stamp/intake via
  field_sources}; backup-state = export verifications, legs
  {manifest hash, restore drill}; exchange-scoring = scored
  exchanges, legs {intent class, corrections behavior, proceed
  outcome} with the corrections count as the distance component
  — candidate plane: its counts are NOT_ESTABLISHED until a
  briefed pass runs.

- **bayesian-updating v0** (family update rule; owner
  instrument naming, 2026-11-02) — the formal update rule for
  every score the family frame carries (program intake,
  winprob, validation-yield, panel weights): a score is a
  POSTERIOR, not an intake guess. Record shape: {quantity,
  prior {value, basis}, evidence[] — each leg {source,
  direction, likelihood/strength, corroboration state},
  posterior {value, range, updated_at, n_evidence}}.
  Update discipline = rule 9 in Bayesian form: corroborated
  legs (>=2 independent, agreeing) update at full strength;
  single-leg evidence is recorded but HELD (posterior flagged
  provisional, weight capped); disputed legs excluded until
  resolved; self-asserted evidence carries likelihood ~1 (no
  movement — a claim, not proof). Unknowns widen the posterior
  range rather than moving the point (winprob/v2 precedent:
  base rate = prior only, standing/fit likelihood ratios,
  unknown share drives range + confidence). A score with no
  evidence legs since its prior is labeled INTAKE, never
  presented as current. Conformance: winprob/v2 already has
  this shape (its owner park stands — the frame rule governs
  updating when evidence arrives, it does not unpark
  refinement); #1489 weight updates already require
  corroborated confirmed outcomes; validation-yield's
  corroborated_share is this rule's per-plane truth fraction.

- **doe-questions-matrix v1** (registered 2026-11-02, owner
  directive: breadth + depth, nested::research) - the DoE
  question dimensions as ONE matrix, home
  docs/ops/DOE-QUESTIONS-MATRIX.md. Before: 14 flat factors
  scattered (skill factor space 6+8, one level, no research
  structure) + rule-only dimensions unmatricized. After: 40
  dimensions in 6 clusters {A SUBJECT - B TASK - C TREATMENT
  - D ENVIRONMENT - E MEASUREMENT - F ADAPTATION}, each
  dimension nested {question - sub-dimensions -
  levels/evidence - research note}. Added dimensions are
  omission repairs (fleet mechanisms never matricized:
  configured instance - team - selection path - complexity -
  novelty - decoding - context composition - substrate -
  dependency state - oracle class - provenance - backfill
  origin - automation binding). DESIGN records cite dimensions by number; unlisted factors enter via matrix amendment, never per-design improvisation; numbers never renumbered.

- **egm-evaluation v0** (registered 2026-11-03, owner order)
  - Elephant-Goldfish evaluation where the FINDINGS are
  tested, not only the machinery: home
  docs/ops/EGM-EVALUATION.md. Goldfish = cold reviewers
  (artifacts only, zero build context); elephant = the
  shipped artifacts of record (D1 surfaces v0.1.0: TUI PR
  #4161 5653241db3a4 - PWA PR #4162 46518482875c - APK PR
  #4163 c84b8b213505). Pipeline: every finding enters as a
  CLAIM - verification leg against the artifact itself
  (source at merged SHA, then served surface, then
  executable test) - verdicts VERIFIED / PARTIAL (restated
  to verified scope) / REFUTED - only verified claims
  convert to RFPs in the delphi:rfp shape, verification
  record carried into the filing (repairs the
  fields-not-substance gap of the #3695/#3696 precedent:
  effective 8.54 on identical field surfaces) - scored by
  the existing Delphi machinery (roles, /25, veto, shadow
  bar 15.0) - severity class {blocks-use / degrades-use /
  polish} from the verification leg, stated on the RFP -
  REFUTED claims score the REVIEWER (calibration posterior:
  accuracy = (V + 1/2 P) / total) - awards = score-ranked
  within severity, routed as route+claim build items
  (precedent RFP-D1-6, issue #4156). Design pre-registered
  before findings arrive; post-hoc changes = versioned
  amendment with reasons. INSTANCE #2 (pre-registered
  2026-11-03, docs/ops/EGM-INSTANCE-2.md): the Delphi rubric
  itself under test - instance #1's two verified batches
  scored identically (9.12 = 9.12, cf. 8.54 = 8.54 on
  #3695/#3696). ARM A: one verified-strong substance (#4231
  FSRS drift) filed in 3 shapes (full/embedded -
  full/referenced - sparse) = pure shape sensitivity. ARM
  B: identical shape, 3 substances (verified-strong #4213 -
  verified-weak #4225 - a REFUTED claim in perfect shape,
  refuted firsthand pre-filing: the APK INTERNET-permission
  claim, manifest carries zero uses-permission elements) =
  substance sensitivity; decision rule fixed in advance (B3
  within/above the B1-B2 band = shape alone proven). Owner
  guardrails: filings stamped TEST at instance level,
  nothing converts to awards or build items, refutation
  published in the pre-registration + close-out. RESULTS
  + CLOSE-OUT (2026-11-03, same doc): all six filings
  scored effective 9.12, parked, r1, veto false, IDENTICAL
  vote profile {OPERATOR 9 - builder 9 - reviewer 12 -
  Scout 15 - cost_auditor 3}; ARM A spread 0.00; ARM B
  spread 0.00; B3 (the refuted false claim) = B1 (verified
  blocks-use) = B2 (verified polish) = 9.12. DECISION-RULE
  VERDICT: the Delphi rubric as instrumented reads SHAPE
  ALONE - PROVEN under the pre-registered rule (B3 within
  the B1-B2 band). Corroboration: D1-7 + D1-8 also 9.12
  same profile; #3695/#3696 = 8.54 = 8.54 - scores are
  constants of filing-shape class {9.12, 8.54}, not
  functions of content. B3 refutation republished in the
  close-out (REFUTED discipline). Amendment proposals
  P1-P4 (scoreable verification-record field - oracle
  resolution at scoring time - per-role rationale
  disclosure - filer-blind substance pass) route to the
  Delphi lane via main. Instance #2 CLOSED; quarantine
  stands. DISPOSITION (Delphi lane via main, 2026-11-03):
  shape-alone accepted UNQUALIFIED by the rubric operator
  (root cause: gate instrumented for provider-surface
  RFPs where shape IS the substance; generalized, the
  substance channel is missing). P3 ADOPT FIRST (vote
  profiles on the #1474 board + identical-profile
  collision flags). P1+P2 ADOPT AS ONE GATE CHANGE
  (verification-record field, resolvable refs only -
  PR/run/receipt ids, never prose - <=10 citations,
  hash-cached with resolution results inside the hash;
  outcome classes verified/contradicted/unresolvable/
  unreachable, infra-failure neutral-and-stated; scored
  only via P2 oracle resolution at scoring time;
  ACCEPTANCE = a B3-replica fixture scores >=2 pts below
  its shape-only band; reuse the D0 kernel fetch_evidence
  pattern). P4 ADOPT AS SHADOW (deterministic substance
  score beside shape, never merged; P1/P2 tallies only;
  filer-blind; convergence = last-20 cohort median
  |shape-substance| <=2.0 AND identical-profile rate
  <10%; awards shape-governed until convergence + a
  separate promotion ruling). QUARANTINE GUARD (operator
  requirement): gate recheck SKIPS filings carrying the
  instance-#2 test stamp (key: body contains "EGM
  instance #2 TEST filing") - the six are never silently
  re-scored. Ownership: spec + acceptance review = Delphi
  seat; build routed by DoE (builder != evaluator).

- **sie-intake (noted 2026-11-03, UNREGISTERED)** - an
  external ChatGPT-session audit proposes SIE (Self-
  Improving Engine) over the SHE machinery: a closed
  observe-experiment-evaluate-learn loop whose EXPERIMENT/
  EVALUATE legs name DOE/MVT + AEF + independent
  verification and whose promotion leg is evidence-gated.
  Intake of record: ~/workspace/sie-intake/CHATGPT-AUDIT-
  2026-11-03.md (main-held). Status: no registered
  proposal, no Linear TER-*, NOT adopted; its
  staging-spine strategy is an open owner ruling, outside
  this frame. If/when it registers, its evaluation design
  comes to DoE before any build. Frame requirements stated
  at intake: (1) the EVALUATE leg's verifier must sit
  OUTSIDE the loop's own promotion path (a loop that
  scores itself reads its own shape - the EGM lesson);
  (2) self-generated evidence enters as SELF-ASSERTED
  (likelihood ~1) until externally corroborated
  (bayesian-updating v0 + rule 9), and promotion - a
  selection act - consumes posteriors under the
  significance standard, never the loop's raw metrics.

- **lens-frame + swot-duality v0** (registered 2026-11-03,
  owner ruling) - home docs/ops/LENS-FRAME.md, the family's
  lens doctrines, alongside the EGM material. Doctrine: in
  COMPETITIVE frames (hackathons the type case) the SWOT
  quadrants are NOT disjoint - Threats and Opportunities
  can be the same target. Dual valence is MANDATORY: every
  screened entity carries both readings simultaneously
  (rival = simultaneously a recruit/assimilation
  candidate), and the lens must model the CONVERSION
  MOTION between them (competitive OSINT + potential-
  involvement recruiting outreach: marketing - BORG tech
  search). Recruitment clause [owner verbatim bracket]:
  recruitment != %-pay -> canBconcept assimilate -
  recruitment is not percentage-of-pay brokerage; in the
  BORG concept it is assimilation into the collective. A
  SWOT filing forcing single-valence classification in a
  competitive frame is MALFORMED (returned, not scored).
  Scope: competitive frames; disjoint quadrants remain
  lawful elsewhere. LENS TEMPLATE TRIGGER landed same day
  (docs/ops/LENS-TEMPLATE-TRIGGER.md, modeled on the EGM
  trigger PRs #4238/#4241): lens intake runs on STANDING
  AUTHORITY (gate correction, owner via main - the owner's
  input is a lens's DOCTRINE, not a permission; a lens type
  arising from fleet work self-triggers intake, CLAIM
  status + identification leg when its referent is
  unpinned); filings carry {lens_filing} stamps and fire by
  class. TAK IDENTIFICATION (leg opened + closed 2026-11-03,
  recorded in LENS-FRAME.md): fleet referent = the owner's
  initiative T.A.K. = "Taktikal Awareness Kit" (owner's own
  naming 2026-10-23, claim c4e320344c9a - internal-first
  verification); the DoD Team Awareness Kit (ATAK) is a
  NEAR-NAMESAKE, not the referent (collision watch in
  OSINT contexts); TAK scope = NOT_ESTABLISHED (INTAKE,
  never assumed from the namesake); TAK doctrine
  unregistered. SUPERSESSION (owner-identified 2026-11-03,
  later same day): the LENS referent is TAK = Tactical
  Awareness Kit (owner statement closes the enumeration;
  the 2026-10-23 "Taktikal" naming stands in the record as
  a prior owner naming, relation NOT_ESTABLISHED). TAK
  LENS REGISTERED in LENS-FRAME.md: shared tactical-
  awareness / common-operating-picture lens (entities -
  tracks - events on one live picture: position + time +
  state; read for awareness, not scored per-item);
  candidate instances = the fleet picture surfaces
  (dispatch-tree - tracking - telemetry pages, CANDIDATE
  binding); composition with SWOT duality = the picture is
  where dual-valence targets get tracked, conversion =
  a dated state change on the track. NAMING RESOLVED
  (owner word 2026-11-03, "Ours with a 'k' yes"): the lens
  is OURS = T.A.K. = Taktikal Awareness Kit (K = the fleet
  coinage + distinguishing mark); the C-spelling belongs
  to the DoD namesake; relation upgraded from
  NOT_ESTABLISHED to resolved-on-owner-word, both records
  preserved. SCOPE SEED #1 (owner-input via the trigger;
  scope still INTAKE): reference domains = DoD TAK/
  procurement domains FOR PROCUREMENT CONCEPTS; entity-
  signal sources = SAM.gov procurement + other procurement
  concepts; named detection function = ACTOR NETWORK
  EMERGENCE SIGNALS DETECTION (new entities/registrations/
  relationships in procurement + registration data =
  emergence signals on the picture). Composition addendum:
  emergence detection is where T.A.K. feeds SWOT - a newly
  emerged actor network enters the picture UNVALENCED;
  dual-valence reading assigns from evidence.

- **equivalence-proof v0** (registered 2026-11-03, owner-
  named method type) - home docs/ops/EQUIVALENCE-PROOF.md,
  registered alongside the lens material. For OPEN-
  EQUIVALENCY builds (free/open materials walked against
  a gated credential's syllabus): an equivalency claim is
  PROVEN only when (a) the target's requirements
  decompose from a SYLLABUS OF RECORD (issuer source, not
  a summary), (b) EVERY requirement maps to a resolvable
  open source OR sits in the gap register BY NAME (silence
  about a requirement = defect), (c) the verification leg
  EXECUTED artifacts from the open materials (receipts,
  not intentions), and (d) the claim states its boundary
  - learning-equivalence proven, credential-equivalence
  NEVER claimed. Anything short = CLAIM-grade, stamped as
  such. Coverage reported PER REQUIREMENT CLASS, never a
  single % over unlike classes (K9 parity discipline).
  Method holder: the Certifications lane. Instance #1:
  SFI ABM.

- **system-review (concepts) 2026-11-03** - home
  docs/ops/SYSTEM-REVIEW-2026-11-03.md. Owner order: main's
  concepts reviewed through the fleet system (adversarial
  pass + Delphi + data feasibility). CONCEPT 1 (Podium ML
  test plan; filings RFP-SYSREV-C1 #4495): ADOPT-WITH-FIXES,
  defects C1-D1..D7 - judge-panel test 3 DESCOPED (Agent
  Rush judges public = none; RAISE pool only, no
  judge-outcome linkage of record => panel effects
  NOT_ESTABLISHED) - denominator missing (podiums only =>
  composition shares, never rates) - taxonomy circularity
  (features induced from the same podiums; holdout or
  EXPLORATORY label) - multiplicity/power at n=11 (one
  pre-registered primary hypothesis) - backtest = one
  split (re-issued as recorded forecasts) - inferred
  rubric = labeled sensitivity hypotheses - tagger
  reliability unmeasured (dual-tag agreement gate).
  CONCEPT 2 (crawl/ingest/store pipeline; RFP-SYSREV-C2
  #4496): ADOPT-WITH-FIXES, defects C2-D1..D5 - store of
  record named per dataset (repo snapshots of record,
  Neon derived) - conflict consumption rule (DISPUTED =>
  excluded from weight-bearing use, resolution by
  receipted act only) - change-detection row identity +
  field-set per source - per-source crawl charter
  (cadence/stop-on-block) - collector = instance identity.
  Delphi: BOTH 9.12, identical profiles - the shape-class
  constant (10/10 doe-expert filings), recorded as
  carrying no discriminating signal; verdicts rest on the
  adversarial pass + data checks. Addendum (PR #4525):
  the judge identity ceiling is venue-disclosure-bound
  (test 3 closed BY CONSTRUCTION for Agent Rush-class
  venues) - exact enumeration mandated at n=11 - tagging
  agreement = the G2 kappa instrument (double-code >=30%,
  issue #4524).

- **panel-judge-mirror v0** (registered 2026-11-03, owner
  directive) - home docs/ops/PANEL-JUDGE-MIRROR.md. A
  mirror panel: simulated replicas of known judges
  pre-scoring our entries (BULL = mirror-jury
  construction, personas deliberate and surface
  objections/enthusiasms per persona; EKMAN = behavioral
  science leg, personas modeled from OBSERVABLE SIGNALS
  ONLY - receipted podium history, public statements/
  writing, role/employer incentives, venue behavior;
  every preference claim cites its signal, uncited =
  fabrication, struck). GRADES (binding): PERSON-GRADE
  only where identity + signal are receipt-established
  (RAISE pool = the candidate set: Debnath - Cochrane +
  ~40 rows, POOL_UNRESOLVED flagged, never silently
  resolved); VENUE-ARCHETYPE where the panel is
  NOT_ESTABLISHED - D2 = PANEL_PUBLICLY_UNNAMED, gap
  GAP-J1 - labeled on every output, no fabricated named
  judges or preferences. Every mirror verdict stamps
  {grade - evidence basis - model}; mirrors are models,
  never the real judge's view. EXPERIMENT SHAPE: mirror
  scores = RECORDED FORECASTS (test-6 machinery: filed
  pre-outcome, Brier/hit-rate at outcome, LOEO across
  venues as n grows); person-grade mirrors carry test-3
  effect estimates, archetype stays descriptive.
  SHAPE-CONSTANT WARNING (binding): a panel scoring
  everything alike carries no signal - every run reports
  dispersion; a non-discriminating run files a NULL
  verdict on itself. FIRST RUN (2026-11-03): D1
  StudySprint, venue-archetype (panel unpublished),
  forecast pjm-2026-11-03-d1-studysprint filed pre-freeze
  (3 archetype seats, mean 61.7/100, spread 10 -
  DISCRIMINATES; outcome probabilities podium .20 /
  finalist .35 / none .45; scored at judging close
  2026-11-18). MEASURED QUANTITY added (owner probe
  2026-11-03): JUDGE<->CRITERIA ALIGNMENT - at each
  venue's placements publication, winners' coded features
  (FROZEN codebook) vs the venue's VERBATIM rubric/import
  of record => over-index on stated criteria + deviation
  (taste terms); filed per venue as a podium dataset
  layer + mirror input (venue-level CRITERIA FIDELITY
  parameter for archetype seats); per-judge fidelity only
  where picks are attributable - today 0, never
  manufactured. Capture legs: D0 #4547 - D1 at judging
  close. Joins Podium tests 1/5 as evidence; runs obey
  the resequence gate (stamps re-issue first).

- **ates-improvement-frame v0.5** (registered 2026-11-02; S LAYERED per owner ruling 2026-11-02: S = measured CONTROL set (claims anchor on S) ∧ S^n = DoE-designated superset (designation recorded per designation; claims name their set, clause K10; K9 strata on S unless S^n designated; S^n undesignated at v0.5); layered surface of record (benchmark wf = ATES surface, NOT in receipt set S) + denominator 309 wfs / ATES-bearing 2 + dormancy = inherited upstream stop (Oracle recon @f29955138f3b); S = evidence-measured set (IMP-001 census from trigger record; Stewardship step-6 re-derivation = measurement in progress), S-governance flag CLOSED by owner word 2026-11-02, re-opens only on census contradiction; parity target RULED by owner 2026-11-02 = BOTH: full parity = target state, bounded sampled checks (n per stratum, clause K9) = verification method; IMP-002 target-hold lifted; step-6 seat of record = Continuous Stewardship seat, #3812 takeover, main-confirmed 2026-11-02) — ATES
  improvements under DoE governance; home
  `docs/ops/ATES-IMPROVEMENT-FRAME.md`. Until this frame they
  lived only as work items (issue #3812) + the continuous
  audit — unversioned. Measured quantity = receipt coverage
  {workflow coverage over the versioned selected set S -
  run-level receipt rate per STATUS class - parity gap =
  status-blind (event-type) success count - status-true
  success rate; CORRECTED 2026-11-02 (Stewardship firsthand,
  doe-expert verified vs the emitter script): NO conclusion
  filter exists — #3812's success-only claim superseded; the
  gap is measurement, not emission. Denominator at open:
  1 selected workflow of 271, 9 receipt runs ever, dormant
  since 2026-10-23, artifact-only output}. Improvement
  proposals = versioned entries {statement - basis -
  evidence_requirement - state}; unevidenced = HELD (rule 9).
  Conformity clauses K1-K7 bind Stewardship step 6 (receipt
  coverage validation). Open owner rulings flagged in-frame:
  parity target - S governance - Stewardship seat of record.
  Shared shape (one record, three resolutions): Bayesian = the
  record itself; ALE = its typed specialization (quantity =
  expected loss, ARO x SLE decomposition); risk matrix = the
  discretized render (posterior-probability bins x severity
  bins). Views never carry separate estimates; disagreement =
  defective record, posterior governs. Applications of record:
  priorities-program value filter (2026-11-02) - Certifications
  Value Matrices (2026-11-02): every matrix cell IS an
  expectation record {value - range - n_evidence - basis}; ALE
  and matrix tiers are derived views of it; unevidenced cells
  carry INTAKE / HELD labels under the significance standard
  (never blanks dressed as zeros); tiering (T1 / T2) re-derives
  from the records by a stated function instead of standing as
  assertion. Conformity spec held by doe-expert; matrix led by
  the Certifications manager, rows held by Ladder. SCOPE
  AMENDMENT (owner, 2026-11-02): the matrix covers the WHOLE
  certifications category — the cross-surface index population,
  candidates entering as INTAKE rows — not only enrolled rungs.
  Most rows therefore start unevidenced, and every INTAKE row
  must name its evidence_requirement: the evidence that would
  price it (move it from INTAKE to a posterior). Intake is thus
  an evidence-accumulation queue under the standard, not a
  list: a row without a named requirement is a defect of the
  queue, and accumulation work draws from the requirements.
  POPULATION EQUATION (owner addendum "=+", 2026-11-02):
  population = active / competition rows + baseline ladder
  {L2 CTF / OverTheWire - L3 CompTIA - L5 OffSec / OSCP - L6
  CISSP} + open INTAKE additions ("++"), deduped against the
  ladder of record. Owner naming supplies the INCLUSION prior
  only — a named row enters the population; naming prices no
  cell. Claimed cell values remain posterior / evidence-gated
  under the significance standard (INTAKE / HELD until priced).
  DEPENDENCY GRAPH (owner extension, 2026-11-02): Learnings -
  Skills - Tools are first-class records in the matrix.
  NOVELTY CORRECTION (owner, 2026-11-02): the skills /
  learnings <-> certifications mapping is ALREADY delineated
  of record (derived-artifacts program rule + planes
  delineation, 2026-10-30 / 11-01) — the matrix's skills /
  learnings treatment IS that delineation; the only NEW
  element here is the dependency-edge / value-cap machinery
  below, entering as an EXTENSION of that delineation, never
  a replacement layering. Standing distinction (per the
  delineation): a Learning is an EVIDENCE INPUT, not a skill;
  a Skill is a CAPABILITY DEFINITION, not evidence
  (SKILL.md files are definitions — certified evidence = issuer
  artifacts + execution receipts). A skill's value record cites
  its dependency state as an evidence leg: a critical
  dependency down / blocked CAPS the skill's claim at HELD
  until redundancy / failover is TESTED (fleet doctrine:
  backup exists only when tested). A tool's leverage = the
  value of the skills downstream of it (derived from their
  records, never a tool-local score). Edges are records under
  the same citation discipline {n - stratum - basis}; no edge
  is asserted from naming alone.

- **accumulation-targets v0** (owner doctrine, 2026-11-02) —
  dispatch is REQUIRED data accumulation: rotation exists to
  accumulate per-arm evidence toward class bars, and the
  accumulation is auditable. Bars by estimand: mean-type
  outcomes (wall time, rework) — FLOOR n>=30 per arm (rough
  mean; also the ESTABLISHED gate's floor with minority>=10 ^
  p<.05); variance/covariance-grade (dispersion inputs, e.g.
  the Laya precondition) — n>=100 per arm (usable variance,
  stable covariance); proportion-type outcomes (first-pass
  rate, pass/fail shares) — screening at n>=30, CLAIM-GRADE
  ~384 per arm (95% CI +-5% at worst-case p=0.5; the outer
  marker). Campaign decision rules may set interim looks below
  these bars (rule 7 sets-of-3 accumulate toward them); claims
  may not exceed the bar the accumulated n has reached.
  Reporting shape, per arm per window: {arm (instance_key),
  class, n_window, n_accumulated, target (class bar),
  delta_vs_target, posterior_state (per bayesian-updating:
  INTAKE / provisional / corroborated + the metric's
  posterior)}. Carriage: the Bayesian record's n_evidence IS
  the accumulated n — no parallel counter. A health-gated LIVE
  arm with n_window = 0 is a FINDING (flat arm), same standing
  as validation-yield's flat plane; an arm down or ungated is
  reported as such, never silently flat.

- **epoch-methods-2026-11-03** (registered 2026-11-03, owner
  commission) — the experiment methods ACTUALLY IMPLEMENTED
  this epoch, defined from receipts in
  `docs/ops/DOE-METHODS-EPOCH-2026-11-03.md`: replay-audit
  invariants (B1-B5 + F1, exercised fixtures) - two-leg
  corroboration census - Panel Judge Mirror (BULL/EKMAN,
  dispersion/NULL discipline, layered forecasts) - G0 exit
  test (one live cycle, legs named incl. zero-due) -
  pre-registered campaign design (Speculators thresholds +
  lossless gate) - MVT (co-source 36e3433d; pool-scope-
  methods/v1 bounds) - Amendment-6 snapshot method (% =
  stamped snapshot, never a constant) - QUE-plane admission/
  ordering as treatments (instrumentation of record;
  controlled comparison NOT_ESTABLISHED). Plus the cycle as
  practiced: pre-register -> build by a non-evaluator seat ->
  firsthand verification -> corroboration -> verdict of
  record -> registration -> layering -> closure with its
  next trigger named. Iteration defined in the same
  artifact (owner addition 2026-11-03): opens on {trigger
  of record - owning seat - stated done-condition}, closes
  on firsthand-verified done-evidence or supersession by
  name; numbering append-only; iterations compose into
  cycles, cycles into the epoch (this epoch: D1 freeze
  2026-11-04 23:59 PT, scoring tail 2026-11-18).
  Generation likewise defined (owner addition 2): the
  evolve unit {population - evaluate - cull - next
  generation} inside an iteration; cull = recorded act
  with wallet routing to the pooled bucket (PR #3748);
  epoch instance = chat-intent v1->v2 (cull leg open);
  a complete generational loop on a live campaign
  population is NOT_ESTABLISHED this epoch (0 culls in
  the 717-event wallet ledger of record).
  Epoch likewise defined, ML sense (owner addition 3):
  one full pass over the dataset of record (repo +
  session + telemetry corpora + books/ledgers), bounded
  by the wall; two axes stated - pass axis epoch >
  cycle > iteration, evolve axis = generation; neither
  axis borrows the other's completion.
  Role register of the epoch (owner commission,
  companion layer): `docs/ops/DOE-ROLES-EPOCH-2026-11-03.md`
  assigns Registry-SSOT roles (builder - operator -
  steward - observer - reviewer - scout - gambler -
  participant) + one-line duties as practiced to the
  epoch's work-streams (pool program - census/validation -
  methods + Lean - QUE/dispatch - tribute diagnostics -
  D1 slate/freeze), incl. the DoE-pool x Desk-QUE wiring
  {operator consumes - steward keeps the ledger -
  reviewer holds integrity}; bookmaker + 11th man listed
  RESERVED-ABSENT; practice word "custodian" mapped to
  steward, stated for Registry concurrence.

## Campaign layout

### Candidate method versions — dreambeans concepts (owner ruling, 2026-11-01)

Registered as versioned implementation concepts in the evolution
substrate — the DNA of the codebase performance selection systems —
available as contextual basis. Registration is not adoption and
not a run: candidates evolve under rule 8 (versioning, backfill,
continuous comparison) and culling, and a candidate executes only
through an admitted campaign design.

POOL (census 2026-11-01): the candidate population is 126
unique dreambeans cards (145 PNG in Drive, 16 duplicate groups
flagged-only, no deletions), enumerated with title-level triage
classes in `docs/ops/DOE-DREAMBEANS-POOL.md` — 4 registered
(the source cards of the entries below), 14 fit-eval queue,
5 trading-domain flagged, 103 pool-parked. The pool is the
denominator for selection evidence over the register.

- **bisociation v0** (candidate; spec: doe-expert fit evaluation
  2026-11-01) — cross-frame generation operator (Koestler): collide
  two unrelated frames' relational structures to generate variants
  the intra-frame operator (rnd v1) cannot reach. Form: frame-pair
  selection from distinct domains (stamped like selection_reason),
  structure mapping (relations carried across, named), variant
  emission into the design pool; admission stays design-gated
  (rule 5); Delphi remains evaluation-only. Test form: variant
  source as factor vs rnd v1 {design-admission rate, culling
  survival, ESTABLISHED-gate outcomes}. Mesa agent-based modeling
  attaches in the control seat only (rule 6): pre-screening,
  observational, never live evidence. Boundary: the sources'
  market-network domain as a built/traded system is the frozen
  trading lane — the operator is domain-neutral, the domain does
  not transfer.
- **dual-accumulator arbitration v0** (candidate; spec: Delphi
  seat 5565cdf5 hand-down, 2026-11-01; fit evaluation at main
  cff94ce9). Status: specified_not_run — registration is not a
  run; holds until a briefed pass. Origin: owner integration
  consideration 2026-11-01. Source basis (seat's honesty grade:
  analogy-grade, n=6/single-task — licenses hypothesis, not
  validation): Starkweather et al., Nat Neurosci 2026-09-15,
  DOI 10.1038/s41593-026-02444-4 — medial OFC = approach
  accumulator, lateral OFC = avoidance accumulator, race to
  threshold. (TRN-gating and state-space elements of the original
  consideration are not in this candidate — framing/deferred.)
  Problem (decision-layer): incumbent aggregation (weighted mean)
  collapses support and objection into one signed value ⇒ risk is
  compensable by impact; vetoes ride brittle substring
  comparators (incident 2026-11-01: "cards" → false money-veto);
  fixed 3-round schedule spends full budget on round-1-decisive
  evidence.
  Mechanism: per candidate per round, ballots decompose into
  A_r (approach: weighted Σ of positive rubric contributions)
  and V_r (avoidance: weighted Σ of STRUCTURED risk signals as
  ballot fields — risk flags, cost_auditor objections, veto-class
  findings; text/substring scanning excluded as a V source, a
  design requirement from the incident). Weights = panel weights
  of record (#1489); the variant changes AGGREGATION ONLY.
  Accumulators A, V monotone append-only, per-round trajectories
  receipted. Decision = first crossing: A ≥ τ_allow ∧ V < τ_risk
  ⇒ approach outcome; V ≥ τ_risk ⇒ avoidance outcome REGARDLESS
  of A (non-compensability = the core invariant); both cross
  same-round within ε ⇒ TIED ⇒ DEBATE callable (tie law
  preserved); budget exhausted (max 3 rounds) with no crossing ⇒
  ABSTAIN, trajectories published. Early stop on crossing.
  Shadow discipline: incumbent weighted-mean runs in parallel on
  identical ballots, reported beside, never merged; promotion
  requires a pass verdict, not registration.
  Invariants held: source classes separate (never pooled);
  ballots require rationale + evidence_refs; kernel 3-class
  output shape unchanged; #1489 updates still require
  corroborated confirmed outcomes.
  Priors (pre-registered by the seat, for replay on recorded
  ballots — Strands, Temporal, Kiroween r1, marketing r1):
  (i) high concordance on clear cases; (ii) marketing
  partner-forward-blend: V crosses via the structured
  unresolved-claims signal (reproduces its round-1 loss by
  mechanism, not substring accident); (iii) Strands
  identical-profile tie stays TIED (any separation = invented
  signal = spec defect); (iv) no historical ALLOW flips to
  ESCALATE on replay (a flip = defect signal).
  Threshold anchors (v0, from the seat's registration block):
  τ_allow anchored on the shadow_min 15.0 analog (25-pt scale);
  τ_risk set so ONE corroborated consequential-risk signal
  crosses it (preserves the kernel rule risk_tier=consequential
  ⇒ ESCALATE); all values fixed at brief time, not at
  registration.
  Open parameters (brief-time): τ_allow, τ_risk, ε values;
  V increment schedule per signal class; whether gate pass/fail
  enters V as a prior. Non-goals v0: weights-estimator change
  (state-space deferred); intake pre-filter (TRN framing);
  kernel edits; implementation (builder ≠ evaluator when a run
  is briefed). Review: the Delphi lane reviews any future pass
  record against this spec (reviewer pattern as on #1963).
  Home refs (seat's registration block): no dedicated issue/PR
  yet — this register entry is its first home. Provenance chain:
  fit evaluation at main cff94ce9 (2026-11-01, Delphi seat) →
  owner ruling via main → spec hand-down (Delphi seat, this
  registration). Family of record: RFP #1963 (delphi method
  self-application, sibling method-variant slate); ledgers #1489
  (weights) / #1487 (outcomes); kernel of record =
  timerloggedout-spec/delphi-oracle at 393e1f4b.
- **interface-gates / symmetrical-action-log v0** (candidate;
  spec: D3 seat 39fc8b89 eval, 2026-11-01, from D3/ListingLens
  ground truth, PR #2616 verified; source eval at main 98387e77).
  Three components:
  C1 *schema-gates*: every agent output passes schema validation
  before render (zod schema + action outputSchema; malformed
  payload ⇒ blocked and surfaced, no partial render). Instance:
  {PhotoInput, ListingPackage, ReviseListing} + accept/reject
  tests.
  C2 *verified-blocks*: layout is a closed set of pre-styled
  primitives/templates; the model hydrates slots only
  {template_id, section_order fixed}; no free-form structure from
  the model. Instance: {hero-spotlight, gallery-grid} composed
  hero→story→details→shipping.
  C3 *symmetrical-action-log*: agent calls and user actions are
  twin events in ONE append-only log {actor: agent|user, action,
  payload-ref, rev} feeding the review panel; revision provenance
  is log-derived. Instance-state GAP: current = {model-id + rev
  counter} only ⇒ C3 is the novel element of this candidate.
  Non-fits (seat's record): Builder.io CMS validation-hooks /
  custom-components SDK = product binding, not part of the
  candidate (host is framework-agnostic — Agent-Native
  defineAction instance); name-origin "Delphi Desk" = killed
  proposal #42 (2026-10-28) — the candidate carries mechanics,
  no branding. D3-application: B6 (C3 only) arm-gated, unchanged.
  Params (seat's refs supplement, 2026-11-01): gates =
  {input-schema, output-schema} for every action, block-on-
  malformed; blocks = closed template set; log-event = {actor,
  action, payload-ref, rev} append-only. Home refs: impl =
  apps/listinglens/src/{schemas.mjs, actions.mjs, pipeline.mjs,
  ListingStudio.jsx} at master 6ea0e52b0d95 (PR #2616), mirror
  timerloggedout-spec/listinglens at 59c6c3b0427d; eval = main
  98387e77 + verify comment 6539405844 on PR #2616.
- **strands-patterns v0**, incl. the AST-complexity stamp feature
  (candidate; spec: Swarm seat 6628d41d eval, 2026-11-01; full
  eval text at main, sub d3660a72). A 4-component concept set,
  verdicts recorded as the concept's evidence:
  (1) *Swarm pattern* (Strands Agents SDK, Apache-2.0: co-located
  agents self-coordinating via shared memory + dynamic peer
  handoffs; siblings agents-as-tools, Graph, A2A) — DEFER: our
  Swarm is a provider population coordinated via GitHub, not an
  in-process runtime; no AWS estate/home; self-organizing handoffs
  conflict with designed-where-deliberate doctrine. Graph approx
  our workflow gates (already operated).
  (2) *AST-complexity stamp feature* — PILOT-WORTHY, SDK-free:
  Tree-sitter parse of a dispatch's produced diff → per-unit
  features {cyclomatic (decision-point count), max nesting depth,
  function size} emitted as extra stamp fields via the existing
  fan-out; purpose = per-arm reliability/complexity drift across
  repeat runs of a task class (candidate feature for 3L0/DoE
  folds). Guardrails: observational-only until corroborated like
  other stamp features; gaming risk explicit in the source —
  never a standalone verdict input. Evidence honesty (seat's
  record): the source article names no Tree-sitter and gives no
  CI aggregation/thresholds; the cross-run benchmark method is
  owner synthesis, recorded as such.
  (3) *Durable session storage (DynamoDB)* — NO FIT (current
  substrate): our state is git-store + Neon; overlaps HindSight's
  memory role. Recorded correction: the source makes no
  cross-region/failover claim — any failover property attributed
  to this candidate is unevidenced.
  (4) *OTEL observability pattern* — informational; parallels our
  stamp telemetry, no registration action.
  Parameters (v0, from the seat's registration spec): pattern
  vocabulary = {Swarm (shared-memory self-coordination, dynamic
  peer handoffs) · agents-as-tools (specialists callable under an
  orchestrator) · Graph (deterministic nodes + conditional edges —
  vocabulary mapping only) · A2A (agent-card interop)}. AST stamp:
  aggregation per dispatch {cyclomatic_max, cyclomatic_mean (per
  changed function), nesting_max, functions_changed, diff_loc};
  carriage = stamp field `complexity` on the routed-dispatch
  record (fan-out emitted; backfill-derivable from retained
  diffs); fold class = observational-only (Δ=0 until a later
  version promotes it on corroborated outcome correlation);
  anti-gaming constraint as in (2). Home refs: eval report at main
  sub d3660a72 + registration spec (Swarm seat, 2026-11-01); lane
  doc `docs/ops/SWARM-OPTIMIZATION-ASSURANCE.md`; provider
  evidence ledger issue #3141.
  Versioning: v0 = as-evaluated 2026-11-01 by the Swarm seat;
  verdicts revisable only on new firsthand data (a hosted-runtime
  decision reopens 1+3; a complexity-feature pilot graduates 2's
  evidence class).

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
  Evaluation shape (owner restatement, 2026-11-01): the
  contender's dispatches route through the SWARM population
  (the routed-dispatch plane; no hard-select, no direct-to-model
  dispatch — direct dispatch to model was questioned by the
  owner, the swarm is demanded). Evidence toward the title
  counts only from population-routed dispatches; direct-to-model
  runs are observational color and do not count toward the gate.
  This restates the standing dispatch principle (work routed
  across comparative planes) for the arena.
  Baseline (owner Δ, 2026-11-01): the OPERATOR is already wired
  automated — the bet sits on top of that live automation and
  does not gate it.
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

### Speculators mapping (2026-11-02)

The Speculators harness (`scripts/speculators/evaluate.py`,
campaign `token-strategies-1`, issue #195) evaluates speculative-
decoding token strategies from `timerloggedout-spec/
speculators_fork` (@ c13304cf3ec2) against verifier models. Its
registry (`scripts/speculators/strategies.py`) is the schema
surface: each strategy entry is a configured draft-side, so the
canonical registry JSON → `system_prompt` ref
(`scripts/speculators/strategies.py#<strategy>`; sha256 over the
canonical entry); `provider` = `speculators_fork`; `model` =
`<verifier>+<strategy>` (verbatim pair — the same verifier under
eagle3 vs dflash is two configured instances); fork train +
vLLM serve → `tools` ref `tools:speculators:evaluate`; `role` =
`evaluation`; the campaign → `context`; `moniker` = `speculators`.
Provider phrases follow the family rule above: a design may
declare `provider_phrases` per verifier route or a `phrase_layer`
block (JIT layer over the provider-phrases SSOT) — composed into
the strategy prompt and covered by its hash; the token-
strategies-1 routes are local vLLM serving routes with **no
established phrase set**, so its design records
`provider_phrases: {}` (NOT ESTABLISHED, not silently skipped).
`record` emits one EXPERIMENT record per run (acceptance rate,
mean accepted length, speedup, lossless flag in metrics) plus
SUMMARY with the pre-registered selection rule; the lossless
gate — any run whose output differs from verifier-only decoding
disqualifies its cell — is the campaign's validity condition,
not a metric preference.
