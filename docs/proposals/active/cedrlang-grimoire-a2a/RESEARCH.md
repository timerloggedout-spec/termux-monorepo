# Research, Review, and Decision Requests — CEDRlang / Grimoire / A2A

**Status:** Open for non-author review. This record does not approve integration, mapper custody, transport, or an agent-contact migration.

## Questions Requiring an Explicit Decision

| ID | Decision question | Required evidence | Decision owner | Current state |
|---|---|---|---|---|
| R-01 | Which approved custody service may hold a production private mapper, and who may access it? | Threat model, access matrix, rotation/revocation procedure, audit/event retention policy, incident response, and no-repository-secret proof. | Operator + security reviewer | Open |
| R-02 | What is the canonical human source for each agent contact point, and may a generated machine projection exist? | Source/target inventory, generator determinism, freshness check, rollback, readability/safety visibility audit, and owner assignment. | Operator + documentation owner | Open |
| R-03 | Which A2A transport and authentication model is acceptable after the local envelope foundation? | Authn/authz model, replay/fuzz tests, bounded idempotency-store ownership, failure semantics, key custody, privacy assessment, and transport threat model. | Operator + security reviewer | Open |
| R-04 | What operational meaning, if any, should the 70% coverage target have? | Representative approved CIR corpus, declared eligibility policy, independent measurement, quality/error analysis, and lower-bound failure behavior. | Linguist reviewer + operator | Open |
| R-05 | How are inherited repository-gate and proposal-registry blockers resolved or formally exempted? | Fix PR or explicit operator disposition, rerun evidence, and updated status board. | Repository maintainer | Open |

## Required Independent Review

A non-author reviewer must evaluate the following before the proposal status can move from `draft` to `accepted`:

1. The clean successor still has no CID, CEDARscript, subprocess, network, mapper-content, or external-service path in `protocol.py`.
2. The lossless claim is constrained to canonical-record reconstruction with the authorized mapper; no public-obfuscation security claim is made.
3. The test suite covers mapper collisions, literal symbol preservation, integrity tampering, coverage threshold failure, TTL expiry, state transitions, and replay conflict.
4. The publication links and relationship diagrams distinguish verified evidence from candidate history and disclose the partial historical index window.
5. Any follow-on agent-contact migration has a separately accepted work item.

## Vote Record

| Reviewer | Role | Vote | Date | Evidence / rationale |
|---|---|---|---|---|
| Manus AI | author-executor | changes requested | 2026-08-20 | Foundation is implemented and published, but private custody, contact-point source policy, A2A transport, baseline blockers, and independent review remain open. |
| _Unassigned_ | non-author technical reviewer | pending | — | Required before acceptance. |
| timerloggedout-spec | operator-authorizer | pending | — | Required before merge/integration claim. |

## Publication Links

- [GitHub follow-up and subtask tracker #274](https://github.com/timerloggedout-spec/termux-monorepo/issues/274)
- [Agent2Agent proposal #117](https://github.com/timerloggedout-spec/termux-monorepo/issues/117)
- [Operator priority/gate record #175](https://github.com/timerloggedout-spec/termux-monorepo/issues/175)
- [Review packet](../../../reviews/linguist-177/LINGUIST-REVIEW-PACKET.md)
- [CEDRlang contract](../../../CEDRLANG-GRIMOIRE-A2A.md)
- [Context-relationship graph reuse guide](../../../reviews/linguist-177/context-relationship-graph-reuse.md)
