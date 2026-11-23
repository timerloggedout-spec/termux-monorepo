---
id: spaceship-interaction-patterns
title: "Spaceship IDE interaction-pattern reference and cross-lane integration"
author: ChatGPT
posted_at: 2026-11-23
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: ChatGPT
    role: author+executor
    status: executing
related_prs: []
related_branches:
  - docs/spaceship-interaction-reference-20261123-v2
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — spaceship-interaction-patterns

## Summary

Register the four Spaceship IDE interaction concepts as a provenance-backed Tier-C design reference in `refTemplates/13_Third_Party_Refs/`, then connect the reference to the prompt/context, evaluation-quality, research-integration, ICM, DoE/MVT, and refTemplates Actions surfaces.

## Authorization and classification

- **Operator direction:** direct request on 2026-11-23 to add the designs to refTemplates and associate all relevant lanes.
- **Classification:** Tier C pattern-only; metadata-first; MIT; immutable source revision recorded.
- **Source finding:** the timerloggedout-spec fork and upstream master resolve to the same commit; local customization delta: none observed.
- **Execution boundary:** metadata, documentation, inventory validation, and tests. Source application code and media remain upstream.

## Acceptance

- [ ] `refTemplates/13_Third_Party_Refs/spaceship-ide/` contains README + SOURCE with MIT and exact-revision provenance.
- [ ] `07_Prompt_Context`, `11_Evaluation_Quality`, SOURCE-MAP, index, ICM reference inputs, and research integration docs link to the source.
- [ ] `refTemplates_inventory.py --strict` validates Tier-C child metadata; focused tests cover present and missing metadata.
- [ ] Tier-C stays outside the Tier-A score, 12-silo Delphi participant registry, and live `smods/` gitlinks.
- [ ] Proposal registry validation, repository gate, Termux smoke, and required PR checks pass on one immutable head SHA.

## Review log

| Date | Actor | Event | Evidence / disposition |
|---|---|---|---|
| 2026-11-23 | timerloggedout-spec | Operator direction | Direct request to add the design source to refTemplates and associate relevant lanes. |
| 2026-11-23 | ChatGPT | Recon and classification | Source README, design pages, LICENSE, fork metadata, and exact master revision inspected; source remains Tier C metadata-only. |

## Links

- [Work items](./ITEMS.md)
- [Source evidence](./source.md)
- [Integration record](../../../ops/SPACESHIP-IDE-DESIGN-INTEGRATION.md)
