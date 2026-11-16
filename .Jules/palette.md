## 2026-08-01 - Flicker-Free Real-Time CLI Dashboards with Rich Live
**Learning:** Terminal dashboards that clear the screen using raw ANSI escape codes (`\033[H\033[J`) or `clear` commands create severe flicker and redraw lag. This harms cognitive accessibility and visual appeal. Using `rich.live.Live` with high-level structural layout (`Table`, `Panel`, `Text`) ensures updates are drawn to the screen differential/flicker-free, and handles terminal exits cleanly.
**Action:** Always prefer `rich.live.Live` (or similar differential-updating curses-like tools) for terminal UI dashboards that require frequent, real-time telemetry updates.

## 2026-10-06 - Responsive ANSI Panel Boundaries for Mobile Termux Viewports
**Learning:** Hardcoding fixed-width panel borders (e.g. 88 columns) or multi-line wide ASCII logo banners causes horizontal text wrapping and broken panel borders on compact mobile terminal screens (e.g. Termux on BLU B160V, ~60-80 columns). Deleting extraneous ASCII banner art and calculating panel width dynamically using `shutil.get_terminal_size()` prevents layout distortion.
**Action:** In CLI/TUI tools targeting Termux or mobile terminals, derive panel widths dynamically via `shutil.get_terminal_size()` capped to maximum screen width, and avoid hardcoded wide ASCII art banners.
