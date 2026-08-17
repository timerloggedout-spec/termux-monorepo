#!/usr/bin/env python3
import time
import os
import json
import sys
import requests
from datetime import datetime
from pathlib import Path

try:
    from rich.console import Console, Group
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.text import Text
    from rich.box import ROUNDED
except ImportError:
    # Clean fallback warning
    print("[ERROR] 'rich' library is required. Please run: pip install rich")
    sys.exit(1)

TELEMETRY_LOG = "agent_telemetry_stream.json"
console = Console()

def check_infrastructure():
    infra = {}
    
    # Hub Status
    hub_url = os.environ.get("LLM_API_HUB_BASE", "http://127.0.0.1:8787/v1").replace("/v1", "/health")
    try:
        resp = requests.get(hub_url, timeout=0.5)
        if resp.status_code == 200:
            infra["Hub"] = ("ONLINE", "green")
        else:
            infra["Hub"] = ("ERROR", "red")
    except:
        infra["Hub"] = ("OFFLINE", "dim red")

    # ML Ingestion Status
    ml_latest = Path("/home/ubuntu/termux-monorepo/data/ml_ingestion/latest.json")
    if ml_latest.exists():
        try:
            with open(ml_latest, "r") as f:
                data = json.load(f)
                ts = data.get("timestamp", "unknown")
                infra["ML Pipeline"] = (f"READY ({ts})", "green")
        except:
            infra["ML Pipeline"] = ("CORRUPT", "red")
    else:
        infra["ML Pipeline"] = ("NO DATA", "dim yellow")
        
    return infra

def read_latest_telemetry():
    if not os.path.exists(TELEMETRY_LOG):
        return []
    active_jobs = {}
    try:
        with open(TELEMETRY_LOG, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    target = entry.get("target") or "System"
                    active_jobs[target] = entry
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    # Sort by timestamp so the list ordering is consistent/predictable
    return sorted(active_jobs.values(), key=lambda x: x.get("timestamp", ""))

def make_dashboard():
    # Read data
    jobs = read_latest_telemetry()
    infra = check_infrastructure()

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

    # Infra Panel
    infra_text = Text()
    for name, (status, color) in infra.items():
        infra_text.append(f"{name}: ", style="bold")
        infra_text.append(f"{status}  ", style=color)
    
    infra_panel = Panel(
        infra_text,
        title="Infrastructure Status",
        box=ROUNDED,
        border_style="blue",
        expand=True
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
                infra_panel,
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
            # Format time if it has full date/time
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
            infra_panel,
            table,
            footer_text
        ),
        box=ROUNDED,
        border_style="blue",
        title="Agent Live Monitor"
    )

def main():
    try:
        # Use Live rendering for smooth, flicker-free updates
        with Live(make_dashboard(), refresh_per_second=1, screen=True) as live:
            while True:
                time.sleep(1.0)
                live.update(make_dashboard())
    except KeyboardInterrupt:
        # Clear screen and say goodbye gracefully
        console.clear()
        console.print(Panel(
            "[bold green]Thank you for using Termux Multi-Agent Dashboard![/bold green]\n"
            "Stay productive and keep building! ⚡🚀",
            title="Exiting Dashboard",
            border_style="green",
            expand=False
        ))

if __name__ == '__main__':
    main()
