# 11_Evaluation_Quality

Evaluation providers, experiment tooling, benchmark methods, and quality-gate references.

| Reference | Primary role | Disposition |
|---|---|---|
| langfuse | LLM traces, datasets, scores, prompts, experiments | P1 adapter comparison |
| phoenix | LLM traces, evaluations, datasets, experiments | P1 adapter comparison; ELv2 review |

Providers consume the same canonical cohort and evidence contract. Repository-owned JSONL/receipts, ATES, and dual-gate retain authority.

## Cited inspiration sources

- [Notary — signed receipts, tamper-evident ledger, independent release verification](../smods/INSPIRATION-SOURCES.md#notary)
- [ShipProof — independent acceptance missions, exact-revision evidence, post-deploy replay](../smods/INSPIRATION-SOURCES.md#shipproof)
- [Unresolved Transcend showcase candidate](../smods/INSPIRATION-SOURCES.md#unresolved-candidate)

Preserve source claims, inspected code, executed tests, and independently reproduced behavior as distinct evidence classes.

Each reference directory contains README and SOURCE metadata. Registration creates no runtime dependency.
