# Session SSOT Schema

> **Status:** SPEC (P0)

## Canonical layout

```
~/.archwiz/sessions/<provider>/<account>/<session-id>/
  manifest.json
  messages.jsonl
  events.jsonl
  blobs/
```

Providers may retain native stores as caches. ArchWiz is the cross-provider identity layer.

Never hardcode `/data/data/com.termux/...` in committed code.
Never represent missing timestamps as `""` — use `null` + `timestamp_source`.

See master-staging for full JSON field definitions.
