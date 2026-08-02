# PR Summary Rewrite Process

Keep PR titles/bodies honest, scannable, and multi-agent — **not** a single-agent monologue.

**Consensus / votes:** [`docs/CONSENSUS.md`](CONSENSUS.md) (Raft-inspired terms, quorums, triage bots).

## When to rewrite

Rewrite (or request rewrite) when **any** apply:

| Trigger | Examples |
|---------|----------|
| Status drift | Body says mergeable; disposition is NO-GO / A≠A+B+C |
| Missing disposition | Open PR with no Status / ArchW1z line |
| Wrong base | Targets `master` but work belongs on `master-staging` |
| Generator noise | ECC/bot blobs, truncated text, false conventions |
| Scope lie | CodeRabbit “new features” summary contradicts “scaffold only” |
| Security incomplete | Tip hygiene sold as full remediation |
| One-liner | e.g. PR #2 body too thin for reviewers |

**Do not** rewrite solely for style if Status, scope, tests, and links are already accurate.

## Standard body skeleton

```markdown
## Summary
One paragraph intent.

**Status:** 🟢 merge-ready | 🟡 conditional | 🔴 NO-GO | ⚪ draft / blocked
**Disposition:** one line (who + why)
**Base:** `master-staging` (preferred) | `master`
**Implements:** CE-xx / TER-n (if any)

### Changes
- …

### Non-goals
- …

### Validation
- commands / Termux notes

### Follow-ups
- …

### Agent notes
- Author / Reviewer / Summary-Editor roles (see below)
```

Titles: conventional (`fix:`, `feat:`, `security:`) + short constraint if needed
`(needs regen before merge)`, `(A only — not history rewrite)`.

## Roles (selective access)

| Role id | Who may act | May rewrite PR body? | May set disposition? |
|---------|-------------|----------------------|----------------------|
| **author** | PR opener (human or bot) | Own PR anytime | Suggest only |
| **summary-editor** | Named agents below | Yes, after reading diff + comments | Suggest; must not erase Author intent |
| **reviewer** | Devin, CodeRabbit, Grok, ChatGPT, human | No (comment only) unless also summary-editor | Yes, via comment + optional REQUEST_CHANGES |
| **executor** | Implementers | Only if also summary-editor | No for P0 security alone |
| **operator** | Repo owner | Yes | Final on credentials / force-push |

### Named summary-editors (roster)

| Agent | id | Scope |
|-------|-----|--------|
| Grok ArchW1z | `grok-archw1z` | All open PRs; process docs |
| Devin | `devin` | PRs it authored or reviewed; fix its own scaffolds |
| ChatGPT | `chatgpt` | Proposals + PR bodies when connector allows write |
| Claude / Codex | `claude` / `codex` | ECC/skill PRs; must not override root `AGENTS.md` |
| CodeRabbit | `coderabbit` | **Comment only** — never sole body rewriter |
| ECC bot | `ecc-tools` | Own generated PRs only; human/summary-editor may correct |

### P0 security body rewrite

See **CONSENSUS.md** §2–§3. Short form:

1. Driver posts proposed body under `term=pr-N/summary/k`
2. ≥1 other Reviewer/Operator: `VOTE: summary OK`
3. Then `update_pull_request`

### Anti-monopoly (distinct PRs only)

**Three consecutive = three different PR numbers**, not three edits to one PR.

| Allowed | Not the intent of the limit |
|---------|-----------------------------|
| Iterate #12 body as often as needed until accurate | Blocking refinement on the same PR |
| Same agent: #3 → #2 → #6 then hand off | One agent owning the entire open queue forever |

Count distinct PR numbers in `docs/PR-SUMMARY-LOG.md` order. Same-PR rows do not increment the counter. After three distinct PR rewrites by one editor, the next **new** PR number should use a different roster agent or Operator.

Record: `Summary-Editor: <id>` on the PR comment.

## Procedure

1. Read PR title, body, files, review threads, prior disposition comments.
2. Classify Status (🟢/🟡/🔴/⚪).
3. Draft body using skeleton; preserve Author’s technical facts; add Status/Non-goals/Follow-ups.
4. Comment: `Summary-Editor: <id> — rewrite per docs/PR-SUMMARY-PROCESS.md` + one-line rationale.
5. For P0: wait for `VOTE: summary OK` if required by CONSENSUS.md.
6. `update_pull_request` title/body.
7. Append `PR-SUMMARY-LOG.md`.
8. Retarget base only when disposition already agrees (not silently).

## Registry of summary passes

`docs/PR-SUMMARY-LOG.md` (append-only).

## Relation to proposals

PR summary rewrite is **not** a proposal. Link `Implements: <ITEM-ID>` when executing proposal work.
