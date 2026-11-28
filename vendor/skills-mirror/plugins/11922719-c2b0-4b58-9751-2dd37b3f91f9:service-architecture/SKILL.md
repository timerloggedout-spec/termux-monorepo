---
name: service-architecture
category: Engineering
description: "Backend architecture decisions: service boundaries, splitting vs consolidating, inter-service calls, auth guards and tiers, where logic lives, strangler migrations. Load before adding or versioning an endpoint or a service-to-service call, or deciding which service owns something. Query performance is database-optimization.\n"
---

# Service Architecture

If `LOCAL.md` sits beside this skill, read it first: it carries this install's project
conventions, which are standing directives and win over the generic defaults here.

Goal: make sound service-architecture decisions, surface optimizations and trade-offs,
and apply already-decided patterns consistently. The main failure in this domain is
inventing a parallel solution to a solved problem.

## Workflow

1. **Search before you build.** Grep ALL the repos — legacy and new services — for the
   capability first. It frequently already exists under another name, and a wrong
   "missing feature" guess in a plan costs more than the grep.
2. **Decide where the logic lives.** One service owns each table's writes: route writes
   through the owner (IPC), read pre-joined read models directly — two writers on one
   table is how data diverges. Pick the cheapest channel that respects ownership
   (direct read model < owning-service IPC < queue/event). Prefer deriving a value from
   data that already holds the truth over adding a column + migration.
3. **Weigh consolidation vs. split.** Modules merged into one service call each other
   in-process (DI); keep the interservice client only for genuinely external services —
   re-IPC-ing into yourself adds latency and a failure mode for nothing. Shared libs a
   frontend consumes stay free of server-framework decorators and dependencies.
4. **Auth at the boundary, re-derived at the service layer.** One endpoint serving
   several caller types uses ONE composite, ordered, short-circuiting guard with
   per-route config — duplicated endpoints per audience drift apart. Default to deny;
   fail closed. The guard answers "may you touch this resource?"; the service still
   clamps what the caller may grant or change.
5. **Migrate incrementally.** Move the client-facing surface (URL + auth + docs + tests)
   first, keep delegating to the legacy engine when reimplementing it is large or risky,
   and delete the old endpoint only after confirming nothing else uses it.
6. **Verify the wiring live.** Guard/provider/module changes are invisible to unit tests
   (mocks never build the DI graph) — a real boot is the only proof the change resolves.

The patterns behind each step, with their caveats:
[general-principles.md](general-principles.md).

## Common failure modes

- **Mutating an existing endpoint's auth/shape in place** instead of adding a sibling
  version and migrating the consumer (Hyrum's Law: every observable behavior becomes a
  contract someone depends on).
- **Swapping a guard without checking what it wrote to the request** — handlers may read
  a field the old guard set; a pass/fail-only replacement silently opens an authz hole.
- **An auth decorator without its guard is inert** — metadata does nothing until a guard
  reads it, so the route is silently OPEN.
- **Fanning out one external API call per list row** — keep a synced read model for
  sortable/filterable columns and refresh only the visible page on demand.
- **Building a parallel admin UI** when the same permission-gated screens can serve both
  audiences — then failing to verify the lower tier can't reach the privileged actions.
- **Stampeding boot-time tasks** — gate them (advisory lock + change detection) so N
  instances booting don't all write.

## Related skills

- [deprecation-and-migration](../deprecation-and-migration/SKILL.md): the mechanics of moving logic off a legacy service once this skill has decided where it lands.
- [code-quality](../code-quality/SKILL.md): the hard rules every backend diff meets — one responsibility per file, readable by a junior engineer, and one rhythm per kind of work (every endpoint moves data through the same stages).

## Capturing learnings

Record architectural decisions, the reasoning, patterns adopted and anti-patterns to
avoid in `LEARNINGS.md` beside this skill, when your copy keeps one. Pull the general
principle out into the general-principles reference, and keep project-specific
conventions in `LOCAL.md`. Dedupe and merge; if any one file grows past ~250 lines,
split it further.
