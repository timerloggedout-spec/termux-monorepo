# Linguist Agent-Contact Inventory and Drift Assessment

**Collected:** 2026-08-20 UTC

**Repository revision inspected:** `933d65d0e2c49e28079f300f5a516932330c60e7`

**Collection boundary:** tracked repository files, with the context-relationship scope exclusions applied. Session archives, browser/device state, secrets, generated relationship-index internals, vendor material, and runtime workspaces are not agent-contact inputs for this review.

## Canonical and Projected Instruction Surfaces

The root `AGENTS.md` is the controlling instruction surface. It requires proposal registration, bounded relationship reconnaissance, an `Implements:` work-item reference, and the repository gate pair before integration. `CLAUDE.md` is a short delegating projection that directs Claude-compatible agents back to `AGENTS.md`. The root `AGENTS.hum.md` is a tracked human companion, but it is not a generated CEDRlang projection: it largely mirrors the readable root content and has already drifted on at least the integration-branch guidance.

| Surface | Current role | Compression eligibility | Finding |
|---|---|---|---|
| `AGENTS.md` | Root governance and technical instructions; authoritative for agents. | **Not eligible for lossy/public-only replacement.** A future machine projection must be generated from a readable canonical record and retain mandatory governance text. | Current root policy requires `master`, while the change process specifies `master-staging`; this must be reconciled before any generation work. |
| `AGENTS.hum.md` | Tracked human-readable companion. | **Candidate canonical source after a decision record.** | It duplicates the root surface rather than proving a reproducible source/projection pipeline. |
| `CLAUDE.md` | Claude-specific routing shim to `AGENTS.md`. | **Low-value projection.** Keep plain and short; do not compress it independently. | Its content is intentionally referential, so a generated compressed variant would add little value and risks a stale pointer. |
| `docs/icm/AGENTS.md` and `docs/icm/CLAUDE.md` | Parallel ICM system-map entry points. | **Not in the initial codec migration.** | These files are navigation artifacts and must remain directly readable; their actual sources are the cited ICM cards and governing documents. |
| `docs/icm/maintenance/{AGENTS,CLAUDE}.md` | Human-gated documentation-maintenance guidance. | **Excluded.** | The ICM map itself says maintenance requires a human gate. |
| `README.md` | Public, human-facing recovery and inventory documentation. | **Presentation-only.** | L337 styling may be editorial, but the file cannot conceal behavior, safety constraints, credentials, or materially operational instructions. |

## Runtime, Codec, Pointer, and Dictionary Surfaces

The current implementation contains three distinct systems that have been conflated by the Linguist PR family. The first is the CedrLang regex translator, the second is CID-backed CEDARscript command pointers, and the third is a public Grimoire presentation lexicon. They need separate ownership, APIs, tests, and security claims.

| Surface | Actual responsibility found | Required disposition |
|---|---|---|
| `workspace/compression_sandbox/cedrlang/cedrlang.py` | Regex-based prose/document translator with symbolic and Grimoire substitution tables, formatting placeholders, rough token statistics, a CLI, and no mapper custody, CIR, A2A schema, digest, version negotiation, or 70% coverage gate. | **Refactor target.** Rename/document it as a non-executing CEDRlang codec; retain only deterministic public test mappings in the repository. |
| `tests/test_cedrlang.py` | Validates selected round trips and Markdown protection. | **Expand.** Add collision, malformed input, canonical-digest, mapper-version, coverage denominator, A2A, and contact-surface fixtures. |
| `bin/cedrlang` | Public launcher that directly invokes the current codec script. | **Compatibility surface.** Preserve as a thin stable entry point or add a documented adapter during a package migration. |
| `workspace/compression_sandbox/cedrlang/cid.py` | `CedarIndex` registry that writes short pointers for CEDARscript commands to `~/.cedar/cedar_index.json`; it registers and expands an edit-command catalog. | **Separate from CEDRlang.** Do not rename or absorb it into a document codec. It needs its own review because it is a command-pointer registry, not a CEDRlang private mapper. |
| `.cedar/cedar_index.json` | Tracked mapping file cited in Linguist discussions. | **Not private.** It must not be treated as the internal/private mapping needed for lossless CEDRlang document reconstruction. No contents were recorded in this review. |
| `harmony_hub/config/GRIMOIRE_DICTIONARY.md` and `harmony_hub/config/grimoire/1337_D1CT10N4RY.md` | Tracked public style and vocabulary references; the former also embeds pointer examples. | **Public presentation lexicon only.** Split pointer examples from diction terms in a later scoped cleanup; neither document qualifies as a protected mapper. |
| `harmony_hub/workspace/agent/LINGUIST_SPEC.md` | Current role definition assigns both CedrLang translation and CID pointer registry responsibilities to Linguist. | **Drift source.** Replace its mixed mandate with separate non-executing codec/A2A and CEDARscript-pointer responsibilities after the proposal is accepted. |
| `harmony_hub/src/patch_router.py` | Execution-capable route that can invoke CEDARscript, `sed`, or generated Python. | **Hard boundary.** It must never be reachable from CEDRlang compile/decompile or from an A2A envelope validator. |

