# Plan — enforce refTemplates and sMods contracts

**Work item:** IIS-002  
**Base:** master at b71b9c3ab60cc7cba72fd040715ffbba7c4f1776

## Outcome

Make the reusable template library and custom-fork lane enforceable across all
numbered template categories, without recursive submodule fetches or a second
integration registry.

## Tasks

1. Extend the inventory to discover reusable template children across numbered
   categories, preserving the existing research scoring fields.
2. Require nonempty regular README/SOURCE files for each template; require
   integration.json for every runtime integration template.
3. Validate sMods .gitmodules/gitlink parity, HTTPS URL hygiene, shallow pins,
   and exact immutable gitlink SHAs using local Git metadata only.
4. Require every implemented/native Integration Registry entry to adopt a
   concrete template or record a reasoned not_applicable disposition; planned
   integrations must make this choice before implementation.
5. Add focused regression tests for missing metadata, missing runtime manifest,
   orphan/duplicate pins, unsafe URLs, shallow policy, invalid SHAs, and missing
   integration-adoption dispositions.
6. Wire tests into the existing refTemplates evaluation workflow and update the
   workflow-hook, Integration Registry, and sMods documentation.
7. Run focused tests and repository gates; wait for same-head Actions evidence.

## Non-goals

- No recursive submodule initialization or upstream fetch.
- No pin advancement, fork creation, runtime installation, or deployment.
- No new registry, scheduler, or alternate adapter router.
- No claims of runtime compatibility from metadata alone.
