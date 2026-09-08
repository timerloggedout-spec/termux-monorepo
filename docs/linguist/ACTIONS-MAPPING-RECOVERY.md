# Linguist Actions / Mapping Recovery

## Status

Research and integration plan. This document does **not** activate automatic public-comment obfuscation.

## PR #154 evidence

PR #154 explicitly proposed an encrypted pointer mapping as the working model while lossless compression/decompression was developed further. The comments describe a public-facing lossy representation and a private encrypted pointer index intended to support guaranteed lossless reconstruction.

The same discussion proposes integrating the mapping with agent-ingestion material and GitHub Actions: public comments could carry an obfuscated surface, agents could exchange CAVEMAN-compressed material, and collaborators could retain access to a human representation.

The historical implementation discussion also identifies `REV_SYMBOL_MAP` and `REV_GRIMOIRE_MAP` as explicit reverse tables intended to avoid decompile collisions.

## What is implemented vs proposed

### Implemented lineage

- `workspace/compression_sandbox/cedrlang/cedrlang.py` — historical CedrLang compiler/decompiler and symbol/Grimoire mapping.
- `AGENTS.md` / `AGENTS.hum.md` — historical compressed/human projection milestone.
- `.jules/Linguist.md` — performance/provenance learning ledger.
- `workspace/llm_map/` and `archwiz/` — existing taxonomy, pointer, alias, concept, tool, and relationship index surfaces.
- `phase_codec.py` — current master recovery seed for the PR #154 70% diaspora experiment.
- `mapping_pointer_index.py` — current recovery contract for explicit mapping provenance.

### Proposed in PR #154 comments, not verified as historically deployed

- outbound GitHub Actions hook that obfuscates public comments;
- inbound private-agent decompression hook;
- collaborator decryptor/UI;
- encrypted private mapping-pointer store as the authoritative reconstruction sidecar.

These remain architecture candidates until a historical commit or artifact proves an earlier deployment.

## Correct layered contract

```text
canonical human/semantic source
        |
        v
canonical IR / semantic index
        |
        +--> public renderer -> lossy/obfuscated surface
        |
        +--> private renderer -> exact compressed surface + encrypted mapping sidecar
                                      |
                                      v
                             Mapping Pointer Index
                                      |
                                      v
                            exact reverse reconstruction
                                      |
                                      v
                              canonical IR / source
```

The public lossy surface is an **obfuscation/representation layer**, not a cryptographic security boundary. Confidentiality must come from access control and encryption of the private mapping material.

## Actions integration sequence

1. **Offline fixture:** run historical and current codecs against representative Markdown, code, URLs, paths, numbers, lists, headings, symbols, and nested formatting.
2. **Exact round-trip gate:** require `decode(encode(x)) == x` for private/exact mode.
3. **Public-lossy gate:** require readability plus explicit declaration that exact reconstruction is unavailable without the private mapping sidecar.
4. **Pointer integrity:** verify mapping version, codec version, source digest, encoded digest, and mapping digest before reconstruction.
5. **Workflow dry-run:** Actions may generate artifacts in a controlled test job; no automatic mutation of public comments.
6. **Agent-ingestion dry-run:** ingest fixture comments and verify deterministic reconstruction from the private mapping fixture.
7. **Security review:** ensure private mappings/keys never enter logs, artifacts, caches, comments, or repository history; preserve existing 0o600/0o700 policy where applicable.
8. **Operator acceptance:** only after #175 gates and a separately accepted NSE item should an outbound public-comment hook be enabled.

## Historical large-commit question

A search of the repository commit history finds substantial GitHub Actions work, including the later DeepSeek CI integration in #174 and multiple Actions governance/refinement commits. However, the supplied PR #154 comments establish the **Actions integration as a proposed next step**, not proof that a large multi-file Actions implementation for the mapping system was merged at that point.

The recovery process therefore searches the historical commit graph for the missing implementation rather than reconstructing it from the comment alone.

## Related evidence

- PR #154 comments: encrypted pointer mapping; lossy public surface; lossless private reconstruction; Actions/agent ingestion integration; reverse symbol/Grimoire maps.
- `discussion_r3754718523`: 70% randomized `to_1337speak()` threshold.
- `discussion_r3754876987`: reverse-map collision avoidance and mapping-to-agent ingestion question.
- #196 / `ea2a2f8e...`: accepted O(N) CedrLang v2 + `AGENTS.hum.md` round-trip milestone.
- `dc8c08d`: CedrLang v2 implementation baseline.
- #218 / `7a6e5a7...`: single-pass regex optimization.
- #228 / `267fecc...`: fast-path term search.
- #175: operator/CI gate.
- NSE-019: phased diaspora recovery.
- NSE-020: Mapping Pointer / round-trip implementation contract.

## Non-goals

- Do not treat obfuscation as encryption.
- Do not store secrets in the mapping index.
- Do not automatically rewrite public GitHub comments yet.
- Do not make the compressed surface the semantic source of truth.
- Do not infer a missing historical implementation merely because a PR comment proposed it.
