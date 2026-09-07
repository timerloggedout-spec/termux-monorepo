"""Non-secret catalog of provider runtimes exposed by ``multi-ai-cli``.

The catalog intentionally describes connection ownership and user-visible guidance only.
It never contains credentials, browser-profile paths, cookie names, session identifiers,
or provider request mechanics. Provider runtimes continue to own their native state.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ProviderDescriptor:
    """A provider available to the provider-selection checklist."""

    provider_id: str
    label: str
    runtime_owner: str
    capability: str
    connection_mode: str
    manual_steps: tuple[str, ...]
    manual_command: str | None
    account_url: str
    initial_state: str
    notes: str = ""


_PROVIDERS: tuple[ProviderDescriptor, ...] = (
    ProviderDescriptor(
        provider_id="deepseek",
        label="DeepSeek",
        runtime_owner="deepcli.session_manager",
        capability="live-web-wrapper",
        connection_mode="reuse-existing-runtime",
        manual_steps=(
            "Choose the account alias used by the existing DeepCLI runtime.",
            "Complete the provider-owned browser sign-in only if the local runtime requests it.",
            "Return here and mark the provider complete after the local runtime is ready.",
        ),
        manual_command="python3 deepcli/deepcli/cli.py import-session --dir <browser-profile>",
        account_url="https://chat.deepseek.com",
        initial_state="selected",
        notes="The hub delegates browser-session lifecycle ownership to DeepCLI.",
    ),
    ProviderDescriptor(
        provider_id="mistral",
        label="Mistral AI",
        runtime_owner="multi-ai-cli bridge and manual helper",
        capability="bridge-dependent",
        connection_mode="manual-provider-flow",
        manual_steps=(
            "Open the provider sign-in page and complete the provider-owned login flow.",
            "Use the existing local manual helper or bridge when configured.",
            "Return here and mark the provider complete after the bridge is ready.",
        ),
        manual_command="node multi-ai-cli/harvesters/mistral_cookies.cjs",
        account_url="https://chat.mistral.ai",
        initial_state="selected",
        notes="The current bridge/backend remains the runtime owner.",
    ),
    ProviderDescriptor(
        provider_id="gemini",
        label="Google Gemini",
        runtime_owner="multi-ai-cli.backends.gemini_web",
        capability="legacy-unverified",
        connection_mode="manual-provider-flow",
        manual_steps=(
            "Open the provider sign-in page and complete the provider-owned login flow.",
            "Confirm the existing local backend configuration is available.",
            "Return here and mark the provider complete after local validation.",
        ),
        manual_command=None,
        account_url="https://gemini.google.com",
        initial_state="selected",
        notes="No new authentication implementation is introduced by the hub.",
    ),
    ProviderDescriptor(
        provider_id="claude",
        label="Claude",
        runtime_owner="multi-ai-cli.backends.claude_web",
        capability="legacy-unverified",
        connection_mode="manual-provider-flow",
        manual_steps=(
            "Open the provider sign-in page and complete the provider-owned login flow.",
            "Confirm the existing local backend configuration is available.",
            "Return here and mark the provider complete after local validation.",
        ),
        manual_command=None,
        account_url="https://claude.ai",
        initial_state="selected",
        notes="No new authentication implementation is introduced by the hub.",
    ),
    ProviderDescriptor(
        provider_id="colab",
        label="Google Colab",
        runtime_owner="multi-ai-cli.backends.colab",
        capability="execution-only",
        connection_mode="manual-provider-flow",
        manual_steps=(
            "Open the provider page and complete the provider-owned login flow.",
            "Choose the notebook used by the existing Colab backend.",
            "Return here and mark the provider complete after local validation.",
        ),
        manual_command=None,
        account_url="https://colab.research.google.com",
        initial_state="selected",
        notes="Colab is an execution integration, not a chat-provider replacement.",
    ),
    ProviderDescriptor(
        provider_id="perplexity",
        label="Perplexity AI",
        runtime_owner="multi-ai-cli.backends.perplexity_web",
        capability="live-web-wrapper",
        connection_mode="manual-provider-flow",
        manual_steps=(
            "Open the provider sign-in page and complete the provider-owned login flow.",
            "Extract cookies using the provided helper script.",
            "Return here and mark the provider complete after local validation.",
        ),
        manual_command="python3 scripts/ops/extract_cookies.py",
        account_url="https://www.perplexity.ai",
        initial_state="selected",
        notes="Uses headless API emulation via session cookies.",
    ),
    ProviderDescriptor(
        provider_id="kimi",
        label="Moonshot Kimi",
        runtime_owner="multi-ai-cli.backends.kimi_web",
        capability="live-web-wrapper",
        connection_mode="manual-provider-flow",
        manual_steps=(
            "Open the provider sign-in page and complete the provider-owned login flow.",
            "Extract cookies using the provided helper script.",
            "Return here and mark the provider complete after local validation.",
        ),
        manual_command="python3 scripts/ops/extract_cookies.py",
        account_url="https://kimi.moonshot.cn",
        initial_state="selected",
        notes="Uses headless API emulation via session cookies.",
    ),
)

_BY_ID = {provider.provider_id: provider for provider in _PROVIDERS}


def all_providers() -> tuple[ProviderDescriptor, ...]:
    """Return catalog entries in the curated connection order."""

    return _PROVIDERS


def get_provider(provider_id: str) -> ProviderDescriptor:
    """Return a catalog entry or raise a concise error for unknown providers."""

    try:
        return _BY_ID[provider_id.strip().lower()]
    except (AttributeError, KeyError) as exc:
        available = ", ".join(_BY_ID)
        raise ValueError(f"Unknown provider '{provider_id}'. Available: {available}.") from exc


def provider_ids(items: Iterable[str]) -> tuple[str, ...]:
    """Validate and de-duplicate provider IDs while preserving caller order."""

    selected: list[str] = []
    for item in items:
        provider = get_provider(item)
        if provider.provider_id not in selected:
            selected.append(provider.provider_id)
    return tuple(selected)
