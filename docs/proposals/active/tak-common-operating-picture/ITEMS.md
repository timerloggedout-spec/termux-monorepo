# ITEMS — T.A.K. Common Operating Picture

| ID | Work | Priority | Owner | Status | Evidence / acceptance criteria |
|---|---|---:|---|---|---|
| TAK-01 | Define the versioned T.A.K. common-operating-picture envelope and evidence contract for public organizational procurement/registration signals; preserve source dataset versions, conflicts, timestamps, coverage, append-only events, unvalenced emergence, and SWOT duality composition. | P1 | ChatGPT | executing | PR #5025 adds `docs/ops/TAK-COMMON-OPERATING-PICTURE.md` and `docs/ops/TAK-PICTURE.schema.json`. Acceptance: schema semantics validate; doctrine and privacy boundaries align with LENS-FRAME; upstream #4496 interface is reconciled; no duplicate crawler/store; proposal review recorded; proposal-lifecycle + repo-gate + termux-smoke pass on the current SHA. |

## Deferred work — not admitted by TAK-01

- Source adapter / projection implementation: requires the concrete, versioned output contract from #4496 and a separately itemized/accepted proposal revision.
- Actor-network detection rules: requires labeled fixtures, provenance, rule versioning, and false-positive review before quality claims.
- Dashboard bindings: require explicit records from the dispatch-tree, tracking, telemetry, and Web Design owners.
- Any procurement, risk, security, recruiting, or other adverse action: outside T.A.K. awareness scope and requires separate human-authorized governance.
