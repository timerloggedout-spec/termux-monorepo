# 🔱 Forge Oversight – Master Delegation

## Active Delegations
| Task | Agent | Account | Status | Sandbox |
|------|-------|---------|--------|---------|
| Token extraction automation | Scout | Secondary | 🟡 Spec drafted | `~/deepseek-cli/test-reports/` |
| Chronomancer fork execution | Chronomancer | Primary | 🟢 Ready | N/A |
| Pointer registry expansion | Linguist | Primary | 🟡 Spec drafted | `~/harmony_hub/workspace/linguist/` |
| ELO bidder wiring | Bidder | Primary | 🟡 Spec drafted | N/A |
| HTML dashboard skeleton | Orchestrator | Primary | ⚪ Queued | `~/harmony_hub/workspace/dashboard/` |

## Oversight Protocol
1. All agent outputs go to designated **sandboxes** – NEVER to production.
2. **Chronomancer** reviews `run_history` daily; forks if unverified > verified.
3. **Bidder** reads `run_history.validated` before placing wagers.
4. **Linguist** compresses all inter-agent messages via `cid.py`.
5. Promotion to production requires `--promote` flag with timestamped backup.

## State Summary (persistent)
Updated: $(date)
- Accounts: primary (orsW…), secondary (eE9t…) – verified
- Agents: Chronomancer, Linguist, Bidder specs drafted
- Utility Belt: verify-session, list-sessions, list-messages, find-fork-point
- Docs: Grimoire Dictionary, 1337 Profile, System Map
- Sprints: cli-synthegration/metrics/sprints.json
- run_history: validated column active, false positives flagged
