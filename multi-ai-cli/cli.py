#!/usr/bin/env python3
import click
from core.session_manager import SessionManager
from core.chat_dispatcher import ChatDispatcher

@click.group()
def cli():
    pass

@cli.command()
@click.option("--provider", "-p", default="deepseek")
@click.option("--session", "-s", default=None)
@click.argument("prompt")
def chat(provider, session, prompt):
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
    mgr = SessionManager()
    dispatcher = ChatDispatcher(mgr)
    try:
        click.echo(dispatcher.send(provider, code))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    cli()
