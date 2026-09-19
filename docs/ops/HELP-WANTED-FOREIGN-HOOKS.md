# Help-wanted foreign hooks + interthread

## Interthread (already in-repo)

```text
scout ──(optional chain_execute)──► repository_dispatch:help-wanted-execute
execute (always after contribute)──► repository_dispatch:help-wanted-followup mode=poll
followup chain-execute ───────────► workflow_dispatch execute
```

| Event type | Workflow |
|------------|----------|
| `help-wanted-execute` | execute |
| `help-wanted-foreign-execute` | execute |
| `help-wanted-followup` | followup |
| `help-wanted-foreign` | followup |
| `help-wanted-changes-requested` | followup |
| `help-wanted-scout` | scout |
| `help-wanted-foreign-scout` | scout |

### POST foreign signal into monorepo

```bash
curl -X POST \
  -H "Authorization: Bearer $OPERATOR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/timerloggedout-spec/termux-monorepo/dispatches \
  -d '{"event_type":"help-wanted-changes-requested","client_payload":{"mode":"poll","pr":"https://github.com/vedantnimbarte/zero/pull/81"}}'
```

## True foreign webhooks (App install)

GitHub does **not** deliver `pull_request_review` events from `vedantnimbarte/zero` into **our** Actions unless:

1. A **GitHub App** is installed on the foreign repo (or org) and routes webhooks to us, or
2. We poll (schedule `*/2h`) — **already live**.

ECC Tools / OPERATOR App path: prefer install on high-value mutual targets; until then `repository_dispatch` + schedule is the interthread.

## Cadence

| Workflow | Cron |
|----------|------|
| scout | `17 */2 * * *` |
| followup | `17 */2 * * *` |
| execute | `41 */4 * * *` |

Agent-Identity: Grok (Administrator)
