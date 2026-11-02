# Chat Provenance — session-history pipeline (owner requirement, 2026-11-01)

Pipeline owner: telemetry lane (`hindsight-provenance`). FULL chat
provenance {thinking steps · tool calls · outcomes, ∀ chats ∧
collaborators} feeds ForeSight · 3L0 · etc. as the **session-history**
source class (3L0 charter amendment, PR #3430).

## Canonical record — `chat-provenance/v1`

Feed: `ops/telemetry/session-history.jsonl` — append-only, emit-once
(`dispatch_id` unique), never rewritten; backfill doctrine applies
(re-scoring at method versions, records immutable).

| field | rule |
|---|---|
| `dispatch_id` | `sess:<chat_id>:<message_id>` (charter: session/chat id + turn anchor) |
| `origin` | `"session-history"` |
| `route` | `api-token` \| `apk` \| `webwrapper` |
| `actor` | attribution chain (stamp > trailer > manifest > git-author > app_bot), then surface default with evidence named; unknown ⇒ null, ¬ owner-default |
| `content` | full message/activity text, scrubbed (below) |
| `content_sha256` | over the scrubbed content as emitted |
| `thinking` | carried where the surface exposes it; Muse route = `WITHHELD_BY_PLATFORM` (platform withholds private reasoning by design — recorded, ¬ fabricated) |
| `tool_calls` | carried where the route exposes them; Muse DB route currently = `NOT_EXPOSED_BY_ROUTE` (tool-call tables read 0 through the export surface — recorded, ¬ zero-activity claim) |
| `outcome` | `{confirmed: null}` unless the record itself states an outcome (3L0 fold: observational until confirmed ≠ null) |

## Capture routes

- **API+TOKEN** — API-driven surfaces. Muse fleet: runtime DB export
  (messages ⋈ events.chat_context_json → chat_id), run lane-side on the
  Muse host (the DB is not reachable from Actions). Provider APIs with
  token access export the same row shape.
- **.APK endpoints** — on-device collaborators (Runable/DeepAgent
  class): the device-side endpoint emits export rows
  `{chat_id, message_id, role, ts, body, route:"apk", surface_actor,
  tool_events?}` to the lane; population starts when device lanes emit
  (their stabilization gates are theirs — contract is ready).
- **webWrappers** — web-surface collaborators (Grok/ChatGPT/GenSpark
  class): wrapper session exports land as row files in the same shape
  (`route:"webwrapper"`, surface_actor = collaborator) and are ingested
  identically; wrapper campaigns own capture, this pipeline owns
  transform + attribution + feed.

Emitter: `scripts/telemetry_ingest/session_history.py` (rows JSON →
records; `--feed` append, emit-once by dispatch_id, receipt written).

## Hard boundary — credentials

Credential VALUES never enter payloads. The emitter scrubs
secret-shaped values (GitHub PATs/tokens, `sk-*`, AKIA, JWTs, bearer
values, `key/token/secret/password = value`) to `[redacted:<kind>]`
BEFORE hashing or writing, and counts redactions per record. Secret
NAMES and refs are preserved — they are provenance, not credentials.

## Consumers

- **ForeSight** — canonical layer is open JSON/JSONL
  (FORESIGHT-IMPLEMENTATION-STATUS: "The canonical layer is open
  JSON/JSONL… surfaces are adapters/consumers"); this feed is the
  canonical event stream its next evidence gate #1 asks for (events
  from a real runtime). OTel/Langfuse/etc. project from it.
- **3L0** — `session_history.to_3l0()` maps records to
  `3l0-intake/v1` (origin session-history); fold stays observational
  until a record carries a confirmed outcome (3L0-PLANE charter).
- **DoE / others** — same feed, same mapping discipline.

## First population (2026-11-01)

API+TOKEN route, this lane's own chat (0b0272f1): **15 records**
(2026-10-28 → 2026-11-02), actors {owner, hindsight-provenance},
redactions 0, receipt `ops/telemetry/session-history-receipt.json`.
Fleet-wide expansion = repeat the DB export per chat (bounded,
per-chat emit-once), then APK/webWrapper rows as those lanes emit.
