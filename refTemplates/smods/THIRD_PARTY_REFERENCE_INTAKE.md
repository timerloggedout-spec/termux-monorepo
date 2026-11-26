# Third-party reference intake — sMods bridge

This file makes the third-party radar visible from the sMods integration surface without falsely treating research candidates as live submodules.

## Current candidates

The canonical source records and machine-readable pre-adoption dispositions are maintained in:

- refTemplates/13_Third_Party_Refs/open-source-radar-2026-11-15/README.md
- refTemplates/13_Third_Party_Refs/open-source-radar-2026-11-15/SOURCE.txt
- refTemplates/13_Third_Party_Refs/open-source-radar-2026-11-15/smods-disposition.json

Registered candidates:

1. alibaba-open-code-review — research_only
2. chrome-devtools-mcp — research_only
3. ag-ui — research_only
4. univer-office-sdk — research_only

## Promotion rule

When a candidate is selected for actual repository use:

- If consumed as an upstream package, API, or adapter without repository-owned source changes, record the concrete integration/version in its owning component. Do not create a submodule merely for tracking.
- If repository-owned changes are required, add a matching reference_candidates entry to the canonical INTEGRATIONS.json with status fork_required, an explicit planned sMods path, and the fork URL. This is not yet a gitlink.
- Change to pinned only after the user-owned fork exists, its immutable commit SHA is recorded, .gitmodules points to the exact fork URL, a 160000 gitlink exists at the declared path, license/provenance is reviewed, and dual-gate evidence passes.

A research_only entry must never imply that a dependency is installed, a fork exists, or a runtime is validated. The offline intake validator enforces this distinction.
