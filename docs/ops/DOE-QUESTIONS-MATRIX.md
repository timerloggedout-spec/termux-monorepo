# DoE Questions Matrix

**`doe-questions-matrix` v1** — registered 2026-11-02 under
DoE governance (see `docs/ops/DOE-FAMILY.md`, Method
versions). Owner directive 2026-11-02: the DoE questions
matrices require more breadth and depth — larger dimension
considerations, nested::research.

## Before / after

BEFORE: the question dimensions lived flat, scattered across
surfaces — the multivariate-doe skill's factor space (core 6
{provider · model · prompt · manager · cohort · sequencing}
+ 8 extensions {task family · task instance · scope/ref ·
tool policy · context budget · concurrency policy ·
validation policy · recovery policy} = **14 dimensions, one
level, no per-dimension research structure**), the outcome
chain, and dimensions that existed only as RULES (instance
identity, corroboration, accumulation, backfill origin)
without matrix form.

AFTER: **40 dimensions in 6 clusters**, every dimension
carrying sub-dimensions in the nested::research scheme:

```
dimension
├─ question      — what this dimension asks of a run
├─ sub-dimensions — the nested splits that change the answer
├─ levels/evidence — what values it takes, from which record
└─ research      — the open refinement this dimension carries
```

Every added dimension is an OMISSION REPAIRED, not an
invention: each names a fleet mechanism that already
produces the variation (cited per cluster) but was never a
matrix dimension, so its effects were absorbed into noise or
misattributed to a listed factor.

## Cluster A — SUBJECT (who/what is treated)

1. **provider** — Q: which inference provider? Subs:
   {endpoint class · account/tier}. Levels: registry of
   record. Research: provider-vs-account confounding.
2. **model@version** — Q: which model, provider-verbatim
   version? Subs: {version pin state (exposed |
   NOT_ESTABLISHED) · alias vs pinned id}.
3. **configured instance** *(omitted before)* — Q: which
   configured instance (instance_key doctrine)? Subs:
   {system_prompt ref+hash · tools ref+hash · role ·
   moniker · context class}. Evidence: intake stamps.
   Research: which tuple elements move outcomes most.
4. **manager / policy** — Q: under which manager + policy
   version? Subs: {manager seat · policy version ·
   steering intensity (interventions per run)}.
5. **team composition** *(omitted)* — Q: solo arm or a
   composed team? Subs: {roster · team manager · contract
   shape}. Evidence: team records (own stratum; member n
   never substitutes).
6. **selection path** *(omitted)* — Q: how did this unit
   come to run this task? Subs: {requesting manager ·
   selecting scout · selection basis = feed state at stamp}.
   Evidence: selection-experiment stamps.
7. **arm history** *(omitted)* — Q: what is this arm's
   lineage? Subs: {generation · cherry-pick lineage ·
   prior cull/promote events}. Evidence: cull wallet
   records, generation ledgers.

## Cluster B — TASK (what is asked)

8. **task family** — Q: which family of work? Subs:
   {family taxonomy ref · family size in window}.
9. **task instance** — Q: which concrete instance? Subs:
   {instance id · ref SHA · dedup state}.
10. **task complexity** *(omitted)* — Q: how hard is the
    instance, measured? Subs: {complexity stamp (AST class)
    · scope size · dependency depth}. Research: complexity
    as covariate vs as factor.
11. **novelty** *(omitted; live-1's factor, absent from the
    skill list)* — Q: greenfield or iteration? Subs:
    {greenfield | iteration · iteration depth (round n)}.
12. **scope/ref stability** — Q: did the target move?
    Subs: {base SHA pinned? · mid-run base movement}.
13. **stakes** *(omitted)* — Q: what rides on the outcome?
    Subs: {competition-linked? · wall proximity class ·
    reversibility}. Research: stakes as a blocking factor
    for promotion decisions.

## Cluster C — TREATMENT (how it is run)

14. **prompt variant** — Q: which prompt/JIT phrase? Subs:
    {variant id · generation method (rnd phrase pool) ·
    density/register class}.
15. **tool policy** — Q: which tools, under what policy?
    Subs: {tool set ref+hash · permission class}.
16. **context budget** — Q: how much context? Subs:
    {budget · utilization at dispatch}.
17. **context composition** *(omitted)* — Q: WHAT is in the
    context? Subs: {memory/backfill state · cited records
    carried · compaction state}. Research: composition vs
    budget as separate effects (budget alone conflates them).
