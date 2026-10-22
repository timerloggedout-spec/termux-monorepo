# Antigravity CLI work items — #1497

| ID | Work | Owner | Status | Acceptance |
|---|---|---|---|---|
| AGY-1497-01 | Preserve seed research with provenance and verify key claims | Cue | done | Original seed retained; source-backed corrections separate from reported observations |
| AGY-1497-02 | Collaborative use cases and initial provisioning proposal | Cue | done | Bounded roles, handoff, stages, rollback, high verbosity and auto-approve preserved |
| AGY-1497-03 | Offline readiness inventory, tests, and dual-gate evidence | Cue | done | No prompts/config writes; missing prerequisites explicit; tests and gate outcomes recorded |

Issue: https://github.com/timerloggedout-spec/termux-monorepo/issues/1497
Linear: unavailable (connector requires login); GitHub fallback per docs/LINEAR-AGENT-PROTOCOL.md §8. Do not fabricate TER IDs or merge.

Original repository delivery evidence: [VALIDATION.md](VALIDATION.md). Those three done items refer only to #1498's original repository deliverables. The later secondary pilot and unresolved runtime gaps are recorded below and in [OPERATIONAL-VALIDATION.md](OPERATIONAL-VALIDATION.md). Proposal remains open for review and follow-up.

## Device-specific operational continuation

| ID | Work | Owner | Status | Acceptance |
|---|---|---|---|---|
| AGY-1497-07 | Native agent definitions, dedicated thin pilot, secondary discovery and bounded execution | Cue | in progress | Pinned identity and one pilot PASS; source/settings hashes unchanged; native enumeration inconclusive; verifier/nested dispatch still untested |
| AGY-1497-08 | Review reconciliation, independent validation, complete plan/status and rollback | Cue | in progress | Focused tests and both gates; explicit runtime limits; pushed commits; no merge |

Operator's operational request supersedes the earlier Device 2 exclusion only for the identity-verified secondary. Origin stays excluded. Registration: https://github.com/timerloggedout-spec/termux-monorepo/issues/1497#issuecomment-6336022930 . Linear remains unavailable; use section 8 GitHub fallback; no invented TER ID.

The operational lane exists, but full provisioning is not done: saved verbosity is low rather than requested High; skill/UI enumeration, native verifier execution, nested delegation and full-repository readiness remain unverified. No hook, plugin, MCP, recurring task or telemetry deployment is claimed. See [the complete plan and modified considerations](OPERATIONAL.md).

## Approved filtering continuation

| ID | Work | Owner | Status | Acceptance |
|---|---|---|---|---|
| AGY-1497-09 | Passive full-diagnostics + three-line steering filter; restore High on pinned secondary only | Cue | in progress; device offline | Offline parser/capture/settings tests and gates; only verbosity changes; auto-approve preserved; raw stream retained; no model calls; device identity and deployment verified before completion |

Operator explicitly approved correcting the low/High mismatch and selected programmatic filtering. Registration: https://github.com/timerloggedout-spec/termux-monorepo/issues/1497#issuecomment-6336367544 . Live PR #1514 head is `cue/1497-operational-device2`, not the original provisioning branch. [Filtering contract and current deployment boundary](FILTERING.md).
