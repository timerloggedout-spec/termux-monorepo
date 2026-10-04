"""_v1_namespace — canonical provenance namespace generator.

Every attributed action uses one string:

    provider::modelfamily::model::settings::role[#moniker]

Fields are positional. Defaults read from environment:
    DEEPSEEK_MODEL    -> model
    DEEPSEEK_ACCOUNT  -> contributor tag (not in namespace)

Public API:
    build(role, provider=None, family=None, model=None,
          settings=None, moniker=None) -> str
    parse(ns) -> dict
    emit_for_commit(role, moniker=None) -> str
"""
import os, re

VALID_ROLES = {"recon","plan","forge","sentinel","rollup",
               "hygienist","scribe","orchestrator"}

_PROVIDER_MAP = {
    "deepseek":   ("deepseek", "deepseek-v4"),
    "google":     ("google",   "gemini"),
    "openrouter": ("openrouter", None),
    "anthropic":  ("anthropic", "claude"),
}


def build(role, provider=None, family=None, model=None,
          settings=None, moniker=None):
    if role not in VALID_ROLES:
        raise ValueError("unknown role: " + str(role))
    provider = provider or "deepseek"
    default_family, default_model = _PROVIDER_MAP.get(provider, (provider, None))
    family = family or default_family or "unknown"
    model  = model  or os.environ.get("DEEPSEEK_MODEL") or default_model or "unknown"
    settings = settings or ("thinking" if "reasoner" in model or "v4" in model else "default")
    ns = "::".join([provider, family, model, settings, role])
    if moniker:
        ns += "#" + re.sub(r"[^a-z0-9-]", "-", moniker.lower())[:32]
    return ns


def parse(ns):
    if not ns: return {}
    moniker = None
    if "#" in ns:
        ns, moniker = ns.split("#", 1)
    parts = ns.split("::")
    keys = ["provider", "family", "model", "settings", "role"]
    out = dict(zip(keys, parts))
    if moniker:
        out["moniker"] = moniker
    return out


def emit_for_commit(role, moniker=None):
    """Trailer block to append to a commit message body."""
    ns = build(role, moniker=moniker)
    return (
        "Provenance-Role: " + role + "\n"
        "Provenance-Namespace: " + ns + "\n"
    )