18. **sequencing / order** — Q: in what order? Subs:
    {position in set · set_index (rule 7) · predecessor
    treatment}.
19. **concurrency policy** — Q: how much parallelism?
    Subs: {admission state · lane concurrency cap}.
20. **decoding parameters** *(omitted)* — Q: which sampling
    settings? Subs: {temperature · top-p · max tokens,
    provider-default vs set}. Research: defaults drift
    silently between provider deploys — pin or record.
21. **retry / recovery policy** — Q: what happens on
    failure? Subs: {retry count · reroute path ·
    reroute-prior-to-failure events}.

## Cluster D — ENVIRONMENT (where/when it runs)

22. **dispatch route** — Q: which route carried it (rule 6:
    re-verified at design ∧ dispatch)? Subs: {route id ·
    route health at dispatch}.
23. **quota / capacity state** — Q: what did capacity look
    like? Subs: {bucket state · replenishment phase ·
    headroom class}. (Capacity variable, never a quality
    score — design rule 8.)
24. **time window** *(omitted)* — Q: when, relative to the
    cycles that govern the fleet? Subs: {quota-window phase
    · wall-clock proximity to deadlines · cohort window}.
25. **substrate** *(omitted)* — Q: which execution surface?
    Subs: {Actions · VM · device (B160V class) · local}.
26. **dependency state** *(omitted)* — Q: were the run's
    dependencies up? Subs: {critical dependency state ·
    failover tested?} (dependency-graph records;
    critical ∧ down ⇒ claims capped HELD).

## Cluster E — MEASUREMENT (how truth is established)

27. **outcome stage** — Q: how far did it get? (chain:
    execution status → task outcome → correctness →
    integration → regression → resource cost; a route that
    never executed is not a model failure.)
28. **oracle class** *(omitted)* — Q: who/what judges
    correctness? Subs: {deterministic gates · judge arm
    (≠ builder) · formal oracle (NSE-023 class) · human}.
    Research: oracle-class agreement rates.
29. **validation policy** — Q: which validation legs ran?
    Subs: {legs count · independence of legs}.
30. **corroboration state** — Q: rule-9 state of the
    record? Subs: {legs · agreeing · conflicts · publisher
    leg}. (Transport vs authorship strata kept separate.)
31. **stratum** — Q: which population does this record
    belong to? Subs: {stratum id · pooling eligibility}
    (wrong-stratum n counts as zero).
32. **accumulation** — Q: how much evidence stands behind
    the claim? Subs: {n vs class target · exploration share
    of n}.
33. **evidence provenance** *(omitted)* — Q: how is the
    evidence itself anchored? Subs: {pointer resolves ·
    hash match · live (merged ≠ served)} (validation-lane
    pointer classes).

## Cluster F — ADAPTATION (how the experiment learns)

34. **generation / cohort** — Q: which generation? Subs:
    {cohort id · cohort/ref stability (design rule 5)}.
35. **variation operator state** — Q: how was this unit's
    treatment generated? Subs: {rnd mix id · generator
    (factorial | taguchi) · complement-cohort state}.
36. **selection pressure** — Q: what generational selection
    produced this population? Subs: {cherry-pick proportion
    (per-design parameter) · complement persistence}.
37. **culling state** — Q: has this participant been
    culled, or is it cull-adjacent? Subs: {standing ·
    wallet state · pool flows}.
38. **exploration share** — Q: how much of the window was
    exploration? Subs: {exploration n / total n ·
    health-gate bounds on exploration}.
39. **backfill origin** — Q: is this record live or
    reconstructed (rule 8)? Subs: {origin · backfill method
    + method_version · from/to span}.
40. **automation binding** — Q: what automation ran this
    (rule 5)? Subs: {automation ref in DESIGN ·
    admitted_design_only flag} (unbound runs =
    OBSERVATIONAL).

## Use

- DESIGN records cite dimensions BY NUMBER from this
  matrix; a factor not in the matrix is proposed as a matrix
  amendment first, never improvised per-design.
- The skill's flat factor list is the CORE PROJECTION
  (dimensions 1, 2, 14, 4, 34, 18 + the B/C extensions as
  listed there); this matrix is the full space it projects
  from.
- Amendments are versioned (rule 8 discipline): a dimension
  added, split, or culled is a new matrix version with the
  delta stated — dimensions are never silently renumbered;
  retired numbers stay retired.
