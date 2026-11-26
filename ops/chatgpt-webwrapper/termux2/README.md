# ChatGPT webWrapper — Termux device instance (v2)

The fleet webWrapper stack running **on the phone**, in the shape of
record: `deepcli/deepcli/core.py` — a wrapped-session driver (persistent
session carrying the participant's own cookies, per-conversation session
cache on disk, save-hook dispatch fan-out, `[{role, content}]` / markdown
export shapes). **No browser binary, no Selenium, no chromedriver** —
the session layer is the whole driver. (v1, the Selenium port under
`ops/chatgpt-webwrapper/termux/`, is SUPERSEDED: wrong shape. On this
device no chromedriver package exists and the Termux `chromium` package
is a 967 MB X11 tree — neither is needed here.)

Zero installs: v2 runs on the Python stdlib floor. Its HTTP ladder uses
curl_cffi or requests opportunistically when present and falls back to a
stdlib session when neither is — `pkg`/`pip` are never invoked.

webWrapper != API key: the driver acts through the owner's own signed-in
web session. The code never sees a password and never enters
credentials. Friction (captcha / security check, account warning, rate
limit) stops the run with its class recorded — never evaded. No step
depends on the owner reading Gmail; there is no emailed-code fetch
anywhere in this bundle.

## Fetch (one line, in Termux)

```sh
mkdir -p ~/chatgpt-webwrapper2 && cd ~/chatgpt-webwrapper2 && curl -sL https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/master/ops/chatgpt-webwrapper/termux2/termux2-bundle.tar.gz | tar xz && ls
```

That URL is public — no credentials needed. The tarball is flat; the
files land in `~/chatgpt-webwrapper2/`. (Second copy, private backup
repo: `chatgpt-wrapper/termux2/chatgpt-wrapper-termux2.tar.gz` in
timerloggedout-spec/muse-vm-workspace-backup.)

## One-time setup on the device (two credentials, both owner-held)

1. **ChatGPT session (ADB import, primary)** — sign in to ChatGPT in
   the phone's **Chrome** yourself, then import the established
   session over ADB:

   ```sh
   cd ~/chatgpt-webwrapper2 && ./run.sh import-session
   ```

   Prerequisites (already true on this device): wireless debugging
   enabled, and the Termux `adb` transport showing the phone itself in
   state `device` (ShizukuPlus keeps this up). The import walks a
   preflight ladder — adb binary → transport → Chrome DevTools socket —
   classes each failure before reading anything, freezes the adb
   target for the run, forwards `localabstract:chrome_devtools_remote`,
   reads the chatgpt.com cookies over CDP (stdlib websocket client,
   zero installs), reassembles the NextAuth session token (it is
   chunked across `__Secure-next-auth.session-token.0/.1/...` when
   oversized), and stores token + cookie header in
   `~/.chatgpt-webwrapper/config.json` (dir 0700, file 0600). The
   value moves only from the browser surface into that config — never
   printed, logged, or traced. Every step is recorded in a step-trace
   (`~/.chatgpt-webwrapper/import-traces/<id>.json`, 0600) and in the
   telemetry stream; the import is single-flighted by a PID-aware
   lock. Exit codes: 0 stored + verified · 2 stored, surface reports
   logged out · 3 friction at verify (stop, never evaded) · 4 browser
   side not ready (the import opens ChatGPT in Chrome via adb — sign
   in there, keep Chrome foregrounded, re-run) · 5 import failure /
   another import in progress.

   **Manual fallback** — `./run.sh import-session` falls back to it
   automatically when adb or its transport is absent, or force it
   with `python3 core.py --import-session --manual`: it prompts
   (hidden input) for the `__Secure-next-auth.session-token` cookie
   value and stores it in the same 0600 config. The env var
   `CHATGPT_SESSION_TOKEN` overrides the config either way. When the
   session expires, the driver reports `no_session` — sign in again
   and re-import.

2. **GitHub streaming token** — captures stream straight to GitHub, so
   the sink needs a credential **the owner provisions once on the
   device**. The bundle contains NO fleet token and never will. Create
   a fine-grained personal access token scoped to
   `timerloggedout-spec/muse-vm-workspace-backup` (Contents: write),
   then on the device:

   ```sh
   export WEBWRAPPER_GH_TOKEN=<the token>   # or key gh_token in the 0600 config
   ```

   **Dry mode:** with no token set, the driver is fully functional —
   every capture lands in the bundle-local `outbox/` instead of being
   pushed, and a later run with the token set flushes the outbox
   automatically (or `./run.sh flush`).

## Run (one line, in Termux)

```sh
cd ~/chatgpt-webwrapper2 && ./run.sh
```

