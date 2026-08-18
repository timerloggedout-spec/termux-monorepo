#!/usr/bin/env python3
"""Command line entrypoint for the lightweight multi-provider surface."""
from __future__ import annotations

from pathlib import Path

import click

from core.provider_checklist import (
    enqueue,
    load_state,
    next_provider,
    public_view,
    save_state,
    select,
    transition,
)
from core.provider_registry import get_provider


@click.group()
def cli():
    """Use existing provider backends and manage non-secret provider checklist state."""


@cli.command()
@click.option("--provider", "provider", "-p", default="deepseek")
@click.option("--session", "session", "-s", default=None)
@click.argument("prompt")
def chat(provider, session, prompt):
    """Send a prompt through an existing provider backend."""

    from core.chat_dispatcher import ChatDispatcher
    from core.session_manager import SessionManager

    mgr = SessionManager()
    dispatcher = ChatDispatcher(mgr)
    try:
        click.echo(dispatcher.send(provider, prompt, session))
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)


@cli.command()
@click.option("--provider", "provider", "-p", default="colab")
@click.argument("code")
def execute(provider, code):
    """Execute code through an existing execution backend."""

    from core.chat_dispatcher import ChatDispatcher
    from core.session_manager import SessionManager

    mgr = SessionManager()
    dispatcher = ChatDispatcher(mgr)
    try:
        click.echo(dispatcher.send(provider, code))
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)


def _load(ctx: click.Context) -> dict:
    return load_state(ctx.obj.get("state_dir"))


def _save(ctx: click.Context, payload: dict) -> Path:
    return save_state(payload, ctx.obj.get("state_dir"))


def _provider_or_fail(provider_id: str):
    try:
        return get_provider(provider_id)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


def _transition_or_fail(payload: dict, provider_id: str, target: str, **kwargs) -> None:
    try:
        transition(payload, provider_id, target, **kwargs)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


def _print_steps(descriptor) -> None:
    click.echo(f"Provider: {descriptor.label} ({descriptor.provider_id})")
    click.echo(f"Runtime owner: {descriptor.runtime_owner}")
    click.echo(f"Connection mode: {descriptor.connection_mode}")
    for index, step in enumerate(descriptor.manual_steps, start=1):
        click.echo(f"{index}. {step}")
    if descriptor.manual_command:
        click.echo(f"Existing local helper (run yourself when ready): {descriptor.manual_command}")
    click.echo(f"Create or return to account: {descriptor.account_url}")
    if descriptor.notes:
        click.echo(f"Note: {descriptor.notes}")


@cli.group()
@click.option(
    "--state-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Override the local non-secret checklist directory.",
)
@click.pass_context
def providers(ctx: click.Context, state_dir: Path | None):
    """Select providers and resume their non-secret connection checklist."""

    ctx.ensure_object(dict)
    ctx.obj["state_dir"] = state_dir


@providers.command("list")
@click.pass_context
def list_providers(ctx: click.Context):
    """List catalog entries and their current checklist state without networking."""

    payload = _load(ctx)
    click.echo("ID\tSTATE\tSELECTED\tCAPABILITY\tRUNTIME OWNER")
    for row in public_view(payload):
        click.echo(
            f"{row['provider_id']}\t{row['state']}\t{str(row['selected']).lower()}\t"
            f"{row['capability']}\t{row['runtime_owner']}"
        )


@providers.command("select")
@click.argument("provider_ids", nargs=-1, required=True)
@click.pass_context
def select_providers(ctx: click.Context, provider_ids: tuple[str, ...]):
    """Select an ordered set of providers for the connection checklist."""

    payload = _load(ctx)
    try:
        select(payload, provider_ids)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    path = _save(ctx, payload)
    click.echo(f"Selected: {', '.join(payload['selected'])}")
    click.echo(f"Checklist state: {path}")


@providers.command("next")
@click.pass_context
def show_next(ctx: click.Context):
    """Show the next provider that can be resumed, with no provider call."""

    payload = _load(ctx)
    entry = next_provider(payload)
    if not entry:
        click.echo("No provider is awaiting action. Use 'providers select' or 'providers retry'.")
        return
    descriptor = _provider_or_fail(entry["provider_id"])
    click.echo(f"Current checklist state: {entry['state']}")
    _print_steps(descriptor)


