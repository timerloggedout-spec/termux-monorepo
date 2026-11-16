# Batteries pre-proofing and theorem reuse proposal

## Intent

`batteries_fork` should do more than sit as a passive submodule. It should provide a **pre-proofing lane**: before a new Lean-facing invariant is written from scratch, search for a known-working theorem, lemma, tactic pattern, or executable test that already covers the intended shape.

This is not a proof cache that blindly replays opaque answers. It is a provenance-aware catalogue of reusable proof ingredients whose compatibility is checked against the pinned Lean/Batteries revision.

## Research-first placement

Keep experiments under a governed `research/` area. Promote only validated artifacts into an applied namespace such as `appliedSxi` after its repository/ownership boundary and runtime dependency are explicit.

The submodule remains at:

- `refTemplates/smods/batteries_fork`

The initial fork pin remains authoritative. Do not silently follow upstream `main`.

## Pre-proofing pipeline

1. **State the proposition shape** — write the intended invariant in a small, typed form before implementation details.
2. **Normalize the goal** — identify types, assumptions, decidability requirements, algebraic structure, recursion shape, and expected computational behavior.
3. **Prefetch candidates** — search the local Batteries source, existing monorepo Lean work, and an explicitly recorded upstream/source revision for matching lemmas, theorems, tactics, examples, and tests.
4. **Record provenance** — candidate name, source path, source revision, Lean toolchain, import requirements, and license/source boundary.
5. **Adapt, don't counterfeit** — if a known theorem is close but not exact, create a small adapter lemma with an explicit relationship to the source theorem. Do not copy a proof and present it as independently derived.
6. **Check locally** — compile the smallest possible example against the pinned submodule before integrating it into an applied component.
7. **Generalize only after success** — extract reusable helper lemmas once a concrete proof has worked.
8. **Promote** — move the validated theorem/helper and its tests into an applied location only when its dependency contract is stable.

## Known-working theorem manifest

A future machine-readable manifest should contain entries like:

```yaml
- id: batteries.<stable-name>
  source: timerloggedout-spec/batteries_fork
  revision: 36cc05ca2d0e469bfbeea9437f460e19238e885e
  lean_toolchain: v4.34.0-rc1
  import: Batteries.<module>
  kind: theorem # theorem | lemma | tactic | example | test
  goal_shape: "<normalized proposition shape>"
  prerequisites: []
  adapter: null
  verified: true
  verified_at: "<UTC timestamp>"
```

The important property is **reproducibility**: a future proofing agent should be able to determine whether the candidate was actually checked under the same dependency/toolchain conditions.

## What counts as a pre-proof

Prefer four increasingly strong forms:

- **Pattern** — a known proof strategy or tactic sequence.
- **Lemma** — an existing theorem that can be applied directly.
- **Adapter** — a tiny local theorem translating the project's representation into the known theorem's representation.
- **Executable witness** — a theorem/example/test that is compiled and, where appropriate, executed against representative values.

A pre-proof is therefore a *validated starting point*, not a claim that the final proposition is already proven.

## Guardrails

- Never weaken a proposition merely to reuse a theorem.
- Never accept a theorem candidate solely because a name matches.
- Keep source revision and toolchain metadata with the candidate.
- Fail closed when imports or versions cannot be reproduced.
- Keep generated/search results separate from authored theorem statements.
- Treat upstream theorem changes as dependency drift requiring revalidation.

## Relationship to Aesop and other proof tooling

Batteries should be the low-level library substrate. Existing proof automation such as `aesop_fork` can be evaluated above it. The useful architecture is:

`Lean toolchain -> Batteries -> proof-search/automation -> project adapters -> applied invariants`

This avoids making Batteries itself responsible for agent behavior or application policy.

## First research milestone

Build one deliberately small proof packet that demonstrates the entire loop:

`goal -> candidate discovery -> provenance record -> adapter (if needed) -> compile -> regression test -> reusable manifest entry`

Do not optimize for theorem count. Optimize for a trustworthy, repeatable workflow.
