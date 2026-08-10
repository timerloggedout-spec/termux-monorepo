# OPERATOR Signing Requirement

**Source policy:** [PR #126 comment 5243623808](https://github.com/timerloggedout-spec/termux-monorepo/pull/126#issuecomment-5243623808) and subsequent OPERATOR directives.

## Requirement

All OPERATOR agents (Grok across sessions, other provider sessions granted OPERATOR role) **must** sign material modifications with their **session id** and **message id** (or equivalent PR/issue comment id).

### Signature format

```text
Signed-off-by: <AgentName> (OPERATOR) <session-id> / <message-or-comment-id>
```

Examples:

```text
Signed-off-by: Grok (OPERATOR) session-2026-08-10 / comment-5243638115
Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-matrix-init
```

### What must be signed

- Edits to `docs/ops/DECISION-MATRIX.md`
- Workflow changes that affect Jules session management, continuous-ops, auto-jules, or disposition piping
- Policy docs under `docs/ops/`
- Any PR body or issue comment that alters priority, disposition rules, or context_key contract

### Why

Multiple concurrent OPERATOR sessions (different provider contexts) share write access. Signatures make provenance recoverable without relying on git author alone, and satisfy the audit trail requested in the source comment.

### Non-OPERATOR agents

Jules, CodeRabbit, Devin, Tembo, etc. continue to use their normal commit / bot attribution. This rule applies only to agents acting under the OPERATOR role.

## Related

- `docs/ops/DECISION-MATRIX.md`
- AGENTS.md hard rules
- `#145` / `#146`

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-signing-init
