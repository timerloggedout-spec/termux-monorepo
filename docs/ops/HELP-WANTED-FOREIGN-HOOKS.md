# Help-wanted interthread + foreign signals

## Intended lane only

```text
scout ──optional──► help-wanted-execute
execute ──────────► help-wanted-followup (poll)
foreign POST ─────► same event types on THIS repo
```

| `event_type` | Workflow |
|--------------|----------|
| `help-wanted-execute` / `help-wanted-foreign-execute` | execute |
| `help-wanted-followup` / `help-wanted-foreign` / `help-wanted-changes-requested` | followup (poll only) |
| `help-wanted-scout` / `help-wanted-foreign-scout` | scout |

```bash
curl -X POST \
  -H "Authorization: Bearer $OPERATOR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/timerloggedout-spec/termux-monorepo/dispatches \
  -d '{"event_type":"help-wanted-followup","client_payload":{}}'
```

No special-case modes. No hard-coded foreign PR recipes in followup.

Agent-Identity: Grok (Administrator)
