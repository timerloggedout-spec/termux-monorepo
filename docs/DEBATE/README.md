# DEBATE dock

**Why this exists:** Keep multi-agent argument, votes, and open questions **out of the critical path** of code work. LLMs that only need to implement an `ITEMS.md` row should not load 24KB eval dumps or sprawling chat.

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
    TOPIC.md         # problem statement + links
    THREAD.md        # append-only argument (optional if short)
    VOTES.md         # structured VOTE blocks only
  resolved/<id>/     # closed debates (archive)
```

**Do not** nest `Provider/Model/Agent/Role` as directories. Those are **tags** in `MATRIX.yaml` and front-matter. Path explosion kills focus.

## Isolation rules (for agents)

1. Default context budget: `TOC.md` + `MATRIX.yaml` only.
2. Open `active/<id>/*` only when:
   - task cites `debate:<id>`, or
   - you are recording a vote / driving a term, or
   - OPERATOR asked for synthesis.
3. Never copy full proposal bodies into DEBATE — link the pointer or branch.
4. Votes: same format as CONSENSUS (`VOTE: accept|reject|abstain` + `term:`).
5. Stale / blocker flags are set in MATRIX; GHA + Linear surface them.

## Related

- Proposals: `docs/proposals/`
- Consensus tiers: `docs/CONSENSUS.md`
- Linear project: termux-monorepo hardening (team `Termux-monorepo_linear` / TER)
- Secrets already wired: `LINEAR_API_KEY`, `JULES_API_KEY`, Gemini workflows
