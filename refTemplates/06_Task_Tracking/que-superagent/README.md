# que-superagent reference templates

Templates porting the dsh-superagent domain model into QUE. Map: `docs/proposals/active/que-superagent/LESSONS.md`.

| File | Use |
| --- | --- |
| `que-ticket.md` | A QUE item (Ticket) with its immutable Mandate block |
| `que-eval-decision.json` | JSON Schema for one admission Decision: accept \| stop \| ignore \| unavailable |
| `que-report.md` | An executor Report (progress \| waiting \| ready \| blocked \| failed \| dropped) ∧ optional attention question |
| `que-policy.yaml` | Versioned rules, per-Source allowed lists, accept mode shadow \| live |

Code of record for the machine blocks: `scripts/que/que_item_fields.py` (P1).
