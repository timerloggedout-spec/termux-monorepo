# VM Webhooks — Receiver Mesh VM leg (bounded intake)

Status: LANDED 2026-10-30 (owner order via main). Extends the Receiver Mesh
design of record (`docs/ops/RECEIVER-MESH.md`, PR #2345) — it does not
duplicate it: the Cloudflare Worker stays the public edge intake, Actions
stays the processor, Neon stays the durable ledger. This leg adds the
VM-local intake surface the AI Studio mesh VM trigger leg precedent
(owner-ruled 2026-10-30, part of the mesh) established: a bounded,
session-scoped receiver where a local session lives.

## ⚠ Scope flag (read first)

The VM rule (2026-10-28) is sandbox-only and the Receiver Mesh doc says
"any standing VM listener remains out of scope". This implementation
stays inside a bounded trigger/intake role:

- intake ONLY: verify → dedupe → append allowlisted envelope to the
  durable log. No business logic, no commits, no dispatch, no processing.
- NO daemon: no systemd unit, no cron, no auto-restart. The process runs
  only while launched in a session and dies with the session/VM.
- Loopback only (`127.0.0.1`). Any public exposure, tunnel, or standing
  hosting EXCEEDS this scope and needs its own owner ruling — flagged
  here, not taken.

## Endpoints (local, port `VM_WEBHOOK_PORT`, default 8791)

| Route | Behavior |
|---|---|
| `GET /health` | `200 {"status":"ok","surface":"vm-webhook-intake","logged":N}` |
| `POST /webhook/<source>` | HMAC verify → normalize → dedupe → log. `202` new, `200` duplicate, `401` bad signature, `400` missing delivery_id/event or invalid JSON |

Verification: `X-Hub-Signature-256: sha256=<hmac-sha256(raw body,
VM_WEBHOOK_SECRET)>` (timing-safe compare; `X-Receiver-Signature`
accepted as alias). Delivery id: `X-GitHub-Delivery` header or
`delivery_id` in the body. Payload discipline = the Receiver Mesh
allowlisted envelope only (`source, event, delivery_id, received_at,
repo, action, actor, object_id`) — raw payloads are never logged or
forwarded, credentials never accepted as payload fields.

Durable intake log: append-only JSONL, fsync per record, dedupe state
rebuilt from the log on startup (survives process restart):
`~/workspace/vm-webhooks/intake.jsonl` (override `VM_WEBHOOK_LOG`).
Code: `ops/receiver-mesh/vm/vm_webhook_receiver.py` (stdlib only).
Tests: `tests/test_vm_webhook_receiver.py` (3 offline tests).

Run: `VM_WEBHOOK_SECRET=<local value> python3 ops/receiver-mesh/vm/vm_webhook_receiver.py`

## Proof (firsthand, 2026-10-30, this VM)

- `GET /health` → ok, `logged: 0`
- signed `POST /webhook/vm-proof` (delivery `vm-proof-20261030-001`) → `202 accepted`
- same delivery again → `200 duplicate:true` (dedupe via durable log)
- bad signature → `401 bad_signature`
- log holds exactly 1 allowlisted envelope; the test payload's `raw`
  field is absent (allowlist verified in the landed record)

## Provider registration

Registered in the fleet Provider Model (`ops/quota/registry.json`,
the 88-model-provider registry of record) so provider-dispatch can
route bounded trigger/intake tasks to this surface:

- `fleet.vm_webhooks` (provider `fleet-vm`, lane `ops`) — this surface.
  Secret name: `VM_WEBHOOK_SECRET` (local 0600 custody on the VM;
  value never in chat, files, or commits).

## Meta ∧ Muse — official API routes (findings, 2026-10-30)

### Meta Model API — the proper route (wired)
- Base: `https://api.meta.ai/v1`; auth `Authorization: Bearer $MODEL_API_KEY`
  (key from the Meta Model API dashboard). OpenAI-SDK drop-in + Anthropic
  Messages format. Surfaces: `POST /responses` (recommended), `POST
  /chat/completions`, `POST /messages`, Files API, structured output,
  parallel tool calling, prompt caching, realtime ASR
  `wss://api.meta.ai/v1/asr/realtime`.
- Models: `muse-spark-1.3` (+ `-contributor` tier), `muse-spark-1.1`,
  `muse-wonder-1.0`, `muse-voice-transcribe-1.0`. Public preview
  (US-only at the 1.1 launch 2026-07-09; $20 starter credit;
  muse-spark-1.1 documented at $1.25 / $4.25 per M in/out tokens).
  No published rate-limit counter established → registry `limit: null`,
  never invent a balance.
- Sources: Meta launch post (ai.meta.com/blog/introducing-muse-spark-meta-model-api/);
  endpoint/key corroboration via Promptfoo + LiteLLM provider docs
  (both cite Meta's dev.meta.ai docs).
- Wired: registry `meta.model_api` + `.github/connectors/llm_providers.yaml`
  `meta_model_api` (`enabled:false` until `MODEL_API_KEY` is provisioned —
  owner provisioning item, names-only).

### Muse Code — code-assist surface (wired)
- Meta's terminal coding agent (binary `muse`), backed by Muse Spark.
  Install: `curl -fsSL https://dev.meta.ai/install.sh | bash`
  (Windows: `install.ps1`). Official page: developer.meta.com/ai/products/muse-code
  (subscription from $5/mo shown there).
- Auth: first run = browser sign-in at dev.meta.ai; headless/CI =
  `META_API_KEY` env or `muse auth set` (keys billed to the Meta Model
  API account). Agent CLIs can also point at the Model API directly
  (OpenAI Responses or Anthropic Messages format; e.g.
  `ANTHROPIC_BASE_URL=https://api.meta.ai`).
- Wired: registry `meta.muse_code` + `llm_providers.yaml` `muse_code`
  (`enabled:false` until the owner takes the sign-in/key step).

### Retired / no-API surfaces (recorded, not routed)
- Llama API (`https://api.llama.com/compat/v1/`, `LLAMA_API_KEY`,
  waitlist/US-only) — RETIRED 2026-07-06, superseded by the Meta Model
  API. Registry record `meta.llama_api` exists with `limit: 0` +
  DO-NOT-ROUTE note only. Llama models keep routing via existing host
  providers.
- Meta AI consumer (meta.ai / Meta AI app) — no separate developer API
  established; developer access to the same Muse models is the Meta
  Model API above (consumer "Thinking" mode is not an API route).
- `g4f/MetaAI` records already in the registry are unofficial web routes
  and stay distinct from these official Meta records.

## Provisioning items (owner, names-only)

- `MODEL_API_KEY` — Meta Model API dashboard key → enables `meta.model_api`.
- `META_API_KEY` — same account, Muse Code headless auth name.
- `VM_WEBHOOK_SECRET` — done locally (VM 0600 file) for the proof above;
  repo/Actions custody is a separate owner item if the leg ever forwards.
