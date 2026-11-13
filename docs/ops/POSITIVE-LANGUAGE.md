# Positive directed language for agent rules

> **Status:** LIVE (2026-08-06)  
> **Agent:** Grok  
> **Follow-up:** Operator Gemini Gem (positive-language) — integrate from Google Drive when connected

## Why

Action-first rules focus human and agent attention on the intended state change. Lead with the **desired** behavior and attach the smallest necessary boundary.

## Prefer / Avoid table

| DO statement | Legacy phrasing (reference examples) |
|--------------------|-------------------------|
| Keep agent shell and `gh` available in trusted ADE runs | Don’t remove agent shell access |
| Target `master-staging` for code | Do not push code to `master` |
| Keep secrets and Class 3/4 artifacts out of git | Do not commit secrets |
| Split unrelated files into a new PR before merge | Do not leave unrelated files in the merge diff |
| Reply “out of scope — see #N” on mismatched review threads | Do not fix out-of-scope findings on this PR |

## Pattern

1. **Lead with the positive action.**
2. If a boundary is required, place it in a short **Avoid** column or a single trailing clause — never as the only content of the rule.
3. Prefer **Keep / Prefer / Target / Use / Preserve** over **Don’t / Do not / Never** as the primary verb.

## Scope

The active repository-wide contract is [`DO-STATEMENT-MANDATE.md`](DO-STATEMENT-MANDATE.md). Apply it to `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `SKILLS.md`, every skill, code comments, workflow prompts, commit messages, pull-request descriptions/comments, and chat relays. Keep historical examples as quoted reference material.

Signed-off-by: Grok <grok@x.ai>


## Enforcement route

Use direct DO statements as the default authoring form. Keep formal negation where logic, code, source quotations, or safety semantics require it. Apply CAVEMAN-6 and the registered Siglary operator classes with accuracy as the governing constraint.

Canonical policy: [DO-STATEMENT-MANDATE.md](DO-STATEMENT-MANDATE.md).
