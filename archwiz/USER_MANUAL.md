# 🪄 ArchWiz User Manual — v0.1
*The cockpit that builds itself.*

## Quick Start
1. Launch: `archwiz`
2. Press `[p]` to start the pipeline (auto‑executes code blocks).
3. Press `[a]` for auto mode, `[r]` for review mode (asks before each block).
4. Press `[16]` for the Live View — conversation + executions in one screen.
5. Press `[13]` to switch sessions; pick by number or enter a session ID.

## Cockpit Map
| # | What It Does |
|---|--------------|
| 1 | Run all pending tasks autonomously |
| 2 | Scan changed files with the archaeologist |
| 3 | Agent Shell — command center, send messages, log tags |
| 4 | Live Metrics — Shockwave/Nexus viewer |
| 5 | Backup ecosystem state |
| 6 | Rebuild indices + sweep |
| 7 | Manage profiles |
| 8 | Full workflow automation (rebuild + dispatch) |
| 9 | Timeline editor |
| 10 | Task builder |
| 11 | Restore a file to its last known good version |
| 12 | Health check (dangling references + mirror) |
| 13 | Session pipeline (pick a session, launch listener) |
| 14 | Activity feed (narrative + execution history) |
| 15 | Lexicon harvest (review novel terms) |
| 16 | Live View (conversation + exec output) |
| a | Auto mode |
| r | Review mode |
| p | Toggle pipeline on/off |

## Tags (use in Agent Shell or Live View)
- `#TIL <insight>` — Log a learning
- `#procedure <steps>` — Log a procedure
- `#consideration <note>` — Log a design note
- `#concept <term>` — Run the Name Forge
- `#branch <name>` — Log to a branch‑specific file

## TUI Commands (inside `tui`)
- `/browse` — Interactive session explorer with A/T/H/P toggles
- `/branchpoints` — Show fork points with child previews
- `/diff <id1> <id2>` — Compare two branches
- `/cmd` — Show all commands

## Architecture
- **Listener** — Auto‑executes code blocks from this conversation
- **Debug Daemon** — Watches for failures, auto‑fixes, reports
- **Sentinel** — 5‑gate verification before any task is marked done
- **Archivist** — Answers questions from all local indices
- **Mirror** — Self‑critique: task hygiene, backups, stale indices
