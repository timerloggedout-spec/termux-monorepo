# Agent Status Board

**Implements:** #124 — *How do we know if Jules is executing right now?*

Better than inferring from "I'm on it" prose: **structured markers** + a **refresh workflow** that posts a live table on issue **#124**.

## Status enum (machine)

| Status | Meaning | Typical signal |
|--------|---------|----------------|
| `WAITING` | Operator/GHA pinged agent; no ack or commit yet | `@jules` / auto-jules marker < TTL, no agent reply |
| `WORKING` | Agent acknowledged or session active | `<!-- agent-status: WORKING -->` or Jules/Gitar "working" / recent agent commit |
| `DONE` | Task complete for this context_key cycle | `DONE` marker or non-empty push + threads resolved |
| `BLOCKED` | Cannot proceed without external fix | `BLOCKED` marker, quota, dirty with no path |
| `IDLE` | No open ask for this PR | Clean enough; no recent ping |
| `DIRTY` | mergeable_state dirty — rebase required | GitHub mergeable_state |

## Required comment markers

Agents (Jules, OPERATOR, continuous-ops, auto-jules) **must** emit one of:

```text
<!-- agent-status: WAITING context_key=pr-N-ref agent=jules task="…" -->
<!-- agent-status: WORKING context_key=pr-N-ref agent=jules task="…" -->
<!-- agent-status: DONE context_key=pr-N-ref agent=jules task="…" -->
<!-- agent-status: BLOCKED context_key=pr-N-ref agent=jules reason="…" -->
<!-- agent-status: IDLE context_key=pr-N-ref -->
```

Optional human line under the marker (not parsed):

```text
STATUS: WORKING · context_key=pr-148-… · rebase onto master-staging
```

### Heuristic fallbacks (when marker missing)

| Pattern | Inferred status |
|---------|-----------------|
| `<!-- agent-auto-jules -->` or `<!-- continuous-agent-ops -->` in last 90m, no agent reply | `WAITING` |
| Body matches `/I'm on it\|working on this\|Gitar is working\|in progress/i` from agent login | `WORKING` |
| `google-labs-jules` / `devin` / `gitar-bot` comment in last 45m | `WORKING` |
| Agent push (non-empty) in last 60m after a ping | `WORKING` → toward `DONE` |
| `mergeable_state == dirty` | annotate `DIRTY` (orthogonal; can combine) |
| No ping > 6h and clean | `IDLE` |

## Live board

- **Tracking issue:** [#124](https://github.com/timerloggedout-spec/termux-monorepo/issues/124)
- **Workflow:** `.github/workflows/agent-status-board.yml`
  - `schedule` every ~30m + `workflow_dispatch` + `issue_comment` (marker present)
  - Scans open non-draft PRs (cap 20)
  - Posts/updates a single sticky comment marked `<!-- agent-status-board -->`
- **context_key** column ties to Jules session binding (#145 / #148)

## Cross-PR awareness

Board rows include `aware_of` hints when titles/bodies reference other open PR numbers (answers #124 cross-awareness ask). Full dependency graph remains future (MCP Agent Mail / #143).

## Anti-patterns

- Do **not** treat analysis-chain probe dumps as WORKING evidence
- Do **not** mark DONE on empty commits (see empty-commit gate on #148)
- Continuous-ops must not invent new epics from board rows (#150 discipline)

## Related

`DECISION-MATRIX.md` · `jules-session-management.md` · `ROLE-PROMPT-PIPELINE.md` · #124 · #145 · #148

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-status-board
