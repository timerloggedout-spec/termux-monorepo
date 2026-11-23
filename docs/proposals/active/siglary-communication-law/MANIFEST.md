# Proposal Manifest — siglary-communication-law

| Field | Value |
|---|---|
| Proposal ID | `siglary-communication-law` |
| Status | `executing` |
| Owner | `timerloggedout-spec` |
| Implementer | `ChatGPT` |
| Scope | DO-first CAVEMAN-6 and Siglary enforcement across repository-authored communications, source/projection parity, lint, CI, and bounded discussion auditing |
| Base | `master-staging` |
| Linear | [TER-981](https://linear.app/termux-monorepo-linear/issue/TER-981/siglary-001-enforce-caveman-6-do-statement-style-across-repository) |
| Foundation | [PR #5339](https://github.com/timerloggedout-spec/termux-monorepo/pull/5339) |

## Authority

- `CLAUDE.hum.md` is the canonical human source for primary collaborator guidance.
- `CLAUDE.md` is the generated Linguist projection; regenerate from its source.
- `AGENTS.hum.md` is the canonical human source for secondary agent guidance.
- `AGENTS.md` is its generated Linguist projection.
- `docs/ops/COMMUNICATION-LAW.md` is the canonical style guide.
- `docs/ops/SIGLARY-OPERATOR-REGISTRY.md` is the stable operator reference.

## Safety and scope

Apply strict lint to repository-authored prose and advisory analysis to imported/external text. Preserve exact identifiers, API/schema literals, quoted upstream text, legal/security requirements, and code/test strings where rewriting would alter meaning. Keep credentials and private mapper material outside repository documents and generated artifacts.

## Execution

Use item-scoped implementation, focused tests, repository gate, and Termux smoke. Record evidence in this proposal and TER-981. Keep generated projections synchronized with their human sources.
