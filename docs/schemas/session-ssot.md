# Session SSOT Schema

> **Status:** SPEC (P0 / elevated above TER-8)  
> **Goal:** One canonical session identity across deepcli, multi-ai, Codex, Colab, etc.

## Problem

The monorepo currently tries to synchronize multiple independent truths:

- `.deepcli`
- `.mistralai-cli` / multi-ai-cache
- `cli-synthegration`
- `codex_index`
- `archwiz`

That is a symptom. Do not keep six sources of truth.

## Canonical layout

```
~/.archwiz/
  sessions/
    <provider>/
      <account>/
        <session-id>/
          manifest.json
          messages.jsonl
          events.jsonl
          blobs/           # content-addressed optional
          index.json       # optional local search aid
  registry.json            # optional global index
```

On-device path may use `$PREFIX` / `$HOME` resolution; never hardcode
`/data/data/com.termux/...` in committed code.

## manifest.json

```json
{
  "schema_version": 1,
  "session_id": "uuid-or-provider-native-id",
  "provider": "deepcli",
  "account": "default",
  "created_at": "2026-08-02T00:00:00Z",
  "updated_at": "2026-08-02T00:00:00Z",
  "title": "optional human title",
  "native_refs": {
    "deepcli_path": "optional path into provider store",
    "codex_thread_id": null
  },
  "capabilities_used": ["streaming", "history"],
  "status": "active",
  "content_hash": "sha256-of-canonical-message-stream-or-null"
}
```

## messages.jsonl

One JSON object per line:

```json
{
  "message_id": "...",
  "role": "user|assistant|system|tool",
  "timestamp": "2026-08-02T00:00:00Z",
  "timestamp_source": "observed|recovered|generated|unknown",
  "content_hash": "sha256...",
  "content": "plaintext or structured",
  "provider_message_id": null,
  "provenance": {"source": "deepcli", "import_batch": null}
}
```

**Rule:** Never represent missing timestamps as `""`. Use `null` +
`timestamp_source`.

## events.jsonl

Event-sourced dispatch (Critical-Eval §15):

```json
{
  "event_id": "...",
  "timestamp": "...",
  "type": "SessionSaved|SessionForked|MessageSent|MessageReceived|SessionExported|CodeHarvested|IndexUpdated|ProviderFailed|ProviderRecovered",
  "provider": "...",
  "account": "...",
  "session_id": "...",
  "correlation_id": "...",
  "source": "archwiz|deepcli|multi-ai|manual",
  "payload_hash": "...",
  "schema_version": 1
}
```

## Provider adapter contract

Providers may retain native stores as **caches**. ArchWiz is the
cross-provider identity layer.

On `SessionSaved`:

1. Persist native store (provider responsibility).
2. Emit event (or write through ArchWiz adapter).
3. Upsert `manifest.json` + append `messages.jsonl` / `events.jsonl`.

Do **not** make `cache_save()` dynamically import dispatch pipelines
(PR #5 smell). Persist first; emit event; let a coordinator react.

## Migration notes

1. New sessions write SSOT from day one.
2. Existing provider stores: import scripts (offline) that never commit
   Class 3/4 artifacts into Git.
3. Gate already blocks new session_store paths in the index.

## Non-goals (this spec)

- Live multi-provider sync protocol
- Vector embeddings
- Full blob CAS implementation (separate proposal)
