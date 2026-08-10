# Mandatory / must-include phrase seeds (public)

**Track:** [#96 research(prompt): extract Cheat_Code seeds + must-include phrases](https://github.com/timerloggedout-spec/termux-monorepo/issues/96)

Public demo policy: **viewable text OK**. Redact anything operator-private before promoting to this file.

## Core contract phrases (inject early)

| Phrase / rule | Why |
|---------------|-----|
| `Target master-staging` | Integration branch |
| `repo_gate.py` + `termux_smoke.py` must pass | Dual gate |
| `No Class 3/4 artifacts in git` | Security |
| `Implements: <ITEM-ID>` | Traceability |
| `Unposted chat is not consensus` | CONSENSUS.md |
| `Prefer minimal diffs` | Quality |
| `Preserve Sentinel 0o600/0o700` | Credential paths |
| `disposition-first` / `open review threads` | #146 pipe alignment |
| `context_key` + **continue-only** | #145 Jules sessions |
| `ROLE:` + `VOTE:` ballot form | Debate / Delphi |
| `Signed-off-by: … session-… / msg-…` | OPERATOR signing |
| `AGENTS.grimoire` + `AGENTS.conv` dual-file | Grimoire rename path |
| `Round-trip perfect reconstruction` | Merge measurement |

## Disposition markers (pipes)

```text
🟢 accept / ready
🟡 caution / needs work
🔴 block
⚪ unknown / no disposition yet
```

## Probe vs disposition (do not confuse)

| Signal | Actionable? |
|--------|-------------|
| Unresolved review **threads** | Yes |
| Explicit disposition / request_changes | Yes |
| `🏁 Script executed` / Analysis chain dumps | **No** — evidence only |
| `<!-- agent-auto-jules -->` marker | Coordination, not a finding |

## Research backlog (#96)

- [ ] Mine `docs/`, `AGENTS.md`, `GEMINI.md`, DEBATE/ITEMS for more must-include lists
- [ ] Catalog Jules/Gemini workflow prompt templates
- [ ] Produce `docs/research/cheat-code-inventory.md` (path, hash, model affinity, confidence)
- [ ] Flag operator-private packs — never paste into public issues

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-mandatory-phrases
