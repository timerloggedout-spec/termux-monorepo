# 🧠 ArchWiz Learnings — v20260613
*Auto‑captured by the pipeline scribe. Tag #TIL to append.*

## Today I Learned (Session 417ddd6d)
- The listener must be fully detached (`start_new_session=True`) to survive cockpit restarts.
- `nohup` causes ghost messages in Termux; use `subprocess.Popen` with `stdout=DEVNULL` instead.
- Session cache JSON can be corrupted by partial writes; always validate before reading.
- The `ruff` binary installs faster via `pkg` than via `pip` on Termux.
- Multi‑pane code blocks need `# Pane N` markers for the listener to split correctly.
- The Mirror works best as an interactive gate, not a silent logger.
- Debug daemon should auto‑restart the listener on `termios` / `Inappropriate ioctl` errors.
- The TUI's `/browse` command with interactive toggles (A/T/H/P) is the right UX pattern.
- Language detection (`is_shell`) must cover common commands like `tail`, `head`, `wc`, `stat`.
