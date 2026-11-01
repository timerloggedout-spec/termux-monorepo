---
type: object
cluster: operations
universe: live
status: initiated
entity: docs/ops/CERTIFICATIONS-PROGRAM.md
verified_at: 2026-11-01
---

# Challenge and Certifications Program

The repository runs a coordinated **challenge-entries slate** (hackathons and competitions with fixed deadlines) and a **certifications program** whose rules of record are `docs/ops/CERTIFICATIONS-PROGRAM.md`. This card routes program questions to those records; program state (deadlines, entries, rung status) lives in the program's own records and management tree, not in this card.

## Rules that shape the map

- **Earner = `termux-monorepo`.** Its fleet automation earns certifications; side chats manage (oversight, enrolment, evidence) and are never recorded as earner.
- A cert/rung is complete only when the work ran via fleet automation, is telemetry-evidenced, and carries per-model attribution — full rule text in `docs/ops/CERTIFICATIONS-PROGRAM.md`; gate states in `docs/ops/GATES-REGISTER.md`.
- Competition-relevant certifications outrank baseline rungs; ordering follows live deadlines.

## Read when

- Routing a challenge entry, deadline, or submission question to the program's records.
- A certifications-derived skill or knowledge base is produced: those derived objects land on the **knowledge shelf** (`objects/knowledge/`) and are routed from this card once the Certifications program emits them. Until then this program has no derived ICM objects — that shelf state is deliberate, not a gap in this card.

## Surfaces

| Surface | Role |
|---|---|
| `docs/ops/CERTIFICATIONS-PROGRAM.md` | Rules of record for the certifications program |
| `docs/ops/GATES-REGISTER.md` | Gate states across the program |
| `docs/ops/` challenge records | Per-challenge briefs, evidence, and verdicts |
| `ops/challenge*` data surfaces | Participant/entry data — routed data estate, not ICM content |

## See

- Rules: [`docs/ops/CERTIFICATIONS-PROGRAM.md`](../../../../docs/ops/CERTIFICATIONS-PROGRAM.md)
- Gates: [`docs/ops/GATES-REGISTER.md`](../../../../docs/ops/GATES-REGISTER.md)
