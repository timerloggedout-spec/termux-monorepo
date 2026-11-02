# OWNER-RECORDS INVENTORY — what the tracking surface holds vs lacks

Audit (tracking lane, 2026-11-01, firsthand vs master: tracking feed +
full repo tree of 11,087 blobs + named sources read in full) for the
owner visual layer (owner direction via main; Web Dev scope). Machine
form: `ops/tracking/owner-records-inventory.json`
(`owner-records-inventory/v1`). This file is an audit artifact, **not**
a workflow output — refresh by tracking-lane PR.

**Surface today:** `repo-tracking/v1` top-level blocks =
{rows, doe_join, summary, sources, honesty_rules, gaps}. There is **no
owner-records block**. All 8 owner/gate string hits in the feed are
incidental prose (2 free-text `next` strings quoting owner orders, 2 PR
titles) — no structured owner-record field exists anywhere in the feed.

| class | verdict | record of record | tracking surface |
|---|---|---|---|
| gates | **PARTIAL** — record HELD, surface LACKS | `docs/ops/GATES-REGISTER.md` (9 gate-type sections, ~49 rows, states CLOSED/OPEN/RESOLVED/TRANSIENT; single-writer main) + coordinator `events[].gates[]` {id, label, blocks, owner, status} | reads coordinator.json but ignores its `gates[]`; never reads the register |
| decisions | **PARTIAL** — register HELD (table/prose), surface LACKS | `docs/ops/OWNER-REQUESTS.md` (OPEN 16 rows + RESOLVED w/ evidence refs; row {item, lane, what's-needed, since, blocks}) | reads neither; rulings appear only as prose in docs/`next` strings. (ACTION-DECISION-LEDGER.md is proposal-level, **not** owner decisions — do not mis-join.) |
| authorizations | **LACKS** — no record exists | none (`phase-approvals.json` checked: `{"approvals": {}}`, an empty agentic stub; standing orders live as doctrine prose only) | nothing (0 mentions) |
| clearances | **LACKS** — class does not exist | none (tree search clearance*/consent* = 0 files). RESOLVED states in the two registers are de-facto evidence only — neither names who cleared what for which scope | nothing (0 mentions) |
| bets | **LACKS** — schema HELD, data absent | `docs/proposals/active/model-selection-market/schemas/bet-ledger.schema.json` (BetLedgerEntry) is the only bet artifact in the tree; **no ledger data file exists**. The one owner bet-of-record (2026-11-01, via D2 seat) lives only in VM lane memory, never landed in-repo — its repo absence is the finding | nothing (0 mentions) |

## Consumable next (for Web Dev, fixture-first)

Proposed feed block `owner_records` (top-level, alongside
`rows`/`doe_join`) in `repo-tracking/v1`, single-writer stays
`repo-tracking-collect.yml`; build owner = tracking lane on main/Web
Dev go:

- **gates** (live-able now): row `{item, gate_type, state, holder,
  scope (register|challenge-event), event_id?}` from GATES-REGISTER.md
  + coordinator `events[].gates[]`.
- **decisions** (live-able now): row `{item, lane, whats_needed,
  since, blocks, section (open|resolved), evidence_refs}` from
  OWNER-REQUESTS.md.
- **authorizations**: `NOT_ESTABLISHED` — no source; row proposal
  `{item, scope, authorized_by, at, evidence_ref, state}` once a
  register exists.
- **clearances**: `NOT_ESTABLISHED` — no source; row proposal `{item,
  cleared_by, at, scope, evidence_ref}`.
- **bets**: schema only; rows adopt `BetLedgerEntry` verbatim when a
  ledger file lands.
