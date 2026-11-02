# Help-wanted interthread + foreign signals

## Intended lane only

```text
scout ──optional──► tribute-execute
execute ──────────► tribute-followup (poll)
foreign POST ─────► same event types on THIS repo
```

| `event_type` | Workflow |
|--------------|----------|
| `tribute-execute` / `tribute-foreign-execute` | execute |
| `tribute-followup` / `tribute-foreign` / `tribute-changes-requested` | followup (poll only) |
| `help-wanted-scout` / `tribute-foreign-scout` | scout |

```bash
curl -X POST \
  -H "Authorization: Bearer $OPERATOR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/timerloggedout-spec/termux-monorepo/dispatches \
  -d '{"event_type":"tribute-followup","client_payload":{}}'
```

No special-case modes. No hard-coded foreign PR recipes in followup.

Agent-Identity: Grok (Administrator)
