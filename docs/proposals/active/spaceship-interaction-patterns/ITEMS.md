# ITEMS — spaceship-interaction-patterns

| ID | Item | Priority | Status | Owner | Evidence of completion | Dependencies |
|---|---|---|---|---|---|---|
| SPACESHIP-001 | Register Spaceship IDE as a Tier-C metadata-only reference with exact revision, upstream provenance, and MIT attribution. | P1 | executing | ChatGPT | `refTemplates/13_Third_Party_Refs/spaceship-ide/README.md` + `SOURCE.txt`; source and runtime boundaries recorded. | Operator direction |
| SPACESHIP-002 | Associate the four concepts with prompt/context, evaluation-quality, research integration, ICM, DoE/MVT, and refTemplates Actions inventory. | P1 | executing | ChatGPT | Category links, SOURCE-MAP, cross-lane integration note, inventory contract, and present/missing/whitespace-only metadata tests. | SPACESHIP-001 |
| SPACESHIP-003 | Validate proposal consistency, inventory metadata, documentation links, repository gates, and same-SHA PR checks. | P1 | pending | ChatGPT | Command output and terminal Actions evidence recorded against the final PR head SHA. | SPACESHIP-001, SPACESHIP-002 |

## Implementation constraints

Keep the source metadata-only. Preserve Tier-A research-template scoring and Delphi participant attribution. Keep live gitlink admission behind the existing custom-fork, compatibility, and dual-gate evidence requirements.
