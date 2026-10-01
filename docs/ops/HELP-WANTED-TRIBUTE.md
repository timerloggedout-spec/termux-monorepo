# Help-Wanted · with Tribute (Contributor project)

**Status:** LIVE
**Meaning:** Every upstream PR is a **tribute** to the maintainer’s project — real code review surface, not drive-by noise. Attribution stays with the foreign repo; we keep a ledger of what we offered.

## Contract

| Rule | Behavior |
|------|----------|
| PRIMARY | Upstream PR into **author** repo |
| Tribute body | Credits maintainer + links issue; never `Fixes #` on stake-only |
| Ledger | Built from evidence + live open PR search |
| Dashboard | `/help-wanted/` shows **Tributes** section |
| Closed without merge | Still a tribute attempt — recorded, not spam-retried if issue closed |

## Pipeline (complete)

```text
scout → claim once → contribute (stake or patch) → followup (CHANGES_REQUESTED)
  → llm-assist (live catalog) → status-refresh → dashboard /help-wanted/
```

Workflows: scout · execute · followup · llm-assist · rerequest · status-refresh · dashboard-deploy.

## Ledger source

Machine: `docs/ops/generated/help-wanted-status.json` → `tributes[]`
Human: this doc + live board

Regenerate: `python3 scripts/ci/help_wanted_status.py` (Actions: `help-wanted-status-refresh`).

## Working with others

- One claim marker; skip closed; foreign-only followup.
- Stake PRs are placeholders until a real patch lands.
- Maintainer feedback → rerequest / revise — no zero-81 special modes.

Agent-Identity: Grok (Administrator)
