# PR Summary Rewrite Process

Keep PR titles/bodies honest, scannable, and multi-agent — **not** a single-agent monologue.

**Consensus / votes:** [`docs/CONSENSUS.md`](CONSENSUS.md).

## When to rewrite

Rewrite when Status drifts, disposition missing, wrong base, generator noise, scope lies, security incomplete, or body is a one-liner.

**Do not** rewrite solely for style if Status, scope, tests, and links are accurate.

## Standard body skeleton

```markdown
## Summary
One paragraph intent.

**Status:** 🟢 merge-ready | 🟡 conditional | 🔴 NO-GO | ⚪ draft / blocked
**Disposition:** one line (who + why)
**Base:** `master-staging` (preferred) | `master`
**Implements:** CE-xx / TER-n (if any)

### Changes
### Non-goals
### Validation
### Follow-ups
### Agent notes
```

## Roles

| Role | May rewrite body? |
|------|-------------------|
| author | Own PR |
| summary-editor (grok-archw1z, devin, chatgpt, claude/codex) | Yes |
| reviewer / coderabbit | Comment only |
| operator | Always |

**Anti-monopoly:** three consecutive = three **distinct PR numbers**. Same-PR iteration always OK.

See full roster and P0 rules in git history / master-staging copy if truncated.
