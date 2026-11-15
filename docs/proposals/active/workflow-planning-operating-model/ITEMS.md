# ITEMS — workflow-planning-operating-model

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| WPO-001 | P1 | in_review | Establish the canonical Workflow Contract (WFC), dimensional model, state separation and source-of-truth boundaries. | Versioned schema; documented ownership; no duplicate scheduler/evidence authority; compatibility map to QUE, Actions, Temporal, Termux, n8n and Platform201. |
| WPO-002 | P1 | in_review | Add deterministic WFC structural validation and dependency-graph integrity checks. | Standard-library validator; rejects malformed identifiers, duplicate IDs, unresolved dependencies, cycles and invalid resource/side-effect declarations; regression tests pass. |
| WPO-003 | P1 | in_review | Define PDDL/HTN/CP-SAT/BPMN/state-machine selection and QUE dispatch planning projection. | PDDL candidate checked by a named planner; plan receipt and domain/problem digests retained; external verification and approval cannot be planner-invented. |
| WPO-004 | P1 | in_review | Define QUE × routing × DoE/MVT bounded optimization pilot. | Frozen baseline, pinned factors, blocked/paired assignment where appropriate, predeclared response variables/stopping rules, uncertainty and Pareto reporting, independent outcome verification. |
| WPO-005 | P1 | in_review | Define Mermaid, n8n, Platform201 and Admin/Desk projection boundaries. | Diagrams map to WFC IDs; n8n remains optional and sanitized; Platform201 owner gates remain intact; no Admin/Desk projection becomes canonical state. |
| WPO-006 | P1 | todo | Build read-only WFC-to-Mermaid compiler and drift checks against selected existing workflow artifacts. | Deterministic output; stable node IDs; generated diagram diff; no execution side effects; source SHA and WFC version attached. |
| WPO-007 | P1 | todo | Implement QUE admission-envelope adapter in shadow mode. | WFC-to-QUE mapping; no dispatch authority; records candidate admission/exclusion and reasons; comparison against live QUE decisions. |
| WPO-008 | P1 | todo | Run bounded routing DoE pilot and publish verified optimization results. | repo-gate + termux-smoke pass on same SHA; held-out or paired cohort; verified outcome; costs/time/rework measured; uncertainty and limitations reported; promotion approved. |

## Disposition

This proposal remains `in_review`. Items WPO-001–WPO-005 describe the initial design/schema slice in PR #5388; WPO-006–WPO-008 remain future execution items. Do not mark the proposal accepted or promote routing policy from simulated results alone.
