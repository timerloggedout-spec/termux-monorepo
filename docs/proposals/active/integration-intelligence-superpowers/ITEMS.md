# Work Items — integration-intelligence-superpowers

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| IIS-001 | P1 | executing | Establish the Integration Intelligence architecture and canonical registry; publish a repository-native Superpowers skill and onboarding pointers; define the event and adapter contracts; record provider capability and trust boundaries; publish phased implementation plan. | Skill frontmatter and procedure are valid; skill is discoverable from `SKILLS.md`, `docs/ops/SKILLS-INVENTORY.md`, and `CLAUDE.md`; registry JSON parses and validates against its schema; capability claims distinguish connected tools, installed skills, not-exposed tools, and unimplemented adapters; docs preserve existing proposal, WAIT, dual-gate, and permissions policy. |

## Disposition

IIS-001 is executing on `feat/integration-intelligence-superpowers`. The initial delivery is the governed foundation; provider-specific runtime adapters and live telemetry remain subsequent, separately validated work items.
