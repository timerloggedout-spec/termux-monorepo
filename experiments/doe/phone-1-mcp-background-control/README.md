# phone-1 — MCP phone-control field population (DoE register)

`[MUSEai]@{role:{speculators-build}}` · landed 2026-11-04 under the
Phone MCP builder follow-on dispatch (owner via main → Desk QUE).

## What this is

The DoE data population for MCP-based phone control: the surveyed
field from the research dossier
`phone-mcp-background-control-20261104-1337`, landed in-repo so the
fleet's device-bridge build evaluates against records, not relays.

- `records/report.md` — the dossier report, byte-identical
  (source of record; web-derived, vendor claims labelled as such).
- `records/population.jsonl` — 20 units, one per surveyed system
  (7 name-matches for "Phone MCP" incl. 2 further collisions; 18
  survey rows; overlaps merged). Fields per unit: pattern class,
  connection shape, capability set as documented, background class
  (A/B/C per the report's taxonomy), governance notes, pricing,
  source refs, evidence level (verified_live | index | mixed |
  via_comparison_in_report — the report's own labels).
- `records/findings.json` — distilled findings: name-collision
  verdict (no single "Phone MCP"; the ad cannot be pinned down),
  background taxonomy, hard limits with no bypass found
  (credential lock, FLAG_SECURE, CAPTCHA hand-back), architecture
  verdict for this builder, token-offload finding, copy-patterns,
  traps, could-not-verify list.

## Rules of the register

- Entries are evaluated on accrued evidence, never preference.
- No product was installed or run for the source research; every
  capability is *as documented by its maker* until a device-side
  exercise lands its own record here.
- New systems or changed facts append by amendment PR; history is
  not rewritten.

## Builder follow-on (scoped, not built)

- **Token offload** — snapshot-first observation (compact
  snapshot-with-refs, capped, stale-ref errors) as the fleet
  bridge's primary perception; screenshots on doubt only.
  Evaluation shape: observation mode as an arm under the pilot-1
  context-routing × compression machinery.
- **DoE data population** — this register; the build's design
  decisions cite units/findings here as they land.
