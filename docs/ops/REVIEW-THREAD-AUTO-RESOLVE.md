# Review-thread auto-resolve (design)

> **Status:** DESIGN (2026-08-06)  
> **Implements candidate:** CE-24  
> **Agent:** Grok

## Problem

Branch protection often requires **resolved conversations** before merge. Agents can:

- push fix commits
- reply on threads

…yet **Resolve** stays a manual GitHub UI action. CodeRabbit and similar bots also impose **cooldowns** (~1 hour), so a naive “resolve immediately after reply” races the next bot pass.

## Preferred design

```text
on: pull_request_review_comment, push (PR head), schedule (cooldown recheck)
  → match thread_id to fix commit / agent reply
  → wait / re-queue until bot cooldown windows clear
  → GraphQL: resolveReviewThread(threadId) when criteria met
  → else: comment “Operator: 1-click resolve checklist”
```

### Criteria (example)

- Agent or Operator reply contains `Fixed in <sha>` or `Addressed`
- Head SHA is descendant of the fix commit
- Optional: CodeRabbit indicator “Addressed in commit …”
- Cooldown: last bot review finished + `N` minutes (configurable)

### Permissions

- GitHub App or PAT with `pull_requests: write`
- Prefer App so actor ≠ Operator username

### curl_cffi / page actions

Reserve browser automation for gaps where the API cannot resolve threads or click UI-only controls. Default path is **GitHub GraphQL + Actions wait/schedule**, not browser.

### Relation to human-in-the-loop

Operator remains authority for **security**, **credential**, and **proposal-bypass** decisions. Thread resolve after an agreed fix is **delegable** to automation once CE-24 lands.

Signed-off-by: Grok <grok@x.ai>
