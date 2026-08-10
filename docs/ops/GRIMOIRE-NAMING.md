# Grimoire naming mandate (rename CEDAR* / cedr*)

**Authority:** OPERATOR · Source intent from #90 + repeated rename requests.

## Rule

| Legacy name | Status | Canonical |
|-------------|--------|-----------|
| `CEDARLang` / `cedrlang` / `cedr` | **Deprecated as product name** | **Grimoire** (family) |
| `CEDARScript` / `cedarscript` | **Seed only** (one dialect among several) | Keep as historical seed; do not brand the monorepo stack as CEDARScript |
| `cid.py` / `CID` | **Retained** | Command/pointer index under Grimoire toolkit |
| `Grimoire` / `Grimiore` (spelling variants) | Prefer **Grimoire** | Docs + module names |
| `MaxC` / `MaxUp` / caveman compressors | Related tools | Sibling compilers in the same compression family |

CEDARScript is a **seed** of several compression/editing dialects already in-repo (`workspace/cedar_forge`, `workspace/compression_sandbox`, caveman research). The monorepo product line is **Grimoire + CID**, not CEDAR*.

## Paths (target)

```text
workspace/compression_sandbox/cedrlang/     → workspace/compression_sandbox/grimoire/   (migrate)
  cedrlang.py                              → grimoire.py  (or keep alias shim one release)
  cid.py                                   → cid.py       (keep name)
AGENTS.cedr.md                             → AGENTS.grimoire.md
```

Migration may be staged: **shim exports** for one cycle so Jules/#126 does not break mid-flight.

## PR #126 intent fix

Linguist PR must:
1. Ship dual-file AGENTS convention (see `AGENTS-DUAL-FILE.md`)
2. Round-trip tests as **merge measurement** (perfect reconstruction)
3. Prefer Grimoire naming in new symbols/docs; deprecate CEDARLang branding in user-facing strings

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-grimoire-naming
