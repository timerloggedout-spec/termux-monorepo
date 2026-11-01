# Navigation

Single source of truth ladder when orienting in the tree.

| Priority | Start here | What you get |
|----------|------------|--------------|
| 1 | `README.md` (root) | Navigation ladder + subsystem inventory |
| 2 | `CLAUDE.md` (root) | Primary collaborator entry: governance, hard rules, dual gates. Load first for agent work |
| 3 | `docs/icm/CLAUDE.md` → `docs/icm/CONTEXT.md` | ICM system map: pick one card/process; source wins over card |
| 4 | `archwiz/TOOL_INDEX.md` | 28 tools / 7 categories (per the index's own header) |
| 5 | `archwiz/CONCEPT_INDEX.md`, `REFERENCE_HUB.md`, `METHODOLOGY_INDEX.md` | Concepts + status, manifest links, approaches tried |
| 6 | `docs/ops/DOCS-BRANCH-INDEX.md` | Docs-lane branch inventory + pointers to master records (certifications, provider/dispatch, fleet) |
| 7 | `docs/proposals/registry.yaml` | Proposal package registry (registers package directories; passes carry their own PASS records) |
| 8 | `_Entry+ReadMe.md` | One-line command → entry table |
| 9 | `termux-ecosystem-architecture.html` | Visual ecosystem diagram |

## Where to start for a task

| What you want to do | Where you start |
|---------------------|-----------------|
| Make a change | Root `CLAUDE.md`, then the one matching ICM card under `docs/icm/` |
| Provider / model routing | `docs/icm/routing.md`, `docs/ops/PROVIDER-DISPATCH-MAP.md`, `llm_api_hub/ROUTING.md` |
| Quota questions | `ops/quota/allocations.json` (SSOT) + `docs/ops/QUOTA-ALLOCATION-PLANNING.md` |
| Certifications | `docs/ops/CERTIFICATIONS-PROGRAM.md` + `guides/certifications-roadmap.mdx` |
| Dated snapshots / old recon | `docs/ops/archive/` (dated records are archived there; living surfaces are named in the archive PRs) |
| Open the cockpit | `python3 archwiz/archwiz.py` |

Also see root `README.md` and `_Entry+ReadMe.md`.
