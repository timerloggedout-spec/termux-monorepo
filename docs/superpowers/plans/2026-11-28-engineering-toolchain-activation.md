# Engineering Toolchain Activation — implementation plan

**Date:** 2026-11-28
**Proposal:** `engineering-toolchain-integration`
**Branch:** `feat/engineering-toolchain-activation`
**Target:** `master`
**Execution model:** one bounded repository integration slice; device-side runtime validation remains separately gated.

## Goal

Make the researched FOSS-first engineering ecosystem discoverable and safely routable from the monorepo without creating a second integration registry, task queue, scheduler, evidence ledger or execution authority.

## Decisions

- New independent engineering taxonomy under `ops/engineering/`; Reverse Engineering remains independent.
- Integration Intelligence remains the canonical external integration portfolio.
- Termux Hub exposes only fixed, shell-free, named discovery/validation capabilities.
- GUI/compute-heavy CAD/EDA/CAE/RTL workloads require a pinned remote Linux runner until device suitability is measured.
- QUE/QDesk own admission and execution lifecycle; ArchWiz is discovery/operator surface.
- DoE owns experiment design, MVT is nested, ATES is the harness, AEF owns evaluation outcomes, Learnings owns promoted reusable observations.
- refTemplates remains metadata-first and read-only until a specific source revision is pinned and adopted.

## Tasks and acceptance checks

| Task | Paths | Test / acceptance |
|---|---|---|
| Taxonomy and toolchain registry | `ops/engineering/{__init__.py,taxonomy.json,taxonomy.py}` | Standard-library validator checks IDs, parent graph, axes, tool metadata, ordered stages, tool references and overlap values |
| Termux inventory | `scripts/engineering/toolchain_probe.py` | Mocked PATH test proves read-only detection; JSON output separates catalogued from detected |
| Hub capability wiring | `hub_mcp/policy.py`, `tests/hub_mcp/test_protocol.py` | OBSERVE admission for probe; OPERATE required for taxonomy validation; unknown arbitrary commands remain rejected |
| Engineering regression suite | `tests/test_engineering_taxonomy.py` | Taxonomy, orphan rejection, probe output, free-tier vs paid separation |
| Tool discoverability | ArchWiz index, skill matrix, integration registry | Canonical links resolve; integration state remains discovered/implemented, runtime unverified |
| Queue/evaluation/cross-domain contracts | `docs/ops/ENGINEERING-*.md` | Reuse QUE/QDesk and DoE/MVT/ATES ownership; cross-domain links remain citation-only |
| refTemplates and Learnings | `refTemplates/engineering/`, Learnings matrix | References remain unpinned/read-only; reusable learning requires validated evidence |
| Review and gates | PR + repo-gate + Siglary + Termux smoke | Same immutable head SHA; no promotion from pending/skipped checks |

## Known constraints

1. The current session has no callable Termux device-operation function. The Hub capability implementation can be reviewed in-repository; device probe receipt remains pending.
2. No remote engineering runner has been verified or provisioned. CAD/EDA/CAE execution adapters remain pending.
3. Local PATH presence does not prove tool startup, GUI availability, solver correctness, format fidelity or engineering validity.
4. License and pricing details must be refreshed against official upstream sources before procurement or distribution.
5. The current integration is additive; separate active lanes retain their ownership and source-of-truth boundaries.

## Verification commands

```sh
python3 -m ops.engineering.taxonomy validate
python3 scripts/engineering/toolchain_probe.py --json
python3 -m unittest discover -s tests -p 'test_engineering_taxonomy.py' -v
python3 -m unittest discover -s tests -p 'test_engineering_issue_template.py' -v
python3 -m unittest discover -s tests/hub_mcp -p 'test_protocol.py' -v
python3 scripts/ci/repo_gate.py
python3 scripts/ci/validate_siglary_mandate.py --base origin/master
python3 scripts/ci/termux_smoke.py
```

Record each command's actual exit status and exact commit SHA. Unavailable device or runner checks remain blocked, not passed.
