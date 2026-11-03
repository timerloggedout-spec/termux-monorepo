# AppID control plane — dry-run inventory (first execution)

[MUSEai]@{role:{appid-migration-plan}} · 2026-11-03 · method: custody-helper probes per App (app + installations), zero writes

| App | ID | Installation | Selection | SEC-03 pair | Declared = Observed |
|---|---|---|---|---|---|
| termux-fleet-collector | 5535733 | 176747357 | selected | True | YES |
| termux-fleet-publisher | 5537873 | 176799777 | selected | False | YES |
| termux-fleet-reviewer | 5539430 | 176838378 | selected | False | YES |
| termux-fleet-gate | 5539499 | 176839926 | selected | False | YES |
| termux-fleet-lifecycle | 5539639 | 176843209 | selected | False | YES |
| termux-fleet-swarm | 5560920 | 177357774 | selected | True | YES |
| termux-fleet-crossreference | 5564430 | 177439462 | selected | True | YES |
| termux-fleet-repostory | 5565297 | 177463385 | selected | other-repo (repo-story) | YES |

Fleet drift (declared vs observed permissions): **none**.
Full machine record: `inventory-2026-11-03.json` (schema appid-control-plane/inventory-1).
Terminal state per program law: this inventory item = **migrated** (executed as dry-run, evidence filed); repo home for the living read model = pending Registry issuance (confer open).