@providers.command("begin")
@click.argument("provider_id")
@click.option("--account", default=None, help="Non-secret local account alias, such as primary or secondary.")
@click.pass_context
def begin(ctx: click.Context, provider_id: str, account: str | None):
    """Begin a manual provider-owned connection step and mark it resumable."""

    descriptor = _provider_or_fail(provider_id)
    payload = _load(ctx)
    try:
        enqueue(payload, descriptor.provider_id)
        _transition_or_fail(payload, descriptor.provider_id, "connecting", account=account)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    _save(ctx, payload)
    _print_steps(descriptor)
    click.echo("When the provider-owned local flow is ready, run 'providers complete <provider>'.")


@providers.command("complete")
@click.argument("provider_id")
@click.pass_context
def complete(ctx: click.Context, provider_id: str):
    """Record that the user completed the provider-owned local connection flow."""

    descriptor = _provider_or_fail(provider_id)
    payload = _load(ctx)
    try:
        enqueue(payload, descriptor.provider_id)
        entry = payload["providers"][descriptor.provider_id]
        if entry["state"] == "selected":
            _transition_or_fail(payload, descriptor.provider_id, "connecting")
        _transition_or_fail(payload, descriptor.provider_id, "connected")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    _save(ctx, payload)
    click.echo(f"Marked {descriptor.label} connected. Provider-native session state remains with its runtime.")


@providers.command("skip")
@click.argument("provider_id")
@click.option("--reason", default="Deferred by user.", show_default=True)
@click.pass_context
def skip(ctx: click.Context, provider_id: str, reason: str):
    """Skip a provider without losing the ability to retry or create an account later."""

    descriptor = _provider_or_fail(provider_id)
    payload = _load(ctx)
    try:
        enqueue(payload, descriptor.provider_id)
        _transition_or_fail(payload, descriptor.provider_id, "skipped", reason=reason)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    _save(ctx, payload)
    click.echo(f"Skipped {descriptor.label}. Resume with 'providers retry {descriptor.provider_id}'.")
    click.echo(f"Account page: {descriptor.account_url}")


@providers.command("retry")
@click.argument("provider_id")
@click.pass_context
def retry(ctx: click.Context, provider_id: str):
    """Return a skipped, failed, or completed provider to the resumable queue."""

    descriptor = _provider_or_fail(provider_id)
    payload = _load(ctx)
    try:
        enqueue(payload, descriptor.provider_id)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    _save(ctx, payload)
    click.echo(f"Queued {descriptor.label}. Use 'providers begin {descriptor.provider_id}' when ready.")


@providers.command("account")
@click.argument("provider_id")
@click.pass_context
def account(ctx: click.Context, provider_id: str):
    """Route a provider to account creation or return-to-login guidance."""

    descriptor = _provider_or_fail(provider_id)
    payload = _load(ctx)
    try:
        enqueue(payload, descriptor.provider_id)
        _transition_or_fail(payload, descriptor.provider_id, "needs_account")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    _save(ctx, payload)
    click.echo(f"Create or return to {descriptor.label}: {descriptor.account_url}")
    click.echo(f"Afterward, run 'providers retry {descriptor.provider_id}'.")


@providers.command("status")
@click.pass_context
def status(ctx: click.Context):
    """Render selected providers, resumable state, and the next user action."""

    payload = _load(ctx)
    selected = payload.get("selected", [])
    if not selected:
        click.echo("No providers selected. Start with 'providers select deepseek mistral gemini claude colab'.")
        return
    click.echo("ID\tSTATE\tACCOUNT\tATTEMPTS\tNEXT ACTION")
    for provider_id in selected:
        entry = payload["providers"][provider_id]
        descriptor = _provider_or_fail(provider_id)
        if entry["state"] == "connected":
            action = "Ready; provider-native runtime owns session state."
        elif entry["state"] == "skipped":
            action = f"Retry with: providers retry {provider_id}"
        elif entry["state"] == "needs_account":
            action = f"Create/return: {descriptor.account_url}; then providers retry {provider_id}"
        else:
            action = f"Continue with: providers begin {provider_id}"
        click.echo(
            f"{provider_id}\t{entry['state']}\t{entry.get('account') or '—'}\t"
            f"{entry.get('attempts', 0)}\t{action}"
        )


if __name__ == "__main__":
    cli(obj={})