## Verified Drift and Blocking Findings

| ID | Classification | Finding | Evidence |
|---|---|---|---|
| D-01 | Blocking design conflict | A public/one-way or lossy transform cannot, by itself, satisfy a perfect reconstruction claim. The current CedrLang `compile_doc` and `decompile_doc` use public in-repository regex maps, not an access-controlled mapper. | `cedrlang.py` lines 74–148 and 241–362; PR [#177](https://github.com/timerloggedout-spec/termux-monorepo/pull/177#issuecomment-5273315069). |
| D-02 | Blocking security-boundary conflict | The cited `.cedar/cedar_index.json` and Grimoire dictionaries are tracked in the repository. They cannot be represented as an internal/private mapping or as an obfuscation security boundary. | `git ls-files --stage` metadata; PR [#177](https://github.com/timerloggedout-spec/termux-monorepo/pull/177#issuecomment-5273357771). |
| D-03 | Blocking scope mix | CID maps CEDARscript editing commands and persists them under a user home directory; CEDRlang translates documents. Combining these responsibilities risks treating a code-editing surface as a passive communication codec. | `cid.py` lines 3–62 and 64–111; `LINGUIST_SPEC.md` lines 3–18; [CEDARScript Editor (Python)](https://github.com/CEDARScript/cedarscript-editor-python). |
| D-04 | Required correctness work | The source does not calculate the defined eligible-token substitution coverage, enforce a 70% threshold, attach a mapper version, canonicalize a CIR, or verify a digest. Existing tests cover only selected textual round trips. | `cedrlang.py` lines 328–384; `test_cedrlang.py` lines 10–149. |
| D-05 | Required protocol work | No local CEDRlang A2A envelope/schema/ACK/NACK/idempotency implementation exists. A historical Agent Mail action used an unaudited remote installation pipe and background service pattern, which is outside the initial deterministic local A2A scope. | Issue [#117](https://github.com/timerloggedout-spec/termux-monorepo/issues/117); PR [#143 files](https://github.com/timerloggedout-spec/termux-monorepo/pull/143/files). |
| D-06 | Required governance reconciliation | Root `AGENTS.md` says target `master`; the ICM change process and status board say tracked code changes target `master-staging`. | `AGENTS.md` lines 22–30; `docs/icm/processes/change-and-validate.md` lines 16–34; `docs/ARCHW1Z-STATUS.md` lines 38–45. |
| D-07 | Review disposition | PR #154 is currently open, large, and marked dirty; its latest operator guidance says to reconstruct only unique value in a small rebased hygiene-passed change. PR #177 is also open, dirty, and contains unrelated bulk changes. | PR [#154](https://github.com/timerloggedout-spec/termux-monorepo/pull/154#issuecomment-5322143674); PR [#177](https://github.com/timerloggedout-spec/termux-monorepo/pull/177). |

The initial implementation scope is therefore limited to a clean, non-executing CEDRlang foundation: canonical record/schema, deterministic codec, synthetic test mapper, coverage/digest validation, and local A2A envelope validation. It excludes CEDARscript execution, CID registry changes, external workflow installation, public obfuscated posting, and broad rewrites of the root instruction documents.

## References

1. [Root AGENTS.md](../../AGENTS.md)
2. [Root CLAUDE.md](../../CLAUDE.md)
3. [Change and Validate ICM process](../../docs/icm/processes/change-and-validate.md)
4. [PR #154 operator scope guidance](https://github.com/timerloggedout-spec/termux-monorepo/pull/154#issuecomment-5322143674)
5. [PR #177 mapping discussion](https://github.com/timerloggedout-spec/termux-monorepo/pull/177#issuecomment-5273315069)
6. [CEDARScript Editor (Python)](https://github.com/CEDARScript/cedarscript-editor-python)
7. [Agent2Agent Comms Proposal, issue #117](https://github.com/timerloggedout-spec/termux-monorepo/issues/117)
