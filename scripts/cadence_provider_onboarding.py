#!/usr/bin/env python3
"""Cadence provider auto-onboarding: one registry, every surface checked.

Implements: QAC-005 (docs/proposals/active/quota-aware-cadence-rfp/ITEMS.md)

Before this module, adding a provider meant hand-editing up to five
independent surfaces, and nothing verified the surfaces agreed:

  1. catalog endpoint   scripts/provider_model_catalog.py ENDPOINTS, or
                        scripts/provider_extension_catalogs.py, or
                        scripts/provider_catalog_protocols.py
  2. catalog secret     the same modules' SECRETS / SECRET_ALIASES
  3. availability env   .github/workflows/provider-availability.yml
  4. quota family       ops/quota/provider-managers.json (provider-quota-managers/v1)
  5. review bot maps    .github/workflows/peer-review-orchestrator.yml
                        (kind=review providers only)

The registry at ops/cadence/provider-onboarding.json is the single
onboarding record. This module derives the *actual* surface matrix from
the live code/workflows, and `check` fails when:

  - a provider appears on any surface but has no registry entry
    (it was wired somewhere and forgotten elsewhere), or
  - a registry entry names a provider that appears nowhere, or
  - an expected surface is missing for a provider and no exception with
    a reason is recorded in its registry entry, or
  - an exception is recorded for a surface that is actually present
    (stale exception), or
  - a secret name wired in provider-availability.yml is claimed by no
    registry entry (primary secret, alias, or declared extra env).

`scaffold` prints every snippet a new provider needs, for every surface,
from one invocation — that output is the onboarding patch, and the
registry entry it prints is pasted into the registry in the same PR.
`render` writes the derived matrix to
docs/ops/generated/cadence-provider-onboarding.json.

No network, no credentials, no admission/routing decision happens here.
Secret *names* only, per the fleet names-only credential rule.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "ops" / "cadence" / "provider-onboarding.json"
QUOTA_MANAGERS = ROOT / "ops" / "quota" / "provider-managers.json"
AVAILABILITY_WF = ROOT / ".github" / "workflows" / "provider-availability.yml"
ORCHESTRATOR_WF = ROOT / ".github" / "workflows" / "peer-review-orchestrator.yml"
GENERATED = ROOT / "docs" / "ops" / "generated" / "cadence-provider-onboarding.json"

SCHEMA = "cadence-provider-onboarding/v1"
LLM_SURFACES = ("catalog_endpoint", "catalog_secret", "availability_env", "quota_family")
REVIEW_SURFACES = ("review_login", "review_check_app")
ALL_SURFACES = LLM_SURFACES + REVIEW_SURFACES


def _load_catalog():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from scripts import (  # noqa: WPS433 (runtime import of sibling modules)
        provider_catalog_protocols,
        provider_extension_catalogs,
        provider_model_catalog,
    )

    return provider_model_catalog, provider_extension_catalogs, provider_catalog_protocols


def collect_surfaces(root: Path = ROOT) -> dict:
    """Derive the actual per-provider surface matrix from live sources."""
    global ROOT
    old = ROOT
    ROOT = root
    try:
        catalog, extension, protocol = _load_catalog()
    finally:
        ROOT = old

    endpoint_module: dict[str, str] = {}
    for name in catalog.ENDPOINTS:
        if name in extension.ENDPOINTS:
            endpoint_module[name] = "extension"
        elif name in protocol.ENDPOINTS:
            endpoint_module[name] = "protocol"
        else:
            endpoint_module[name] = "core"

    availability_text = (root / ".github/workflows/provider-availability.yml").read_text(encoding="utf-8")
    availability_env = set(re.findall(r"secrets\.([A-Z0-9_]+)", availability_text))

    quota = json.loads((root / "ops/quota/provider-managers.json").read_text(encoding="utf-8"))
    quota_status = {r["provider_family"]: r["status"] for r in quota["provider_families"]}

    orch_text = (root / ".github/workflows/peer-review-orchestrator.yml").read_text(encoding="utf-8")
    logins = {pid: f"{login}[bot]" for login, pid in re.findall(r"\['([a-z0-9-]+)\[bot\]',\s*'([a-z]+)'\]", orch_text)}
    check_block = re.search(r"providerCheckApps = new Map\(\[(.*?)\]\);", orch_text, re.S)
    check_apps = {pid: app for pid, app in re.findall(r"\['([a-z]+)',\s*'([a-z0-9-]+)'\]", check_block.group(1))} if check_block else {}
    allowed = re.search(r"OPERATOR_ALLOWED_ACTIONS \|\| '([^']*)'", orch_text)
    trigger_actions = {}
    for pair in (allowed.group(1) if allowed else "").split(","):
        if ":" in pair:
            pid, action = pair.split(":", 1)
            trigger_actions.setdefault(pid.strip(), []).append(action.strip())
    required_default = re.search(r"PEER_REQUIRED_PROVIDERS \|\| '([^']*)'", orch_text)
    default_required = [p.strip() for p in (required_default.group(1) if required_default else "").split(",") if p.strip()]

    providers: dict[str, dict] = {}

    def row(pid: str) -> dict:
        return providers.setdefault(pid, {
            "catalog_endpoint": None, "catalog_secret": None, "secret_aliases": [],
            "availability_env": [], "quota_family": None,
            "review_login": None, "review_check_app": None,
            "review_trigger_actions": [], "review_required_default": False,
            "public_catalog": False,
        })

    for pid, module in endpoint_module.items():
        row(pid)["catalog_endpoint"] = module
    for pid, secret in catalog.SECRETS.items():
        row(pid)["catalog_secret"] = secret
    for pid, aliases in getattr(catalog, "SECRET_ALIASES", {}).items():
        row(pid)["secret_aliases"] = sorted(aliases)
    for pid in getattr(catalog, "PUBLIC_CATALOGS", []):
        row(pid)["public_catalog"] = True
    for pid, status in quota_status.items():
        row(pid)["quota_family"] = status
    for pid, login in logins.items():
        row(pid)["review_login"] = login
    for pid, app in check_apps.items():
        row(pid)["review_check_app"] = app
    for pid, actions in trigger_actions.items():
        row(pid)["review_trigger_actions"] = actions
    for pid in default_required:
        row(pid)["review_required_default"] = True

    # Availability env presence is claimed per provider through its secret
    # names (primary + aliases). Declared extras are resolved by check()
    # against the registry, because their names do not derive from a
    # catalog secret (e.g. xfyun's vendor-alias env, cloudflare's account id).
    claimed: dict[str, str] = {}
    for pid, r in providers.items():
        names = ([r["catalog_secret"]] if r["catalog_secret"] else []) + r["secret_aliases"]
        for name in names:
            if name in availability_env:
                r["availability_env"].append(name)
                claimed[name] = pid
        r["availability_env"].sort()

    return {
        "providers": providers,
        "availability_env_all": sorted(availability_env),
        "availability_claimed": claimed,
        "default_required": default_required,
    }


def load_registry(root: Path = ROOT) -> dict:
    data = json.loads((root / "ops/cadence/provider-onboarding.json").read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise ValueError(f"unsupported registry schema: {data.get('schema')!r}")
    return data


def _apply_registry_extras(surfaces: dict, registry: dict) -> tuple[dict, list[str]]:
    """Claim registry-declared extra availability env names per provider."""
    claimed = dict(surfaces["availability_claimed"])
    problems: list[str] = []
    actual = surfaces["providers"]
    for entry in registry["providers"]:
        for name in entry.get("availability_extra_env", []):
            if name not in surfaces["availability_env_all"]:
                problems.append(f"{entry['provider']}: availability_extra_env {name} declared but not wired in provider-availability.yml")
            claimed[name] = entry["provider"]
            if entry["provider"] in actual:
                actual[entry["provider"]]["availability_env"] = sorted(
                    set(actual[entry["provider"]]["availability_env"]) | {name})
    return claimed, problems


def check(root: Path = ROOT) -> list[str]:
    """Return a list of onboarding drift problems (empty = fully onboarded)."""
    problems: list[str] = []
    surfaces = collect_surfaces(root)
    actual = surfaces["providers"]
    registry = load_registry(root)
    entries = {e["provider"]: e for e in registry["providers"]}

    for pid in sorted(set(actual) - set(entries)):
        problems.append(f"{pid}: present on a surface but has no registry entry — onboard it or remove the wiring")
    for pid in sorted(set(entries) - set(actual)):
        problems.append(f"{pid}: registry entry but present on no surface — stale entry")

    claimed, extra_problems = _apply_registry_extras(surfaces, registry)
    problems.extend(extra_problems)
    for name in surfaces["availability_env_all"]:
        if name not in claimed:
            problems.append(f"availability env {name}: wired in provider-availability.yml but claimed by no registry entry")

    for pid, entry in sorted(entries.items()):
        if pid not in actual:
            continue
        kind = entry.get("kind")
        expected = LLM_SURFACES if kind == "llm" else REVIEW_SURFACES if kind == "review" else None
        if expected is None:
            problems.append(f"{pid}: unknown kind {kind!r} (expected 'llm' or 'review')")
            continue
        exceptions = {e["surface"]: e["reason"] for e in entry.get("exceptions", [])}
        for surface in ALL_SURFACES:
            present = bool(actual[pid][surface])
            if surface in expected:
                if not present and surface not in exceptions:
                    problems.append(f"{pid}: expected surface {surface} missing and no exception recorded")
                if present and surface in exceptions:
                    problems.append(f"{pid}: stale exception for {surface} — surface is present, remove the exception")
            else:
                if present and surface not in exceptions:
                    problems.append(f"{pid}: surface {surface} present but kind={kind} does not expect it and no exception recorded")
            if surface in exceptions and not str(exceptions[surface]).strip():
                problems.append(f"{pid}: exception for {surface} has an empty reason")
        for surface in exceptions:
            if surface not in ALL_SURFACES:
                problems.append(f"{pid}: exception names unknown surface {surface!r}")
    return problems


def build_report(root: Path = ROOT) -> dict:
    surfaces = collect_surfaces(root)
    registry = load_registry(root)
    _apply_registry_extras(surfaces, registry)
    entries = {e["provider"]: e for e in registry["providers"]}
    rows = []
    for pid in sorted(surfaces["providers"]):
        actual = surfaces["providers"][pid]
        entry = entries.get(pid, {})
        rows.append({
            "provider": pid,
            "kind": entry.get("kind"),
            "catalog_endpoint": actual["catalog_endpoint"],
            "catalog_secret": actual["catalog_secret"],
            "secret_aliases": actual["secret_aliases"],
            "availability_env": actual["availability_env"],
            "quota_family": actual["quota_family"],
            "public_catalog": actual["public_catalog"],
            "review_login": actual["review_login"],
            "review_check_app": actual["review_check_app"],
            "review_trigger_actions": actual["review_trigger_actions"],
            "review_required_default": actual["review_required_default"],
            "exceptions": entry.get("exceptions", []),
        })
    return {
        "schema": SCHEMA,
        "contract": "Derived surface matrix for cadence provider onboarding; "
                    "regenerate with scripts/cadence_provider_onboarding.py render. "
                    "Secret names only; no values, no admission decision.",
        "providers": rows,
        "counts": {
            "providers": len(rows),
            "llm": sum(1 for r in rows if r["kind"] == "llm"),
            "review": sum(1 for r in rows if r["kind"] == "review"),
            "with_quota_adapter": sum(1 for r in rows if r["quota_family"] == "implemented_passive_adapter"),
            "exceptions": sum(len(r["exceptions"]) for r in rows),
        },
    }


def scaffold(provider: str, kind: str, endpoint: str = "", secret_env: str = "",
             bot_login: str = "", module: str = "extension") -> str:
    """Print the complete onboarding patch for one new provider."""
    provider = provider.strip().lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", provider):
        raise ValueError("provider id must be lowercase [a-z0-9_-]")
    secret_env = secret_env or f"{provider.upper()}_API_KEY"
    out: list[str] = [f"# Cadence onboarding patch for provider '{provider}' (kind={kind})", ""]
    entry: dict = {"provider": provider, "kind": kind}
    if kind == "llm":
        if not endpoint:
            raise ValueError("llm scaffold requires --endpoint")
        out += [
            "## 1. Registry entry — append to ops/cadence/provider-onboarding.json providers[]",
            json.dumps(entry, indent=2), "",
            f"## 2. Catalog endpoint — scripts/provider_{'extension_catalogs' if module == 'extension' else 'model_catalog'}.py",
            f'    "{provider}": "{endpoint}",  # in ENDPOINTS',
            f'    "{provider}": "{secret_env}",  # in SECRETS (extension module derives this automatically)', "",
            "## 3. Availability env — .github/workflows/provider-availability.yml (job env)",
            f"      {secret_env}: ${{{{ secrets.{secret_env} }}}}", "",
            "## 4. Quota family stub — ops/quota/provider-managers.json provider_families[]",
            json.dumps({"provider_family": provider, "status": "public_documentation_only",
                        "source": "<official rate-limit docs URL>", "scope": "<documented scope>",
                        "reset": "unknown", "signals": []}, indent=2), "",
            "## 5. Verify",
            "    python3 scripts/cadence_provider_onboarding.py check",
            "    python3 scripts/cadence_provider_onboarding.py render",
            "    python3 -m pytest tests/test_provider_onboarding.py -q", "",
            "Provisioning the secret itself stays names-only via the vault/PAT route;",
            "this patch never carries a secret value.",
        ]
    elif kind == "review":
        if not bot_login:
            raise ValueError("review scaffold requires --bot-login (without the [bot] suffix)")
        out += [
            "## 1. Registry entry — append to ops/cadence/provider-onboarding.json providers[]",
            json.dumps(entry, indent=2), "",
            "## 2. Orchestrator maps — .github/workflows/peer-review-orchestrator.yml (both collect and request scripts)",
            f"    ['{bot_login}[bot]', '{provider}'],  // providerLogins",
            f"    ['{provider}', '{provider}'],  // providerCheckApps (value = check-run app slug)", "",
            "## 3. Policy (repo vars, only if this provider should be required/triggerable)",
            f"    PEER_REQUIRED_PROVIDERS += {provider}  (default stays coderabbit-only otherwise)",
            f"    OPERATOR_ALLOWED_ACTIONS += {provider}:trigger_review  (only with a documented trigger command)", "",
            "## 4. Verify",
            "    python3 scripts/cadence_provider_onboarding.py check",
            "    python3 scripts/cadence_provider_onboarding.py render",
        ]
    else:
        raise ValueError("kind must be 'llm' or 'review'")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="fail on any onboarding drift")
    sub.add_parser("render", help="regenerate docs/ops/generated/cadence-provider-onboarding.json")
    sc = sub.add_parser("scaffold", help="print the full onboarding patch for a new provider")
    sc.add_argument("provider")
    sc.add_argument("--kind", choices=["llm", "review"], required=True)
    sc.add_argument("--endpoint", default="")
    sc.add_argument("--secret-env", default="")
    sc.add_argument("--bot-login", default="")
    sc.add_argument("--module", choices=["extension", "core"], default="extension")
    args = parser.parse_args(argv)

    if args.cmd == "check":
        problems = check()
        if problems:
            print("cadence provider onboarding drift:")
            for problem in problems:
                print(f"  - {problem}")
            return 1
        report = build_report()
        print(f"ok: {report['counts']['providers']} providers fully onboarded "
              f"({report['counts']['llm']} llm, {report['counts']['review']} review, "
              f"{report['counts']['exceptions']} recorded exceptions)")
        return 0
    if args.cmd == "render":
        GENERATED.write_text(json.dumps(build_report(), indent=2) + "\n", encoding="utf-8")
        print(f"wrote {GENERATED.relative_to(ROOT)}")
        return 0
    if args.cmd == "scaffold":
        try:
            print(scaffold(args.provider, args.kind, args.endpoint, args.secret_env, args.bot_login, args.module), end="")
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
