# CodeRabbit (and peer) excerpts → Operator & Jules

**Issues:** #146 (signal alignment) · auto-jules workflow · continuous-ops

## Problem

Piped “feedback” sometimes includes **analysis-chain / probe scripts** (`🏁 Script executed`, shell dumps). Those are **not** review disposition. Acting on them wastes Jules quota and confuses Operator sessions.

## Policy

| Source | Pipe to Jules/Operator as |
|--------|---------------------------|
| Unresolved **review threads** | Primary actionable list |
| Review **state** (CHANGES_REQUESTED / COMMENTED) | Disposition signal |
| High-level summary with concrete findings | Secondary excerpt (≤1200 chars) |
| Analysis-chain / probe / `Script executed` | Tag as **probe**; do not treat as tasks |
| Autofix commits already on branch | Note “may already be applied” |

## Excerpt builder rules (workflows)

1. Detect probe: `/🏁\s*Script executed:|Analysis chain|```shell/i`
2. If probe: prefix note — *act only on disposition / open threads*
3. Prefer thread titles + file paths over full bot essay
4. Always include `context_key` and continue-only language
5. Debounce `<!-- agent-auto-jules -->` (existing window)

## Operator read path

When summarizing for humans/OPERATOR sessions: lead with **disposition matrix**, then open threads, then optional probe appendix collapsed.

## Related

- #146 · PR #149 · `agent-review-auto-jules.yml` on #148

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-cr-excerpt-policy
