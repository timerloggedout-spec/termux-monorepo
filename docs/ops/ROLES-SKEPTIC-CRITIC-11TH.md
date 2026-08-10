# Mandatory challenge roles: Skeptic · Critic · 11th Man

## Is “11th Man” the right term?

**Yes, with a definition.** In multi-agent ops we use **11th Man** to mean the **designated outsider / red-team challenger** who is *not* the driver of the proposal — analogous to a bench player who enters specifically to disrupt groupthink. Closest plain synonyms: **devil’s advocate**, **red team**, **opposition researcher**.

We keep **11th Man** as the roster label (short, memorable) and map it explicitly so no one confuses it with “eleventh reviewer in a queue.”

| Role | Duty | When required |
|------|------|----------------|
| **Skeptic** | Attack assumptions, demand falsifiers, question metrics | P1+ claims, matrix score changes, new workflow contracts |
| **Critic** | Attack design/quality of the proposed diff or process | P1+ PRs before merge disposition 🟢 |
| **11th Man** | Outsider challenge — prefer alternate strategy, surface gap findings, vote reject with evidence when group converges too fast | P0 subjects, security, session/auth, merge of ops workflows |

These roles are **participants in Debate + Decision Matrix**, not optional flavor text. Unposted skepticism does not count (`docs/CONSENSUS.md`).

## Ballot hooks

```text
ROLE: skeptic
ROLE: critic
ROLE: 11th-man
VOTE: accept | reject | abstain
```

Log in MANIFEST Review log, DEBATE.md, or PR comment with term id.

## Delphi

Challenge roles feed **Delphi weighting** ([`DELPHI-WEIGHTING.md`](DELPHI-WEIGHTING.md)): skeptic/critic/11th-man votes can carry distinct weights once roster config lands. Delphi is a **critical component** of matrix evolution — not a stub to ignore.

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-roles-11th
