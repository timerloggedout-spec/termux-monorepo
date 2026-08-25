#!/usr/bin/env python3
import time
import os
import json
import sys
from datetime import datetime

try:
    from rich.console import Console, Group
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.text import Text
    from rich.box import ROUNDED
    _has_rich = True
except ImportError:
    _has_rich = False

TELEMETRY_LOG = "agent_telemetry_stream.json"
if _has_rich:
    console = Console()
else:
    console = None

# State-tracking cache and position pointers for incremental I/O performance optimization
_active_jobs_cache = {}
_sorted_telemetry_cache = None
_last_file_pos = 0
_last_file_ino = None
_last_file_mtime = 0

def read_latest_telemetry():
    """
    Optimized telemetry parser using state tracking, seek/tell incremental I/O,
    and sorted list caching to avoid redundant file reads and re-sorting during UI ticks.
    """
    global _last_file_pos, _active_jobs_cache, _sorted_telemetry_cache, _last_file_ino, _last_file_mtime
    if not os.path.exists(TELEMETRY_LOG):
        # Reset cache if file is missing
        _active_jobs_cache = {}
        _sorted_telemetry_cache = []
        _last_file_pos = 0
        _last_file_ino = None
        _last_file_mtime = 0
        return []

    try:
        stat_info = os.stat(TELEMETRY_LOG)
        file_size = stat_info.st_size
        file_ino = stat_info.st_ino
        file_mtime = stat_info.st_mtime

        # Fast-path return: if log file metadata matches previous read and sorted cache exists, return immediately
        if (_sorted_telemetry_cache is not None and
            file_size == _last_file_pos and
            file_mtime == _last_file_mtime and
            _last_file_ino is not None and
            _last_file_ino == file_ino):
            return _sorted_telemetry_cache

        # If file was truncated, recreated, or replaced, reset position and cache
        if (file_size < _last_file_pos or
            _last_file_ino is None or
            _last_file_ino != file_ino or
            file_mtime < _last_file_mtime):
            _active_jobs_cache = {}
            _sorted_telemetry_cache = None
            _last_file_pos = 0
            _last_file_ino = file_ino
            _last_file_mtime = file_mtime

        with open(TELEMETRY_LOG, "r") as f:
            if _last_file_pos > 0:
                f.seek(_last_file_pos)

            while True:
                curr_pos = f.tell()
                line = f.readline()
                if not line:
                    break
                # Torn append guard: check if line terminates with a newline character
                if not line.endswith("\n"):
                    # Seek back so this incomplete line can be fully read on the next tick
                    f.seek(curr_pos)
                    break

                # Commit offset up to the end of this complete line
                _last_file_pos = f.tell()

                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    target = entry.get("target") or "System"
                    _active_jobs_cache[target] = entry
                    _sorted_telemetry_cache = None
                except json.JSONDecodeError:
                    continue
    except Exception:
        # Fallback to returning current cache on file access or read errors
        pass

    # Sort by timestamp so the list ordering is consistent/predictable
    if _sorted_telemetry_cache is None:
        _sorted_telemetry_cache = sorted(_active_jobs_cache.values(), key=lambda x: x.get("timestamp", ""))
    return _sorted_telemetry_cache

def make_dashboard():
    # Read data
    jobs = read_latest_telemetry()

    # Header info
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header_text = Text()
    header_text.append("⚡ TERMUX MULTI-AGENT PARALLEL TELEMETRY ⚡\n", style="bold yellow")
    header_text.append(f"Last Sync: {now_str}  |  File: {TELEMETRY_LOG}", style="dim")

    header_panel = Panel(
        header_text,
        box=ROUNDED,
        border_style="yellow",
        expand=True,
    )

    if not jobs:
        # Beautiful empty state
        empty_text = Text()
        empty_text.append("\n[ Waiting for background agent pipelines to initialize... ]\n\n", style="italic cyan")
        empty_text.append("To start the multi-agent orchestration pipeline, run:\n", style="dim")
        empty_text.append("  ./run_agent.sh\n", style="bold green")
        empty_text.append("\nThis dashboard will automatically update once events are received.\n", style="dim")
        empty_text.append("Press Ctrl+C to exit.", style="dim red")

        body_panel = Panel(
            empty_text,
            title="System Status",
            box=ROUNDED,
            border_style="cyan",
            expand=True
        )
        return Panel(
            Group(
                header_panel,
                body_panel
            ),
            box=ROUNDED,
            border_style="dim"
        )

    # Beautiful table
    table = Table(box=ROUNDED, border_style="dim", expand=True)
    table.add_column("Target File", style="bold cyan", no_wrap=True)
    table.add_column("Agent", style="bold magenta")
    table.add_column("Try", justify="center", style="yellow")
    table.add_column("Status", justify="center")
    table.add_column("Last Message", style="white")
    table.add_column("Timestamp", style="dim", justify="right")

    for job in jobs:
        target = job.get("target") or "Global"
        # truncate long targets cleanly
        if len(target) > 25:
            target = "..." + target[-22:]

        agent = job.get("agent", "Unknown")
        attempt = str(job.get("attempt") or "-")
        level = job.get("level", "INFO")
        message = job.get("message", "")
        timestamp = job.get("timestamp", "")
        if timestamp:
            # Bolt Optimization: Fast-path string slice formatting for HH:MM:SS
            # Avoids datetime.strptime overhead in high-frequency dashboard rendering loops
            if len(timestamp) >= 19 and timestamp[10] in (" ", "T"):
                timestamp = timestamp[11:19]
            elif not (len(timestamp) == 8 and timestamp[2] == ":" and timestamp[5] == ":"):
                try:
                    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    timestamp = dt.strftime("%H:%M:%S")
                except ValueError:
                    pass

        # Beautiful styled status tag
        if level == "SUCCESS":
            status_str = Text("SUCCESS", style="bold green")
        elif level == "RETRY":
            status_str = Text("RETRYING", style="bold yellow")
        elif level == "CRITICAL":
            status_str = Text("CRITICAL", style="bold red")
        else:
            status_str = Text("PROCESSING", style="bold blue")

        table.add_row(
            target,
            agent,
            attempt,
            status_str,
            message,
            timestamp
        )

    footer_text = Text("\nPress Ctrl+C to exit Dashboard Viewer.", style="dim italic red")

    return Panel(
        Group(
            header_panel,
            table,
            footer_text
        ),
        box=ROUNDED,
        border_style="blue",
        title="Agent Live Monitor"
    )

def main():
    if not _has_rich:
        print("[ERROR] 'rich' library is required. Please run: pip install rich")
        sys.exit(1)
    try:
        # Use Live rendering for smooth, flicker-free updates
        with Live(make_dashboard(), refresh_per_second=1, screen=True) as live:
            while True:
                time.sleep(1.0)
                live.update(make_dashboard())
    except KeyboardInterrupt:
        # Clear screen and say goodbye gracefully
        if console:
            console.clear()
            console.print(Panel(
                "[bold green]Thank you for using Termux Multi-Agent Dashboard![/bold green]\n"
                "Stay productive and keep building! ⚡🚀",
                title="Exiting Dashboard",
                border_style="green",
                expand=False
            ))
        else:
            print("Thank you for using Termux Multi-Agent Dashboard!\nStay productive and keep building! ⚡🚀")

if __name__ == '__main__':
    main()
