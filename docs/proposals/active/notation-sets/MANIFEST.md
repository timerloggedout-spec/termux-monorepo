---
id: notation-sets-evolution
title: "Notation Sets, Living Lexicon, and Cross-Domain Semantic Index"
author: ChatGPT
posted_at: 2026-08-22
source: source.md
status: posted
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_issues: [320, 309, 182, 175, 126, 304, 196, 177, 208, 274]
related_prs: [322, 324]
related_branches:
  - docs/notation-sets-evolution
  - docs/mintlify-notation-sets-page
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — notation-sets-evolution

## Summary

Establish #320 as the proposal/specification layer for a canonical, continuously evolving notation vocabulary supporting #309 Grimoire compression and its related semantic/indexing work. The proposal separates canonical notation from domain aliases and domain-specific syntax, connects the vocabulary to the repository's existing pointer/concept/tool/context indexes, and defines a research-driven evolution loop so the glossary/dictionary remains synchronized with implementation and operator governance.

## Linguist lineage

`LINGUIST-LINEAGE.md` records #320 as the semantic research/specification surface within the broader Linguist/CEDRlang/Grimoire lineage. Historical implementation issues remain provenance/evidence; governed successors and projection surfaces retain their own authority boundaries.

## Research basis

This revision integrates two prior research sessions:

- **Language information density & ADLM** (2026-08-23): Coupé et al. 2019 (cross-language convergence near ~39 bits/s); Petrov et al. EMNLP 2023 (tokenizer inequity across scripts); FLORES-200 aligned corpus; tiktoken `cl100k_base`/`o200k_base`; a versioned token-cost measurement tensor; Adaptive Dynamic Language Mixing as a tokenizer- and model-specific semantic codec with a canonical-IR truth layer and hard quality/validity gates.
- **Grimoire compression & category-theoretic IR** (2026-08-22): layered compression stack (zstd, LZ4, Brotli, libarchive, FastCDC, xdelta3, MessagePack/CBOR, Arrow/Parquet); canonical IR for category theory; interning, canonicalization, hash-consing, and per-corpus dictionary training; the `grimoire-core/codec/store/interop` package layout.
- **#324 research integration:** NSE-009 through NSE-018 extend the proposal with measurement, adaptive codecs, evolutionary optimization, canonical IR, agent-native communication, context conditioning, and falsifiable controls. These are research hypotheses/contracts, not proof of implementation efficacy.

These additions remain governed by NSE-008 (evolution ledger). The proposal remains malleable by design and is not frozen by the research expansion.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| timerloggedout-spec | operator-authorizer | requested | 2026-08-22 | Operator review requested before execution |
| ChatGPT | author | posted | 2026-08-22 | Proposal authored from #320 and repository structure |

## Review log

### 2026-08-22 — ChatGPT

- Disposition: posted
- Notes: Proposal connects #320 notation work to #309/#182 and #175's operational gates without claiming implementation is complete.

### 2026-08-22 — timerloggedout-spec (research integration)

- Disposition: revised (items added, not frozen)
- Notes: Integrated language-density + ADLM + grimoire-compression research as NSE-009…NSE-018. Expanded `related_issues` to include #126, #304, #196, #177, #208, #274 per the #309/#182 relationship map. Added agent-native compressed communication (NSE-016) and domain/repo/author-org codec conditioning (NSE-017) using the forked Zipf corpora as reference study sets. Proposal remains malleable per NSE-004/NSE-008. Status stays `posted`; acceptance still required before execution merges.

### 2026-08-23 — lineage reconciliation

- Disposition: documentation reconciliation
- Notes: Added `LINGUIST-LINEAGE.md` to distinguish historical Linguist evidence (#126/#154/#177/#196/#208/#218/#228), governed reconciliation (#274/#275), projection work (#304), and the #320/NSE semantic research layer. Added PR #324 and the Mintlify notation-sets docs branch to manifest provenance.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Linguist lineage/provenance map added
- [ ] At least one non-author review recorded
- [ ] Status → accepted before execution merges
- [ ] PRs cite `Implements: <ITEM-ID>`
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
- Linguist lineage: ./LINGUIST-LINEAGE.md
- Issue #320: https://github.com/timerloggedout-spec/termux-monorepo/issues/320
- Issue #309: https://github.com/timerloggedout-spec/termux-monorepo/issues/309
- Issue #182: https://github.com/timerloggedout-spec/termux-monorepo/issues/182
- Issue #175: https://github.com/timerloggedout-spec/termux-monorepo/issues/175
- PR #322: https://github.com/timerloggedout-spec/termux-monorepo/pull/322
- PR #324: https://github.com/timerloggedout-spec/termux-monorepo/pull/324
