#!/usr/bin/env python3
"""CLI for the Termux lightweight multi-provider browser-wrapper hub."""
from __future__ import annotations

import json
from pathlib import Path

import click

from backends.lightwrap import LightwrapError
from core.chat_dispatcher import DELEGATED_PROVIDERS, WRAPPER_PROVIDERS, ChatDispatcher


def _dispatcher(profile_root: Path | None = None) -> ChatDispatcher:
    return ChatDispatcher(profile_root=profile_root)


def _json(value: dict) -> None:
    click.echo(json.dumps(value, indent=2, sort_keys=True))


def _handle(operation):
    try:
        return operation()
    except (LightwrapError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@click.group()
def cli():
    """Run verified local browser-wrapper provider actions."""


@cli.command()
@click.option("--provider", "provider", "-p", default="deepseek", show_default=True)
@click.option("--account", default="default", show_default=True, help="Non-secret local account/profile alias.")
@click.option("--session", "session", "-s", default=None, help="Optional non-secret conversation context key.")
@click.option("--profile-root", type=click.Path(file_okay=False, path_type=Path), default=None)
@click.argument("prompt")
def chat(provider: str, account: str, session: str | None, profile_root: Path | None, prompt: str):
    """Send only through a prior send-ready local browser profile."""

    reply = _handle(lambda: _dispatcher(profile_root).send(provider, prompt, session, account))
    click.echo(reply)


@cli.group()
@click.option("--profile-root", type=click.Path(file_okay=False, path_type=Path), default=None)
@click.pass_context
def providers(ctx: click.Context, profile_root: Path | None):
    """Inspect, connect, probe, and operate lightweight wrapper providers."""

    ctx.ensure_object(dict)
    ctx.obj["profile_root"] = profile_root


def _group_dispatcher(ctx: click.Context) -> ChatDispatcher:
    return _dispatcher(ctx.obj.get("profile_root"))


@providers.command("list")
@click.pass_context
def list_providers(ctx: click.Context):
    """List browser-wrapper and delegated provider classifications."""

    click.echo("ID\tKIND\tACTION")
    for provider in sorted(WRAPPER_PROVIDERS):
        data = _handle(lambda provider=provider: _group_dispatcher(ctx).capabilities(provider))
        click.echo(f"{provider}\t{data.get('kind')}\t{data.get('state')}")
    for provider in sorted(DELEGATED_PROVIDERS):
        click.echo(f"{provider}\tdelegated\towned by existing compatibility/routing workstream")


@providers.command("capabilities")
@click.argument("provider")
@click.option("--account", default="default", show_default=True)
@click.pass_context
def capabilities(ctx: click.Context, provider: str, account: str):
    """Show non-secret profile state, evidence classification, and last probe result."""

    _json(_handle(lambda: _group_dispatcher(ctx).capabilities(provider, account)))


@providers.command("configure")
@click.argument("provider")
@click.option("--account", default="default", show_default=True)
@click.option("--url", required=True, help="Provider browser URL observed from the user-owned web UI.")
@click.option("--input-mode", type=click.Choice(["textarea", "react-textarea", "contenteditable"]), required=True)
@click.option("--input-selector", "input_selectors", multiple=True, required=True)
@click.option("--submit-selector", "submit_selectors", multiple=True, required=True)
@click.option("--response-selector", "response_selectors", multiple=True, required=True)
@click.option("--ready-selector", "ready_selectors", multiple=True, required=True)
@click.option("--login-selector", "login_selectors", multiple=True)
@click.pass_context
def configure(
    ctx: click.Context,
    provider: str,
    account: str,
    url: str,
    input_mode: str,
    input_selectors: tuple[str, ...],
    submit_selectors: tuple[str, ...],
    response_selectors: tuple[str, ...],
    ready_selectors: tuple[str, ...],
    login_selectors: tuple[str, ...],
):
    """Save a local non-secret selector fixture for a provider/account profile."""

    path = _handle(
        lambda: _group_dispatcher(ctx).configure_profile(
            provider,
            account,
            url=url,
            input_mode=input_mode,
            input_selectors=input_selectors,
            submit_selectors=submit_selectors,
            response_selectors=response_selectors,
            ready_selectors=ready_selectors,
            login_selectors=login_selectors,
        )
    )
    click.echo(f"Saved local selector profile: {path}")
    click.echo("Run 'providers probe <provider> --account <alias>' before sending.")


@providers.command("connect")
@click.argument("provider")
@click.option("--account", default="default", show_default=True)
@click.pass_context
def connect(ctx: click.Context, provider: str, account: str):
    """Open a visible provider browser for a user-mediated login or challenge step."""

    result = _handle(lambda: _group_dispatcher(ctx).connect(provider, account))
    if result:
        _json(result)


@providers.command("probe")
@click.argument("provider")
@click.option("--account", default="default", show_default=True)
@click.pass_context
def probe(ctx: click.Context, provider: str, account: str):
    """Run a redacted local readiness and selector probe for an existing profile."""

    _json(_handle(lambda: _group_dispatcher(ctx).probe(provider, account)))


@providers.command("status")
@click.argument("provider")
@click.option("--account", default="default", show_default=True)
@click.pass_context
def status(ctx: click.Context, provider: str, account: str):
    """Alias for capabilities, useful after connect or probe."""

    _json(_handle(lambda: _group_dispatcher(ctx).capabilities(provider, account)))


if __name__ == "__main__":
    cli(obj={})
