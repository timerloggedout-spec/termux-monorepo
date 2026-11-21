# Linguist Language Lanes — DWP-01

**Status:** candidate registry contract  
**Parent:** [Issue #5740](https://github.com/timerloggedout-spec/termux-monorepo/issues/5740)  
**Existing terminology authority:** [Nomenclature Equivalency Matrix](../nomenclature-matrix/)

## Purpose

Register DerpWiki, PigLatin, and the existing Leet / 1337 and Siglary mappings as peer language lanes. Preserve DevinWiki as a provider-managed source. Each lane owns its own terms, aliases, fixtures, provenance, version, and review state. The shared publication composer combines lane outputs without becoming a second vocabulary authority.

## Publication profiles

| Profile | Unicode tag layer | Agent Ready badge role | Presentation |
|---|---:|---|---|
| `validation` | OFF | Required validation surface | Canonical readable content |
| `public` | ON | Separate from validation badge evidence | Playful encoded presentation |

The public profile adds an optional Unicode tag-character rendering layer (U+E0000–U+E007F) to bounded, inert puzzle payloads. It preserves the existing owner mapping and canonical text. The layer supplements existing Leet/Siglary/DerpWiki/PigLatin mappings; it does not replace them.

The public puzzle presentation carries no automatically injected challenge-revealing copy. The owner mapping remains the inspection surface and records the canonical text, rendered text, decoded text, exact code points, codec/version, lane and term identifiers, provenance, publication profile, and reviewed revision.

## Owner mapping contract

The mapping view presents rendered text beside canonical and decoded text, plus the exact Unicode code points. It supports deterministic inspection and export of both encoded and decoded forms. Mapping assertions continue to use the existing candidate-first nomenclature model: evidence, relation type, confidence, review status, and version remain attached to each term.

## Integrity boundaries

- Keep canonical content and all existing mappings as the source of truth.
- Keep the Unicode layer limited to inert, explicitly delimited puzzle data.
- Preserve ordinary words as contiguous text.
- Keep crawler instructions, metadata, prompts, credentials, authorization data, executable content, filtering inputs, and moderation inputs in canonical readable form.
- Preserve deterministic decode and test normalization, truncation, copy/paste, malformed payloads, and code-point inspection.
- Keep Agent Ready validation receipts tied to the validation URL, profile, commit, timestamp, and digest.

## Registry

The machine-readable peer-lane and profile contract is [`lanes.json`](lanes.json). The Nomenclature Equivalency Matrix remains the terminology/evidence authority; this file registers lane ownership and publication behavior only.
