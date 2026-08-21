#!/usr/bin/env python3
"""Mistralai Vibe Code webWrapper CLI - Legacy Interface"""
import click
from core.session_manager import SessionManager
from core.chat_dispatcher import ChatDispatcher

@click.group()
def cli():
    """Legacy CLI interface for backward compatibility."""
    pass

@cli.command()
@click.option("--provider", "-p", default="mistral")
@click.option("--session", "-s", default=None)
@click.argument("prompt")
def chat(provider, session, prompt):
    """Send a chat message (legacy interface)."""
    mgr = SessionManager()
    dispatcher = ChatDispatcher(mgr)
    try:
        click.echo(dispatcher.send(provider, prompt, session))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.option("--provider", "-p", default="colab")
@click.argument("code")
def execute(provider, code):
    """Execute code (legacy interface)."""
    mgr = SessionManager()
    dispatcher = ChatDispatcher(mgr)
    try:
        click.echo(dispatcher.send(provider, code))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    # Redirect to new CLI if no arguments
    import sys
    if len(sys.argv) == 1:
        from mistralai_cli import cli as new_cli
        new_cli()
    else:
        cli()
