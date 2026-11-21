# Linguist Language Lanes — DWP-01

**Status:** candidate registry contract  
**Parent:** [Issue #5740](https://github.com/timerloggedout-spec/termux-monorepo/issues/5740)  
**Existing terminology authority:** [Nomenclature Equivalency Matrix](../nomenclature-matrix/)

## Purpose

Register DevinWiki, Leet / 1337$934K, Siglary, DerpWiki / d3rpWiki, and PigLatin as peer language lanes. Each transformation lane owns vocabulary, aliases, fixtures, provenance, versions, and review state. The shared composer combines lane outputs while allowing public mappings to evolve and mix across versions and domains.

## Publication profiles

| Profile | Invisible Unicode | Agent Ready badge role | Mapping behavior |
|---|---:|---|---|
| `validation` | OFF | Required validation surface | Canonical readable baseline |
| `public` | ON | Separate from validation badge evidence | Mutable playful remapping and version mixing |

The public profile intentionally changes the visitor-facing mapping experience. DerpWiki may paraphrase, reframe, or cross-map concepts between domains; Leet / 1337$934K, Siglary, and PigLatin can participate in declared mixes. The result is a distinct playful presentation, rather than a character-only encoding of an otherwise identical mapping.

## Versioning and mixing

Mapping versions are first-class records. Every public variant carries mapping ID/version, lane ID/version, codec ID/version, source mapping IDs, source and target domains, mix policy, and published revision. Version history is append-only with parent lineage; the public current pointer may advance as mappings evolve.

Version mixing is enabled for same-lane multi-version, cross-lane, cross-domain, and codec-version combinations. A declared compatibility matrix controls valid combinations. Selection is deterministic for a publication revision and mapping set, so a published build can be reproduced and inspected through the owner mapping.

## Cross-domain public use

Initial selection probability: **25% of eligible public mapping selections** use a cross-domain mapping. This is a configurable rollout parameter, not an observed usage statistic or a per-visitor probability. Record the actual selected share and report it separately from the configured probability. Use publication-level deterministic selection; visitor-level tracking is outside this contract.

This 25% mapping-selection rate is independent of the existing CedrLang phase codec's historical **70% per-eligible-character** substitution probability. Reuse `workspace/compression_sandbox/cedrlang/phase_codec.py` and `tests/test_cedrlang_phase_codec.py` as the established reversible 1337 surface; preserve its seeded RNG and known-token scope. The two probabilities govern different operations and remain separately configurable.

## Owner mapping contract

The owner view preserves canonical terms and exposes each public transformation: rendered text, canonical text, decoded text, exact Unicode code points, mapping and lane versions, codec version, source mapping lineage, source/target domains, mix policy, provenance, publication profile, and reviewed revision. It supports deterministic reconstruction and export of both public and canonical forms.

## Unicode layer

The public profile may add Unicode tag characters (U+E0000–U+E007F) to bounded, inert puzzle payloads. The layer works alongside semantic mapping changes. It does not replace versioned mapping records or the owner reconstruction path.

## Integrity and validation

- Keep canonical owner records and mapping history reconstructable.
- Keep public mapping pointers mutable through append-only version updates.
- Preserve crawler instructions, metadata, prompts, credentials, authorization data, executable content, filtering inputs, and moderation inputs in canonical readable form.
- Keep encoded payloads inert and preserve ordinary words as contiguous text.
- Test normalization, truncation, copy/paste, malformed payloads, version compatibility, mixed-version reproducibility, and code-point inspection.
- Keep invisible Unicode OFF for Agent Ready badge validation.
- Bind validation receipts to exact URL, profile, commit, timestamp, and digest.

## Registry

The machine-readable peer-lane, mapping-runtime, version-mixing, and publication-profile contract is [`lanes.json`](lanes.json). The Nomenclature Equivalency Matrix remains the terminology/evidence authority; this registry defines lane ownership and runtime publication behavior.
