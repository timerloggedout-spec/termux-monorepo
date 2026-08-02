# PR Summary Rewrite Process

Keep PR titles/bodies honest, scannable, and multi-agent — **not** a single-agent monologue.

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

**Consensus for body rewrite on P0 security PRs (#3):**

1. summary-editor drafts rewrite  
2. ≥1 **other** reviewer (Devin or human Operator) acknowledges in a comment, **or** Operator posts “summary OK”  
3. Then apply body update  

For P1–P3: a single summary-editor may rewrite if they cite disposition comment + this process.

**Anti-monopoly:** If the same agent rewrote **three consecutive** PR bodies, the next rewrite should be done by a different roster agent or Operator. Record in the PR comment: `Summary-Editor: <id>`.

## Procedure

1. Read PR title, body, files, review threads, prior disposition comments.
2. Classify Status (🟢/🟡/🔴/⚪).
3. Draft body using skeleton; preserve Author’s technical facts; add Status/Non-goals/Follow-ups.
4. Comment: `Summary-Editor: <id> — rewrite per docs/PR-SUMMARY-PROCESS.md` + one-line rationale.
5. `update_pull_request` title/body.
6. Optional: retarget base to `master-staging` only when that is already agreed disposition (not silently).

## Registry of summary passes

Maintain a short log in `docs/PR-SUMMARY-LOG.md` (append-only):

```text
| date | PR | editor | status set | notes |
```

## Relation to proposals

PR summary rewrite is **not** a proposal. Linking `Implements: <ITEM-ID>` is required when the PR executes proposal work. Disposition may reference Critical-Eval items (CE-*).
