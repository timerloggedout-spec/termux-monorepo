# Quota TUI — termux-monorepo

A working terminal renderer for the quota panel, using the same shared
source as the web panel (`apps/help-wanted-dashboard/quota.html`):

| Role | Schema | Master path | Local copy used here |
|---|---|---|---|
| Registry (ALL services + documented entitlements) | `3l0.quota-registry.v1` | `ops/quota/registry.json` | `../quota_registry.json` |
| Readings (live/reported status, sparse) | `3l0.quota-readings.v1` | `apps/help-wanted-dashboard/data/quota.json` (= `docs/ops/generated/quota-status.json`) | `../quota-panel/quota.json` |

Current data (2026-10-20): **26 registry services, 3 readings**
(`vercel.deployments` = cap_tripped, `openrouter.free_models` = exhausted,
`github.actions.minutes` = watch).

## Stack choice — and why

Named candidates were ratatui (Rust) and LipGloss (Go). Checked on this
machine (2026-10-20):

- `go` — not installed
- `cargo`/`rustc` — not installed
- `python3` 3.12 — installed; `rich` / `textual` — **not** installed;
  stdlib `curses` present

**Chosen: zero-dependency Python 3 (stdlib only) ANSI renderer.**

1. It runs *today*, with no toolchain install and no pip installs.
2. It runs where this panel matters most — **Termux on Android** —
   which ships Python, not a Go/Rust build chain.
3. The TUI is a read-only view of a JSON file; it needs text layout,
   colour, and wrapping, all of which stdlib does fine. If a Go +
   LipGloss or Rust + ratatui port is wanted later, `quota_tui.py`'s
   data-merging behaviour (below) is the spec to port against.

## Behaviour (the contract that matters)

- **All services render.** Registry services are grouped by provider;
  readings with no registry entry are still shown, never dropped.
  Input may be a readings file, a registry file, or a merged file with
  both `services` and `readings`; a registry is auto-discovered next to
  a readings-only input (explicit `--registry PATH` overrides).
- **Never invent a balance.** Documented limits are labelled
  `limit (documented):` — entitlements, not balances. A `used` value is
  printed only when a reading actually carries a non-null `used`.
  Every current reading has `used: null`, so the output shows
  `No live reading` / “status reported, no used value” instead — and
  contains no `remaining` figure anywhere.
- **Alerts first, highlighted.** `cap_tripped` / `exhausted` render as
  bold white-on-red `[!! CAP TRIPPED]` / `[!! EXHAUSTED]`, `watch` in
  bold yellow, in an ALERTS section above the full list.
- **Phone-width.** Rendering wraps at the terminal width, capped at
  80 columns by default (`--width N` overrides; verified clean at 60).
- **Colour only on a TTY.** Piped/redirected output is plain text
  (`--no-color` / `NO_COLOR` also honoured), so captures stay readable.

## Usage

```sh
# auto-discover readings + registry (workspace / repo layout)
python3 quota_tui.py --once

# explicit files
python3 quota_tui.py --once ../quota-panel/quota.json \
    --registry ../quota_registry.json

# interactive (TTY only): refreshes every 30s, reloads the JSON
# each frame, q / Ctrl-C to quit; --interval N to change cadence
python3 quota_tui.py
```

`--once` prints one frame and exits — used for testing and for
generating `sample-output.txt`.

## Verification (2026-10-20)

```sh
python3 quota_tui.py --once ../quota-panel/quota.json > sample-output.txt
```

- Exit 0; **26 / 26 registry services present** in the output
  (checked programmatically against `quota_registry.json`, none missing)
- 3 alerts present: CAP TRIPPED, EXHAUSTED, WATCH
- Max line length 80; also clean at `--width 60`
- No invented balances: no `live reading: used …`, no `remaining`
- ANSI colour + red alert highlight confirmed under a real PTY
  (`script -qec …`); piped output is colour-free
- Readings-only input renders its 3 services; a bad `--registry`
  path warns on stderr instead of crashing

## Files

- `quota_tui.py` — the renderer (stdlib only, executable)
- `sample-output.txt` — verified `--once` output against the real data
- `README.md` — this file

Not committed to the repo — staged here for review first.
