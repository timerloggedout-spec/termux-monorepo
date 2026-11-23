# DERP specification decision matrix

**Candidates:** SPEC-A-01 and SPEC-B-01 · **Version:** 0.1.0-draft

| Criterion | SPEC-A: zero-width envelope | SPEC-B: visible-first grammar | Evidence required |
|---|---|---|---|
| Cross-platform resilience | Lower expected resilience | Higher expected resilience | Unicode/HTML/Markdown fixture suite |
| SEO clarity | Depends on visible fallback | Native visible tokens | Search preview and extracted text |
| Accessibility | Requires careful fallback | Directly expressible | Screen-reader and keyboard review |
| Puzzle atmosphere | Strong | Moderate-to-strong | Newcomer usability sessions |
| Debuggability | Decoder and code-point tooling | Plain-text inspection | Contributor task timing |
| Agent Ready separation | Requires export stripping | Native plain profile | Exact output diff |
| Pointer integrity | Registry + envelope validation | Registry + visible token validation | Broken/stale pointer tests |

## Decision rule

Choose the proposal with the best combined reliability, accessibility, discovery completion, and maintainability. Treat cryptic density as a design benefit only after core navigation and comprehension pass.

Record the selected proposal, rejected trade-offs, fixture results, and migration plan here. Until then, both remain competing drafts.
