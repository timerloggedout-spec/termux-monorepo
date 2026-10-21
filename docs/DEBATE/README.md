# DEBATE dock

**Why this exists:** Keep multi-agent argument, votes, and open questions **out of the critical path** of code work. Agents that only need to implement an `ITEMS.md` row should not load large eval dumps.

**Agents:** load **only** [`TOC.md`](TOC.md) unless the task explicitly says `debate:<id>` or you are the driver on that term.

**Binding truth still lives in** `docs/proposals/active/<id>/MANIFEST.md` Review log + `docs/CONSENSUS.md` tiers.
DEBATE is the **working surface**; MANIFEST is the **ledger**.

## Layout (intentionally shallow)

```text
docs/DEBATE/
  README.md          # this file — policy
  TOC.md             # ALWAYS-SMALL index (LLM entry)
  MATRIX.yaml        # tags: status, stale, blocker, bias, agents
  _template/TOPIC.md # copy for new topics
  active/<id>/       # one folder per open debate
  resolved/<id>/     # closed debates (archive)
```

**Do not** nest `Provider/Model/Agent/Role` as directories. Those are **tags** in `MATRIX.yaml`.

## Isolation rules

1. Default context budget: `TOC.md` + `MATRIX.yaml` only.
2. Open `active/<id>/*` only when the task cites `debate:<id>`, you are recording a vote, or OPERATOR asked for synthesis.
3. Never copy full proposal bodies into DEBATE — link the pointer.
4. Votes use CONSENSUS format (`VOTE: accept|reject|abstain` + `term:`).
5. Stale / blocker flags live in MATRIX; GHA + Linear may surface them.

Extracted 2026-09-23 from PR #69 onto live `master` (base was `feature/proposal-vote-promote`, dirty).
HOLD is not a workflow state. This extract is the corrective action.
