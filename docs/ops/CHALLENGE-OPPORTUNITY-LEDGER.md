# Challenge Opportunity Ledger

Append-only ledger of opportunity cost across the challenge slate.
Machine source: `ops/challenge/opportunity_ledger.json`; event state:
`ops/challenge/coordinator.json`; DB store: Neon via
`scripts/challenge/participant_event.py` (table
`opportunity_ledger_entries`, append-only; view
`opportunity_ledger_totals`).

**Rules:** entries are never edited or deleted — corrections land as
new entries referencing the corrected one. Every event outcome
(submitted/not, placed/not) appends an entry at close. Live events
near deadline with no submission carry `AT_RISK` entries
(`gross_foregone` 0 until close). The totals block is derived and
recomputed on each append. Ledger carries gross only — no EV figures
(win probability is a hidden MoneyBall-internal metric,
`coordinator.json metrics_internal`, per the 2026-10-28 ruling).

## Entries

| id | event | top award | status | gross foregone | basis |
|---|---|---|---|---|---|
| OC-001 | Strands Decider (Oct 16–23) | $5,600 ($5,000 AWS credits + ~$600 swag bundle) | **LOST** | 5600 | owner ruling 2026-10-28 ("$5,000 = LOST"); corroborated PR #2229 (not submitted) |
| OC-002 | D0 Weekend Challenge (Oct 23–26) | $200 ($100 AWS credits + Builder Backpack) | **LOST** | 200 | verified record: 0 submissions, platform Ended |
| OC-003 | D1 Workshop to Ship (Oct 28–Nov 4) | $5,600 ($5,000 credits + ~$600 swag + certificate) | **AT_RISK** | 0 | live, deadline Nov 4, no submission yet, workshop gate open |
| OC-004 | corrects OC-001 | $5,000 AWS credits (1st-place only) | **LOST** | 5000 | owner correction 2026-10-28 |
| OC-005 | corrects OC-002 | $200 (unchanged) | **LOST** | 200 | owner correction: EV field removed |
| OC-006 | corrects OC-003 | $5,000 (1st-place convention) | **AT_RISK** | 0 | owner correction 2026-10-28 |

## Running totals (as of 2026-10-28)

- **LOST: 2 entries — gross foregone $5,200** (credits $5,100 / swag value $100 / cash $0)
- **AT_RISK: 1 entry — exposure $5,000** (credits $5,000)
- WON: 0 — $0 · RECOVERED: 0 — $0

**Correction (owner, 2026-10-28):** LEDGER = 1ST PLACE ONLY — entries
record only the top (1st-place) award gross; `expected_value_foregone`
and win probability are removed from entries + totals. Correction
entries OC-004 (Decider 5600→**5000**), OC-005 (D0 200, EV field
removed), OC-006 (D1 AT_RISK 5600→**5000**) supersede OC-001..003;
totals above are over non-superseded entries. Win probability lives
only in coordinator `metrics_internal` (hidden, adaptive, silent).

— Ledger stood up 2026-10-28 by the challenge-entries-manager
assistant seat under owner ruling (via Manager).
