#!/usr/bin/env python3
"""
Main CLI entry point for DeepCode-CLI Phased Nexus.
"""

import argparse
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.api import (
    get_token,
    create_session,
    fetch_sessions,
    get_history,
    stream_completion,
    send_message,
    export_markdown,
    export_json,
)

console = Console()


def print_banner():
    """Print the CLI banner."""
    banner = """
  ███╗   ██╗██╗  ██╗███████╗██╗   ██╗
  ████╗  ██║██║ ██╔╝██╔════╝╚██╗ ██╔╝
  ██╔██╗ ██║█████╔╝ █████╗  ╚████╔╝
  ██║╚██╗██║██╔═██╗ ██╔══╝   ╚██╔╝
  ██║ ╚████║██║  ██╗███████╗  ██║
  ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝  ╚═╝
    """
    console.print(Panel.fit(banner, title="[bold cyan]NexusCLI[/]", border_style="cyan"))


def cmd_sessions(args):
    """List all sessions."""
    token = get_token()
    sessions = fetch_sessions(token)
    if not sessions:
        console.print("[yellow]No sessions found.[/]")
        return
    console.print("[bold]Sessions:[/]")
    for session in sessions:
        session_id = session.get("id", "N/A")
        title = session.get("title", "Untitled")
        console.print(f"  - [cyan]{session_id}[/] | {title}")


def cmd_new_session(args):
    """Create a new session."""
    token = get_token()
    model_type = args.model or "expert"
    session_id = create_session(token, model_type=model_type)
    console.print(f"[green]New session created: {session_id}[/]")
    if args.save:
        cfg = {}
        cfg_dir = Path.home() / ".deepcode-cli"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        try:
            cfg_dir.chmod(0o700)
        except Exception:
            pass
        cfg_file = cfg_dir / "config.json"
        if cfg_file.exists():
            cfg = json.loads(cfg_file.read_text())
        cfg["last_session"] = session_id
        cfg_file.write_text(json.dumps(cfg, indent=2))
        try:
            cfg_file.chmod(0o600)
        except Exception:
            pass
        console.print("[yellow]Saved as last_session.[/]")


def cmd_chat(args):
    """Start an interactive chat."""
    token = get_token()
    session_id = args.session_id or (args.last and get_last_session())
    if not session_id:
        console.print("[red]No session ID provided. Use --session-id or --last.[/]")
        return

    console.print(f"[bold]Chat Session: {session_id}[/]")

    # Load history
    history = get_history(token, session_id)
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            console.print(f"[blue]You:[/] {content}")
        else:
            console.print(f"[green]Assistant:[/] {content}")

    # Interactive loop
    parent_message_id = None
    while True:
        try:
            prompt = Prompt.ask("[bold cyan]You[/]")
            if prompt.lower() in ["exit", "quit", "q"]:
                break

            console.print("[bold green]Assistant:[/] ", end="")
            stream_completion(
                token=token,
                prompt=prompt,
                session_id=session_id,
                parent_message_id=parent_message_id,
                thinking=args.thinking,
                search=args.search,
            )
            console.print()
            parent_message_id = None  # Reset for next message

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Exiting...[/]")
            break


def cmd_send(args):
    """Send a single message."""
    token = get_token()
    session_id = args.session_id or get_last_session()
    if not session_id:
        console.print("[red]No session ID provided.[/]")
        return

    response = send_message(
        token=token,
        session_id=session_id,
        prompt=args.prompt,
        thinking=args.thinking,
        search=args.search,
    )
    console.print(f"[green]Response:[/] {response}")


def cmd_export(args):
    """Export session history."""
    token = get_token()
    session_id = args.session_id or get_last_session()
    if not session_id:
        console.print("[red]No session ID provided.[/]")
        return

    if args.format == "markdown":
        content = export_markdown(token, session_id)
    else:
        content = export_json(token, session_id)

    if args.output:
        with open(args.output, "w") as f:
            f.write(content)
        try:
            os.chmod(args.output, 0o600)
        except Exception:
            pass
        console.print(f"[green]Exported to {args.output}[/]")
    else:
        console.print(content)


def get_last_session():
    """Get the last session ID from config."""
    cfg_path = Path.home() / ".nexuscli" / "config.json"
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text())
        return cfg.get("last_session")
    return None


def main():
    """Main CLI entry point."""


    parser = argparse.ArgumentParser(
        description="NexusCLI - A fast, lightweight CLI for agent interactions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nexuscli sessions          List all sessions
  nexuscli new-session       Create a new session
  nexuscli chat --last       Start chat with last session
  nexuscli send --prompt "Hello" --last
  nexuscli export --last --format markdown
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Sessions command
    sessions_parser = subparsers.add_parser("sessions", help="List all sessions")
    sessions_parser.set_defaults(func=cmd_sessions)

    # New session command
    new_session_parser = subparsers.add_parser("new-session", help="Create a new session")
    new_session_parser.add_argument("--model", type=str, default="expert", help="Model type (expert/instant)")
    new_session_parser.add_argument("--save", action="store_true", help="Save as last session")
    new_session_parser.set_defaults(func=cmd_new_session)

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start an interactive chat")
    chat_parser.add_argument("--session-id", type=str, help="Session ID")
    chat_parser.add_argument("--last", action="store_true", help="Use last session")
    chat_parser.add_argument("--thinking", action="store_true", help="Enable thinking mode")
    chat_parser.add_argument("--search", action="store_true", help="Enable search mode")
    chat_parser.set_defaults(func=cmd_chat)

    # Send command
    send_parser = subparsers.add_parser("send", help="Send a single message")
    send_parser.add_argument("--prompt", type=str, required=True, help="Prompt to send")
    send_parser.add_argument("--session-id", type=str, help="Session ID")
    send_parser.add_argument("--last", action="store_true", help="Use last session")
    send_parser.add_argument("--thinking", action="store_true", help="Enable thinking mode")
    send_parser.add_argument("--search", action="store_true", help="Enable search mode")
    send_parser.set_defaults(func=cmd_send)

    # Export command
    export_parser = subparsers.add_parser("export", help="Export session history")
    export_parser.add_argument("--session-id", type=str, help="Session ID")
    export_parser.add_argument("--last", action="store_true", help="Use last session")
    export_parser.add_argument("--format", type=str, default="markdown", choices=["markdown", "json"], help="Export format")
    export_parser.add_argument("--output", type=str, help="Output file path")
    export_parser.set_defaults(func=cmd_export)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return

    print_banner()
    args.func(args)


if __name__ == "__main__":
    main()
