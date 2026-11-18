# Grimoire ↔ Recipe Craft — Cauldron Recon

**Status:** concept mapping only; no existing component named Cauldron was found in the inspected repository paths.
**Ownership:** unassigned. **Execution:** not authorized by this document.

## Finding

The repository already has a Grimoire vocabulary and protocol. It does not, on the evidence inspected for this recon, have a documented Grimoire subsystem or runtime explicitly called **Cauldron**.

The existing vocabulary maps:

| Existing Grimoire term | Repository-defined meaning | Recipe/craft relationship |
|---|---|---|
| Grimoire | Run history / scorebook; spells and history | Historical record and vocabulary context, not a recipe composer |
| Spellbook | Task queue | Candidate work intake/queue; not recipe storage |
| Rune | Prompt template | Reusable instruction ingredient/template |
| Incantation | Reusable CLI spell | Reusable procedure or command pattern |
| Cast / Caster | Execute / agent | Execution vocabulary; a recipe must not imply permission |
| Transmute | Refactor | Transformation operation |
| Scry | Review / inspect | Inspection and review operation |
| Probe | Test | Validation operation |
| Echo | Fragment match | Retrieval/matching operation |
| Phylactery | Backup | Recovery/protection reference |

Sources:
- `harmony_hub/config/GRIMOIRE_DICTIONARY.md`
- `harmony_hub/config/grimoire/1337_D1CT10N4RY.md`

The existing `archwiz/name_forge.py` reads Grimoire terms to suggest names. Its source describes a **name suggester**, not a recipe builder, recipe registry, or collision-clearance service.

## Proposed interpretation: Cauldron as a workbench, not a new authority

If the Cauldron metaphor is useful, define it narrowly as a **composition workbench** over existing recipe and craft assets:

1. **Gather** — discover candidate ingredients: Rune prompt templates, Incantations, skills, tools, APIs, libraries, workflow patterns, tests, policy references, and prior recipe records.
2. **Inspect** — Scry sources; preserve immutable provenance, owner, version, confidence, and evidence class.
3. **Prepare** — normalize inputs, check preconditions, resolve dependency references, and expose missing/unknown ingredients.
4. **Compose** — arrange operations into a candidate procedure/DAG; express ordering, branches, loops, waits, dependencies, and output contracts.
5. **Temper** — Transmute/refactor the candidate; run static and contract checks only within existing read-only/admitted boundaries.
6. **Probe** — attach test/evaluation criteria and evidence references. A passing static check is not runtime proof.
7. **Record** — publish a versioned candidate recipe reference into the appropriate existing owner-controlled registry/ledger; link run observations to canonical DoE and orchestration receipts.
8. **Serve** — expose the recipe to existing Spellbook/task intake or orchestration only through their existing interfaces and authorization checks.

This is a proposed user/workflow concept, not a claim that these steps or a Cauldron runtime already exist.

## Boundary map

| Concern | Existing authority / contract | Cauldron boundary |
|---|---|---|
| Recipe structure | Proposed neutral Software Recipe Model (SRM) | Compose candidate SRM records; do not create a second schema |
| Session provenance and reconstruction | External Repo Replay | Link its recipe references; do not reimplement replay |
| Git fragment composition | Commit Replay / `grecipe/v1` | Link its fragment recipes; do not merge replay planes |
| Orchestration treatment and cycle evidence | `ORCHESTRATION-TREATMENT.schema.json` and `ORCHESTRATION-RECEIPT.schema.json` | Reference canonical treatment/receipt records; no new run ledger |
| Experiment design and observations | `docs/ops/corpus/EXPERIMENT.schema.json` | Reference canonical DoE records; no experiment-ledger fork |
| Vocabulary and notation | Grimoire, Linguist, Siglary | Reuse issued terms; submit new terminology through existing governance |
| Task intake and scheduling | Spellbook / existing orchestration authorities | Hand off by existing contracts; do not create a scheduler |
| Permissions and execution | Existing policy, sandbox, execution and promotion owners | Never infer or grant authority from recipe composition |

## Minimum candidate recipe lifecycle

`discovered → extracted → normalized → composed → statically_checked → candidate → independently_validated → admitted`

The lifecycle is descriptive. States must remain evidence-backed and owner-controlled. `candidate` is not `admitted`; `validated` is not `promoted`. Unknown, stale, disputed, blocked, and unavailable states must remain visible rather than being silently repaired.

## Initial acceptance checks

- Every ingredient has a stable source reference, revision/digest where available, owner, and evidence class.
- Every operation declares intent, inputs/outputs, dependencies, effect class, and applicable policy reference.
- Composition rejects unresolved hard dependencies and reports uncertainty; it does not silently invent missing ingredients.
- Recipe similarity does not imply equivalence or compatibility.
- The workbench has no direct secret access, external-write capability, deployment authority, or self-promotion path.
- Execution, if ever considered, requires a separate threat model and explicit admission by existing authorities.
- Existing Repo Replay, Commit Replay, Grimoire, Spellbook, Name Forge, DoE, CRG, and orchestration contracts remain distinct.

## Decision

**Do we already have a Grimoire-related Cauldron?** No explicit Cauldron component was found in this bounded source inspection.

**Do we have recipe-and-craft foundations?** Yes: Grimoire's reusable Rune/Incantation vocabulary, Spellbook task queue, Cast/Transmute/Scry/Probe/Echo operations, Name Forge, the separate Repo Replay and Commit Replay recipe planes, and the proposed SRM domain model.

**Recommended next move:** treat “Cauldron” as a candidate interaction/workbench metaphor and validate the user journey against existing systems before creating a package, service, Brain assignment, registry, or public name. No new component is justified by the metaphor alone.
