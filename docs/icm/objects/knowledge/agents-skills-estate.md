---
type: object
cluster: knowledge
universe: live
status: initiated
entity: .agents/skills/
verified_at: 2026-11-01
---

# Agents Skills Estate

`.agents/skills/` is the repository's fleet skill system: **28 skills**, each a directory holding a `SKILL.md` playbook and, for some, a `references/` folder. The estate registry is `docs/ops/SKILLS-INVENTORY.md`. This card routes skill questions to the estate and its registry; it is not a per-skill index and does not restate skill contents.

## Boundary (load-bearing)

- A `SKILL.md` is a **capability/playbook definition** — what an agent should do. It is **not evidence of a certified skill**. Certified evidence is issuer artifacts (cert ID, date, verify link) plus execution receipts, governed by the certifications program (see the Challenge and Certifications Program card).
- Skills are maintained in place by their owning lanes; adding or retiring a skill updates the registry, not this card.
- Do not load the whole estate into context: pick the one skill the task names, via the registry.

## Read when

- Choosing or invoking a fleet skill for a task.
- Adding, renaming, or retiring a skill (registry update path).
- Checking whether a capability already exists as a skill before building a new one.

## See

- Estate: [`.agents/skills/`](../../../../.agents/skills/)
- Registry: [`docs/ops/SKILLS-INVENTORY.md`](../../../../docs/ops/SKILLS-INVENTORY.md)
- Evidence boundary: [`../operations/challenge-program.md`](../operations/challenge-program.md)
