# Role prompt pipeline — initial context per role

**Mandate:** Every agent invocation (Jules, Gemini, Omni/OpenRouter, OPERATOR sessions) must receive **role-specific initial context** before task text.

## Assembly order

```text
1. AGENTS.md / AGENTS.grimoire.md (contract)
2. docs/ops/MANDATORY-PHRASES.md (must-include seeds)
3. docs/ops/prompts/<role>.md (this pipeline)
4. context_key block (if PR-bound)
5. disposition / open-threads excerpt (not analysis-chain probes)
6. task-specific user/issue/PR body
```

## Role → snippet map

| Roster id | Snippet path | Primary use |
|-----------|--------------|-------------|
| operator | [`prompts/operator.md`](prompts/operator.md) | Tier-4, matrix commits, signing |
| jules / engineer | [`prompts/jules.md`](prompts/jules.md) | Async builder |
| skeptic | [`prompts/skeptic.md`](prompts/skeptic.md) | Falsify assumptions |
| critic | [`prompts/critic.md`](prompts/critic.md) | Design/quality attack |
| 11th-man | [`prompts/11th-man.md`](prompts/11th-man.md) | Outsider / red-team |
| l337 | [`prompts/l337.md`](prompts/l337.md) | Elite implementation |
| haxor | [`prompts/haxor.md`](prompts/haxor.md) | Adversarial edge cases |
| researcher | [`prompts/researcher.md`](prompts/researcher.md) | Inventory / Cheat_Code mine |
| gemini-triage | use `GEMINI.md` + mandatory phrases | Issue triage |

Full roster: [`ROLES-ROSTER.md`](ROLES-ROSTER.md).

## Workflow injection points

| Workflow | Inject |
|----------|--------|
| `agent-review-auto-jules.yml` | jules + mandatory phrases + disposition excerpt policy |
| `agent-continuous-ops.yml` | jules + **matrix discipline** (no invent outside DECISION-MATRIX / ITEMS) |
| `agent-jules-on-issues.yml` | jules + prior-PR inventory |
| `gemini-*` | GEMINI.md already; add mandatory phrases + role when reviewing as critic |
| OPERATOR sessions | operator snippet + signing ledger rules |

## Excerpt policy (CodeRabbit → Operator & Jules)

See [`CODERABBIT-EXCERPT-POLICY.md`](CODERABBIT-EXCERPT-POLICY.md). **Disposition / open threads drive action.** Analysis-chain probe dumps are evidence only.

## Context method

See [`INTERPRETED-CONTEXT-METHOD.md`](INTERPRETED-CONTEXT-METHOD.md) — scaffold MVP; expand from `refTemplates/` and #96 inventory.

## Continuous maintenance (#150) constraint

Scheduled / continuous ops **must not** expand scope beyond:

1. Rows on [`DECISION-MATRIX.md`](DECISION-MATRIX.md), or
2. `docs/proposals/active/*/ITEMS.md` rows, or
3. Explicit OPERATOR-signed matrix updates.

Challenge sprawl with **ROLE: skeptic** / **ROLE: 11th-man** ballots.

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-role-prompt-pipeline