Flow: telemetry `run_started` fires first (entrypoint, before anything)
-> outbox flush -> session check (`no_session` stops cleanly) -> the
MonoRepo project's conversations are enumerated at the session layer
(census of record: 417 chats, `project.json`) -> each conversation is
captured in surface order, checkpointed in the session store after
EVERY conversation (a rerun resumes by skipping completed ids), and
streamed to the backup repo at
`chatgpt-harvest/<project_id>/<conversation_id>.md` (+ the
`[{role, content}]` JSON under `sessions/`). The device keeps only
small cache: `~/.chatgpt-webwrapper/` (config + session cache), the
bundle's session-store run state, `exports/` telemetry records, and
the outbox.

Checks: `./run.sh doctor` (environment + credential presence + cache
counts — values never printed) · `./run.sh probe` (session state as
the surface reports it).

## What runs where

| Piece | Role |
|---|---|
| `core.py` | Session core in the deepcli shape: HTTP ladder, cookie/token session, session cache + dispatch hook, friction taxonomy, participant read primitives, export shapes, `--doctor` / `--probe` / `--import-session` (ADB-primary, manual fallback) |
| `driver.py` | Harvest driver: census-order capture, per-conversation checkpoint, stop-on-friction |
| `sink.py` | Streaming GitHub sink (Contents API) + outbox dry mode |
| `session_store.py` | Per-task session ids + run-state checkpoints (stack shape, verbatim) |
| `dispatch_pipeline.py` | Save-hook fan-out (stack shape, verbatim) |
| `telemetry.py` / `telemetry_export.py` | Entrypoint listener + Provenance-shaped export records (stack shapes, verbatim) |
| `project.json` | Census of record (MonoRepo project, 417 chats) |
| `run.sh` | Single entrypoint; telemetry `run_started` before anything else |

## Immediate telemetry (owner ruling, 2026-11-26)

Telemetry fires from the entrypoint from the very first attempt — never
as an after-step, no deferred mode. `run.sh` appends `run_started`
before the driver starts; the driver appends its own `run_started`,
then `session_event` / `conversation_captured` / `friction_event`, and
closes with `run_finished`, all in the stack's `telemetry.py` shapes
(`{ts, stream, actor, event, ...}`), actor `termux-device`. When the
sink credential exists, the telemetry artifacts stream to
`chatgpt-harvest/<project_id>/telemetry/` at run end.

## Patterns adopted from google/artemis

The import leg's reliability discipline comes from Google's ARTEMIS
(`timerloggedout-spec/artemis_fork` ← `google/artemis`), mined
2026-11-26 and fitted to a single-device bundle:

- **Atomic trace writes** (`runtime/trace_store.py`): temp file +
  fsync + `os.replace`; corrupt state is quarantined aside, never
  silently trusted. Used for the import step-trace and the import
  lock — load-bearing on a 95%-full disk.
- **Sessions as ordered step records** (admin-console session/step
  repositories): one import session owns its steps; terminal statuses
  are canonical (`completed` / `failed` / `stopped`); liveness that
  cannot be determined counts as alive, so a live import is never
  displaced by the lock.
- **ADB target as an immutable snapshot** (`runtime/adb_endpoint.py`):
  endpoint + serial are frozen at import start; every adb call in the
  run uses exactly that target; malformed values fail precisely.
- **Blocker-class preflight probe** (`core/diagnostics/probes/adb_probe.py`):
  rungs in order — adb binary → transport → devtools socket — each
  failure classed before any session read; enrichment cached briefly.
- **Replayable trace** (`telemetry/replay.py`): the import's steps are
  recorded end-to-end (trace file + telemetry stream) so the one
  credential-adjacent operation stays auditable — steps always,
  values never.

Left behind, deliberately: artemis's cross-process device-lock FIFO
queue, MCP server, admin console, device pool, and UI/coordinate
targeting — server and UI-automation machinery with no surface on a
single-phone CLI bundle that reads the session over CDP and never
drives UI.

## Shape deviations (surface-forced, named)

- **Credential leg:** DeepSeek's core takes a bearer token; this
  surface's web session is cookie-based (NextAuth), so the leg is a
  session cookie + the access token the surface's own session endpoint
  returns — same env-first / 0600-config custody.
- **PoW leg:** DeepSeek's core solves the surface's proof-of-work for
  gated calls. v2 solves nothing: the harvest is read-only under an
  already-established participant session, and a fresh challenge demand
  is friction (stop).
- **Send leg:** no send primitive ships — sending on this surface
  requires its sentinel/PoW flow. v2's participant primitives are the
  read set (session state, enumerate, fetch, export).
- **Enumeration:** the project page's embedded payload is merged with
  the surface's conversation list (project-filtered when the item
  carries its association), because this surface exposes no single
  project-list read shaped like the model's `fetch_page`.
