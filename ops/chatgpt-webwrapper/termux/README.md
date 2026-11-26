> **SUPERSEDED (2026-11-26) — v2 is the shape of record:** this Selenium bundle was the wrong shape (owner ruling: `deepcli/deepcli/core.py` is the shape — a session-layer driver, no browser binary). Use **termux2**: `ops/chatgpt-webwrapper/termux2/`. This v1 bundle is kept for the record only.

# ChatGPT webWrapper — Termux device instance

The fleet webWrapper stack (DeepAgent.py -> core.py model) running **on the
phone**: Selenium + Termux Chromium wrapping a ChatGPT participant session.
This is real fleet code on the device — not the Muse in-app browser. The
VM-local Playwright instance cannot pass the surface's managed challenge
(datacenter egress); the phone's own Chromium on the phone's own network
passes cleanly, so the session lives here.

webWrapper != API: participant primitives only (open, read visible text,
send). No API keys, no backend endpoints. Friction (captcha / account
warning / rate limit) stops the run with its class recorded — never evaded.

## Fetch (one line, in Termux)

```sh
curl -L "https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/master/ops/chatgpt-webwrapper/termux/termux-bundle.tar.gz" | tar xz -C "$HOME"
```

That URL is public — no credentials needed. It extracts to
`~/chatgpt-wrapper-termux/`. Nothing in the bundle writes outside that
dir. (Second copy, private backup repo:
`chatgpt-wrapper/termux/chatgpt-wrapper-termux.tar.gz` in
timerloggedout-spec/muse-vm-workspace-backup.)

## Run (one line, in Termux)

```sh
cd ~/chatgpt-wrapper-termux && ./run.sh
```

`run.sh` flow: `bootstrap.sh` if needed (detects Termux chromium +
chromedriver — if missing it prints `pkg install chromium` and stops;
pip-installs selenium + beautifulsoup4; runs the doctor) -> probe the
persistent profile -> if no session, **headed Chromium opens on the phone
screen and you perform the sign-in** (the participant step; the code never
enters credentials) -> once a session exists, `driver_se.py` harvests.

## What runs where

| Piece | Role |
|---|---|
| `core_se.py` | Selenium session core: persistent profile, friction taxonomy, participant primitives, `--doctor` / `--probe` / `--establish` |
| `driver_se.py` | Harvest driver: census-order capture -> `scrape/full/<id>.md`, checkpointed run state |
| `session_store.py` | Per-task session ids + run-state checkpoints (copied from the VM stack verbatim) |
| `dispatch_pipeline.py` | Save-hook fan-out (device copy reads `core_se`) |
| `telemetry.py` / `telemetry_export.py` | Entrypoint listener: `run_started` / `session_event` / `conversation_captured` / `friction_event` / `run_finished` -> `telemetry.jsonl` + Provenance-shaped `exports/` |
| `project.json` | The census of record (MonoRepo project, 417 chats) — bundle copy |
| `bootstrap.sh` / `run.sh` | Setup / single entrypoint |

## Immediate telemetry (owner ruling, 2026-11-26)

Telemetry fires from the entrypoint from the very first attempt — never
as an after-step and with no deferred/post-hoc mode. `run.sh` appends
`run_started` to `telemetry.jsonl` before bootstrap, probe, or session
establishment; establishment appends `session_event` / `friction_event`;
the harvest appends `conversation_captured` and closes with
`run_finished`. All events use the stack's existing `telemetry.py` shapes
(`{ts, stream, actor, event, ...}`, Provenance-shaped) and land in this
bundle's `telemetry.jsonl` + `exports/` on the device.

## No Gmail in this flow

No step depends on the owner reading Gmail, and no emailed code is
fetched or used anywhere. Sign-in verification rides the on-device
ChatGPT app / Google prompt path only — the owner approves on the phone
screen, in the headed Chromium window `run.sh` opens.

## Session-inheritance note

The session is born on this device, in this bundle's Chromium profile
(`~/chatgpt-wrapper-termux/profile/`), from the owner's own sign-in, and it
persists there across runs — later runs probe and reuse it, no re-login.
It is **never transplanted**: the VM instance keeps its own separate
profile, and no cookies or profile files move between the two instances
(the stack's standing rule). Captures stay on the device under
`scrape/full/` + `session_store/` + `telemetry.jsonl` until they are
carried back through the fleet's backup/export route.
