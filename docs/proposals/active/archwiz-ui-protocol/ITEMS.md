# Work Items — archwiz-ui-protocol

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| AWUI-001 | P1 | proposed | Define the canonical boundary between ArchW1z TUI/mobile UI and the underlying agentic protocols. | Architecture doc names protocol ownership and explicitly prevents a duplicate orchestration contract in the UI. |
| AWUI-002 | P1 | proposed | Specify a minimal UI/client contract for observe, inspect, dispatch, approve/escalate, and authorized stop operations. | Contract is transport-agnostic and maps each operation to capability/authority requirements. |
| AWUI-003 | P1 | proposed | Define a versioned agent handoff envelope with task lineage, source/destination, context/ref/SHA, authority, constraints, evidence, outputs, completion, and escalation. | Schema is deterministic, validated, and suitable for GitHub, Termux, and remote workers. |
| AWUI-004 | P2 | proposed | Define HITL, supervised-autonomous, and autonomous modes over the same protocol. | Mode changes are explicit state transitions; UI does not invent separate execution semantics. |
| AWUI-005 | P2 | proposed | Define event/evidence consumption for a future mobile UI without making dashboards authoritative. | UI can observe current state and evidence while canonical state remains in protocol/GitHub sources. |
