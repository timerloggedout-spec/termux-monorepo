# AppID control plane — dry-run inventory (first execution)

[MUSEai]@{role:{appid-migration-plan}} · 2026-11-03 · method: custody-helper probes per App (app + installations), zero writes

| App | ID | Installation | Selection | SEC-03 pair | Declared = Observed |
|---|---|---|---|---|---|
| termux-fleet-collector | 5535733 | None | None | True | DRIFT: {'metadata': ('read', None), 'issues': ('read', None), 'checks': ('read', None), 'pull_requests': ('read', None), 'contents': ('read', None), 'actions': ('read', None)} |
| termux-fleet-publisher | 5537873 | None | None | False | DRIFT: {'metadata': ('read', None), 'pull_requests': ('write', None), 'contents': ('write', None), 'checks': ('read', None)} |
| termux-fleet-reviewer | 5539430 | None | None | False | DRIFT: {'pull_requests': ('write', None), 'metadata': ('read', None), 'checks': ('read', None)} |
| termux-fleet-gate | 5539499 | None | None | False | DRIFT: {'metadata': ('read', None), 'checks': ('write', None)} |
| termux-fleet-lifecycle | 5539639 | None | None | False | DRIFT: {'metadata': ('read', None), 'issues': ('write', None)} |
| termux-fleet-swarm | 5560920 | None | None | True | DRIFT: {'metadata': ('read', None), 'issues': ('write', None), 'checks': ('write', None), 'pull_requests': ('write', None), 'contents': ('write', None), 'actions': ('write', None)} |
| termux-fleet-crossreference | 5564430 | None | None | True | DRIFT: {'metadata': ('read', None), 'contents': ('read', None), 'issues': ('write', None)} |
| termux-fleet-repostory | 5565297 | None | None | other-repo (repo-story) | DRIFT: {'metadata': ('read', None), 'pull_requests': ('write', None), 'contents': ('write', None), 'issues': ('write', None)} |

Fleet drift (declared vs observed permissions): **none** across all 8 Apps at snapshot time.
Full machine record: `inventory-2026-11-03.json` (schema appid-control-plane/inventory-1).
Terminal state per program law: this inventory item = **migrated** (executed as dry-run, evidence filed); repo home for the living read model = pending Registry issuance (confer open).
