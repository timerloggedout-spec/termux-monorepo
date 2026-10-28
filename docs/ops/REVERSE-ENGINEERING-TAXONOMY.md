# Reverse Engineering — taxonomy & toolchains (fleet version)

`[MUSEai]@{role:{reverse-engineering-toolkits}}` — the RE category's own
version of the collaborator-supplied taxonomy example (Perplexity export,
owner-supplied 2026-10-28: a cybersecurity polyhierarchy with an RE
category/toolchain map). Their version is a readable essay; this one is
the fleet's working registry — machine-readable, validated in tests,
with the fleet's own assets placed in it. An improvement-research
request against this v1 is filed through the research-intake pipeline
(see the closing section).

Machine SSOT: `ops/reverse_engineering/taxonomy.json`
(`re-taxonomy/v1`), validator/query: `ops/reverse_engineering/taxonomy.py`,
tests: `tests/test_reverse_engineering_taxonomy.py`.

```bash
python3 -m ops.reverse_engineering.taxonomy validate
python3 -m ops.reverse_engineering.taxonomy node mobile-android
python3 -m ops.reverse_engineering.taxonomy toolchain mobile-android
python3 -m ops.reverse_engineering.taxonomy overlap
```

## What changed vs the collaborator example

| Theirs | Ours (and why) |
|---|---|
| Whole cybersecurity field in one hierarchy | This registry is the **RE family only**; the umbrella (field families, hats/teams/visibility axes, credentials) is recorded as context in `umbrella`, not modelled here — this lane owns RE, and kinds stay distinct (Kali = platform, CISSP = credential, CTF = format, pentest = activity) |
| Overlap described in prose + a qualitative matrix | Overlap is **structural**: extra `parents[]` (polyhierarchy) + axis `tags{}` on every node, plus the overlap matrix as data with a fixed value vocabulary (`central/supporting/peripheral`) |
| Tool lists per category | **Toolchains as stage handoffs**: `acquire → identify → extract → analyze-static → observe-dynamic → validate → document`, each stage naming its tool(s) and the output that passes on — a chain is not a shopping list |
| Example YAML record | Same record shape, machine-checked: parents/tools in the example must resolve to real nodes (validator-enforced) |
| No fleet assets | Fleet placed: `apk-xref` belt (PR #2143) as the Android chain's acquire/extract/cross-validator, the Web Adapter Foundry as the web-client chain's factory, Kali as a registered **workspace** (offload-only, per the campaign doc), the Foundry's web taxonomy named as this registry's sub-registry for `target-web-client` |
| Evidence words: observed/inferred/unverified | The Foundry's evidence vocabulary, extended fleet-wide: `observed | inferred | reproduced | contradicted | unknown` |

## The shape

- **Primary tree by target** — native (PE/ELF/Mach-O), bytecode
  (JVM/Android DEX/.NET), scripts, firmware (embedded-Linux/bare-metal),
  protocols & formats, hardware-assisted, mobile, web clients — because
  the target decides the toolchain. Method and objective are **axes**,
  not branches: `method` (static/dynamic/hybrid/comparative/emulated/
  automated) and `objective` (understanding, interoperability,
  malware-analysis, vulnerability-research, patch-analysis,
  cross-validation, ctf, incident-support) tag any node.
- **Work families are nodes too** — malware analysis and CTF reversing
  are objectives with their own chains, not targets; the tree keeps
  them distinct from both.
- **The Android lesson is encoded**: `mobile-android` and
  `bytecode-android-dex` cross-parent each other — an APK is manifest/
  resources (Apktool, apk-xref), DEX (JADX), and native `.so` (Ghidra),
  correlated at runtime (Frida). One decompiler view is incomplete by
  construction.
- **Placement rules** (validator-enforced where mechanical): placed
  once by primary kind; no duplicate nodes for overlap; every tool
  carries a `tool_role`; every node descends from the root; toolchains
  reference real tool nodes in stage order.

## Registered sibling registries

- Web RE: `ops/web_adapter_foundry/taxonomy.json` — the nested
  sub-registry under `target-web-client` (engines, drivers,
  capture-and-recon, contract-synthesis, adapter-systems…).
- APK cross-reference belt: `docs/ops/APK-XREF-TOOLKIT.md`.
- Kali: registered environment in
  `docs/ops/WEB-REVERSE-ENGINEERING-CAMPAIGN.md` — here it is the
  `kali-linux` workspace node, `environment: ci-remote` (B160V law:
  offload/container only).

## Improvement research (requested)

Filed via the research-intake template set (`research:service`,
label-routed, deterministic parser) with the scoped question: what
should v2 change — missing target families or tools (e.g. iOS
bytecode, WASM-first chains, symbolic/concolic tooling), axis
vocabulary gaps vs the field's standards (Kali tool catalog, MITRE
ATT&CK as a classification layer, OWASP WSTG/ASVS for the web chain),
and whether the overlap matrix should move from qualitative values to
measured fleet usage. The research record lands through the
Observatory/research-seeds pipeline; adoption of any change stays a
separate, evidence-led PR in this lane.
