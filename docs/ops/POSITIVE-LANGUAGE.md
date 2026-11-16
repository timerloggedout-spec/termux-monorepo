# Positive directed language for agent rules

> **Status:** LIVE (2026-08-06)  
> **Agent:** Grok  
> **Follow-up:** Operator Gemini Gem (positive-language) — integrate from Google Drive when connected

## Why

Negation-heavy rules (“Don’t X”, “Do not Y”) still **name the forbidden act**. Recency bias in humans and models amplifies the trailing clause. Prefer stating the **desired** behavior.

## Prefer / Avoid table

| Prefer (directive) | Avoid (negation-first) |
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

Applies to `AGENTS.md`, `GEMINI.md`, workflow prompt strings, and ops docs agents read first.

Signed-off-by: Grok <grok@x.ai>
