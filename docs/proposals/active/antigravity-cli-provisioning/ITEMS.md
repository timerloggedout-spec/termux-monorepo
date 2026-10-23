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

The operational lane exists, but full provisioning is not done. The later AGY-1497-09/10 receipt supersedes the original Low setting: High is restored with auto-approve unchanged, and secondary SSH recovery is deployed with a supervised-child restart verified. Skill/UI enumeration, native verifier execution, nested delegation, live stream filtering and full-repository readiness remain unverified. Boot activation/reboot remain unverified; no agent scheduler, plugin or MCP deployment is claimed. See [the complete plan and modified considerations](OPERATIONAL.md) and [current recovery receipt](SECONDARY-RECOVERY.md).

## Approved filtering continuation

| ID | Work | Owner | Status | Acceptance |
|---|---|---|---|---|
| AGY-1497-09 | Passive full-diagnostics + three-line steering filter, explicit controller runner; restore High on pinned secondary only | Cue | in progress; High restored, controller runner fixture-verified; live stream unverified | Strict pinned identity and exact candidate re-read verified High-only change; auto-approve preserved; private full stdout/stderr and separate producer exit; official docs + offline fixtures only; no model calls or native telemetry claim |

Operator explicitly approved correcting the low/High mismatch and selected programmatic filtering. Registration: https://github.com/timerloggedout-spec/termux-monorepo/issues/1497#issuecomment-6336367544 . Live PR #1514 head is `cue/1497-operational-device2`, not the original provisioning branch. [Filtering contract and current deployment boundary](FILTERING.md).

## Controller telemetry and archive follow-up

| ID | Work | Owner | Status | Acceptance |
|---|---|---|---|---|
| Local follow-up (not separately registered) | Incremental schema-v1 event telemetry, encrypted archive/JIT comparison, and reviewed Hindsight outbox | Cue | in progress; code and synthetic fixtures on PR branch only | Immediate allowlisted event emission; final usage remains authoritative; fake-age round trip; Hindsight disabled by default/no live sends; no Device 2 or Origin changes |

This is a repository implementation follow-up to AGY-1497-09, not a claim of continuous telemetry deployment. The explicit status map, activation gates, and sources are in [TELEMETRY-PIPELINE.md](TELEMETRY-PIPELINE.md). Keep the issue open and PR unmerged until the owner reviews the resulting branch and decides whether to activate any external service.

## Approved secondary recovery continuation

| ID | Work | Owner | Status | Acceptance |
|---|---|---|---|---|
| AGY-1497-10 | Secondary-only Boot + WakeLock, runit SSH recovery, non-killing reconnect alias | Cue | in progress; deployed, Boot activation/reboot unverified | Pinned key/local identity verified; native recovery wrapper/logger running, manual listener untouched; 13 fixture tests; reconnect/alias verified; Boot installed but first launch unknown; no Tailscale edits, Origin access, model prompts or merge |

Operator explicitly requested crash recovery and a quick reconnect command after manually running `termux-wake-lock` and `sshd`. Registration: https://github.com/timerloggedout-spec/termux-monorepo/issues/1497#issuecomment-6339476940 . Work remains on PR #1514's actual branch using the existing section 8 GitHub fallback. All unrelated checkout changes preserved. Freshly observed Low was corrected under already-approved AGY-1497-09; High and unchanged auto-approve were reverified. [Runtime evidence, limitations and rollback](SECONDARY-RECOVERY.md).

### Existing resilience priority: controller-only access continuation

AGY-1497-10 also covers the bounded [controller access preflight and recovery decision path](ACCESS-PREFLIGHT.md): distinguish Tailscale observation, fresh pinned SSH/listener/authentication and read-only GitHub/Git connectivity. Only fixed connection-establishment handshakes may retry; no AGY task or non-idempotent command is accepted or replayed. Device services/configuration, Tailscale, credentials and AGY settings are unchanged. Live pinned SSH and public Git passed; `gh` was unavailable on the noninteractive PATH, so overall readiness remains false. Work and test scratch stay in RAM while the original filesystem is full; no unrelated data is removed. This is a continuation of the existing priority, not a new priority, completion claim or merge authorization.
