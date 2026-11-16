<!-- live-4 framing-ba: DO patterns B>>A (framework sections 4B then 4A).
     Fill EVERY field. Phase B output MUST land (PR section or issue comment)
     before implementation evidence. Stamp comment below is mandatory. -->
<!-- campaign: live-4-dispatch-framing | framing: framing-ba | block: <D2|D4|M2|M3> | slot: <k> | size: <S|M|L> -->

## Phase B — Research and find gaps (first)

**Research** <question/system> using <primary sources or specified evidence>.
**Compare** observed state against <contract/baseline>.
**Identify** confirmed facts, assumptions, contradictions, and missing evidence — separately.
**Rank** gaps by impact, likelihood, and dependency.
Post the recon as a PR section or issue comment BEFORE implementing.
Do not claim implementation from research alone.

## Phase A — Implement or repair (after Phase B lands)

**Implement** <specific behavior, as scoped by the Phase B recon> in <bounded scope: named paths / issue scope>.

- **Target:** <system, files, behavior>
- **Outcome:** <what is true afterward, observable>
- **Scope:** <where work may occur; nothing outside>
- **Constraints:** preserve <invariants>; do not <named prohibitions>
- **Acceptance evidence:** add/update tests for <expected behavior + failure cases>; run <available checks>; report exact evidence, changed paths, remaining risks, anything not verified
- **Stop / escalation:** stop + explain if the change crosses the stated scope or an approval boundary
