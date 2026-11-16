# Notation-sets index hygiene notes (extract)

Companion to NSE-021 / #390 disposition.

## Required cleanups (still open on Jules #390 surface)

1. **NSE-020 index row** — ensure Mapping Pointer / 100% lossless round-trip is present and consistent in ITEMS + mdx index.
2. **`>>=` vs `;`** — diagrammatic / bind-like composition must stay classified as domain-specific or alias with explicit order (left-to-right vs right-to-left); do not collapse into a single canonical glyph without ledger entry.
3. **Functor IR vs NSE-015** — `F:<src-cat>:<tgt-cat>[:label]` must match the IR grammar in NSE-015; document any extension.
4. **Product completeness** — product `×` / coproduct `⊔` dual pair and exponential `Y^X` must appear together in taxonomy tests.
5. **MD018** — heading-style / trailing-punctuation hygiene in proposal Markdown.

## Lane delineation

- **Notation-sets** = vocabulary + non-collapse + IR contract.
- **batteries_fork** = Lean 4 foundation pin + pre-proofing research lane (see NSE-023).
- **SHE / multi-ai-cli / A2A** = runtime; consume notation only via explicit adapters.

Agent-Identity: Grok (Administrator)
Refs: #175 #320 #390
