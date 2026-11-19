---
name: convention-commit-gate
description: Use at every checkpoint review before committing — enforces centralized enums, no magic string/number literals, constant-based collection/model names, and the project's commit-message style.
---

# Convention & Commit Gate

The smallest gate, applied at every checkpoint alongside
`checkpoint-verification`. Executors reliably leave convention drift (one repo
had 73 status string literals and inline model names with no central enum). Put
the convention requirement in the handoff prompt for new code, and check it here.

## Convention Checklist

- [ ] **Centralized enums.** Every status/type/code is a member of a central
      enum module (e.g. `src/common/enums.ts`), not an inline string/number.
- [ ] **No magic literals.** No bare status strings or numeric codes in logic;
      no magic numbers for thresholds/intervals — name them.
- [ ] **Names via constants.** Collection/model names come from a constant
      (e.g. a `DatabaseCollection` map), never inline string literals.
- [ ] **Follows existing patterns.** New code matches the surrounding module's
      idiom, not the executor's default style.

If any fail, fix (or re-dispatch) before committing.

## Commit Style

Follow the project's configured commit convention. Default for this workflow:
- One-line message: `<type>: <short description>`.
- No `Co-Authored-By` or other footer, unless the project says otherwise.

This is a per-project setting — a company repo with a clean history wants
one-liners; another repo may want trailers. **Read the project's own history
before committing** (`git log --oneline -20`) rather than assuming the default
above.

## Red Flags

| Thought | Reality |
|---------|---------|
| "It's just one status string" | One becomes 73. Centralize it now. |
| "The magic number is obvious" | Name it. The next reader doesn't share your context. |
| "I'll add the enum later" | Later is a cleanup task nobody schedules. Gate it here. |
| "Default commit footer is fine" | Match the project's style — some repos forbid footers. |
