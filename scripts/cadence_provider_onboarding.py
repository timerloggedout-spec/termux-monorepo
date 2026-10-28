#!/usr/bin/env python3
"""Cadence provider auto-onboarding: one registry, every surface checked.

Implements: QAC-005 + QAC-006 (docs/proposals/active/quota-aware-cadence-rfp/ITEMS.md)

Before this module, adding a provider meant hand-editing independent
surfaces, and nothing verified the surfaces agreed:

  1. catalog endpoint   scripts/provider_model_catalog.py ENDPOINTS, or
                        scripts/provider_extension_catalogs.py, or
                        scripts/provider_catalog_protocols.py
  2. catalog secret     the same modules' SECRETS / SECRET_ALIASES
  3. availability env   .github/workflows/provider-availability.yml
  4. quota family       ops/quota/provider-managers.json (provider-quota-managers/v1)
  5. quota registry     ops/quota/registry.json model-lane records, mapped
                        to families by the provider_quota_coverage rule
                        (lane == "model" or id in provider_quota_service
                        SERVICES; provider alias google -> gemini)
  6. review bot maps    .github/workflows/peer-review-orchestrator.yml
                        (kind=review providers only)

Automation (QAC-006, owner order: automated & programmatic):
  - `apply` writes a new provider onto every surface programmatically
    (registry entry, extension catalog, availability env, quota family,
    quota registry record) and lists the generator post-steps.
  - `autofix` adds registry entries for providers that appeared on a
    surface without one (kind inferred; missing surfaces recorded as
    exceptions whose reason states they were absent at first detection).
    The cadence-provider-onboarding workflow runs check + autofix +
    render on every surface change and weekly, and opens/updates one
    auto-extend PR; hard drift (stale exceptions, unclaimed secrets,
    unacknowledged unmapped quota providers) fails the run loudly.
  - Model-lane quota providers that map to no family are surfaced:
    namespaced aggregates (g4f/*, gpt4free/*) are counted in the report;
    a non-namespaced unmapped provider fails check unless it is listed
    in the registry's acknowledged_unmapped_quota_providers with a reason.

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
LLM_SURFACES = ("catalog_endpoint", "catalog_secret", "availability_env", "quota_family", "quota_registry")
REVIEW_SURFACES = ("review_login", "review_check_app")
ALL_SURFACES = LLM_SURFACES + REVIEW_SURFACES
QUOTA_REGISTRY = "ops/quota/registry.json"
AUTO_EXCEPTION_REASON = ("auto-registered by the cadence-provider-onboarding workflow: "
                         "surface absent at first detection — complete the surface or "
                         "amend this reason in the auto-extend PR")


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
            "availability_env": [], "quota_family": None, "quota_registry": [],
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

    # Quota registry surface (ops/quota/registry.json), mapped with the
    # provider_quota_coverage rule: a service matches a family when its
    # lane is "model" or its id is a provider_quota_service SERVICES id,
    # with provider alias google -> gemini.
    try:
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from scripts import provider_quota_service

        private_ids = set(provider_quota_service.SERVICES)
    except Exception:
        private_ids = set()
    quota_registry = json.loads((root / QUOTA_REGISTRY).read_text(encoding="utf-8"))
    unmapped: dict[str, list[str]] = {}
    namespaced = 0
    for svc in quota_registry.get("services", []):
        if svc.get("lane") != "model" and svc.get("id") not in private_ids:
            continue
        raw = str(svc.get("provider", "")).lower()
        family = {"google": "gemini"}.get(raw, raw)
        if family in providers or family in quota_status:
            row(family)["quota_registry"] = sorted(set(row(family)["quota_registry"]) | {svc["id"]})
        elif "/" in raw:
            namespaced += 1
        else:
            unmapped.setdefault(raw, []).append(svc["id"])
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
        "quota_registry_unmapped": {k: sorted(v) for k, v in sorted(unmapped.items())},
        "quota_registry_namespaced_records": namespaced,
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

    acknowledged = registry.get("acknowledged_unmapped_quota_providers", {})
    for raw, ids in surfaces["quota_registry_unmapped"].items():
        if raw not in acknowledged:
            problems.append(
                f"quota registry provider {raw!r} (records {ids}) maps to no onboarded family — "
                "onboard it or acknowledge it in acknowledged_unmapped_quota_providers with a reason")
        elif not str(acknowledged[raw]).strip():
            problems.append(f"quota registry provider {raw!r}: acknowledgement has an empty reason")
    for raw in acknowledged:
        if raw not in surfaces["quota_registry_unmapped"]:
            problems.append(f"stale acknowledgement for quota registry provider {raw!r} — it now maps to a family or is gone; remove the acknowledgement")

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
            "quota_registry": actual["quota_registry"],
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
        "quota_registry_unmapped": surfaces["quota_registry_unmapped"],
        "quota_registry_namespaced_records": surfaces["quota_registry_namespaced_records"],
        "counts": {
            "providers": len(rows),
            "llm": sum(1 for r in rows if r["kind"] == "llm"),
            "review": sum(1 for r in rows if r["kind"] == "review"),
            "with_quota_adapter": sum(1 for r in rows if r["quota_family"] == "implemented_passive_adapter"),
            "with_quota_registry": sum(1 for r in rows if r["quota_registry"]),
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


def _write_registry(root: Path, registry: dict) -> None:
    registry["providers"] = sorted(registry["providers"], key=lambda e: e["provider"])
    (root / "ops/cadence/provider-onboarding.json").write_text(
        json.dumps(registry, indent=2) + "\n", encoding="utf-8")


def autofix(root: Path = ROOT) -> list[str]:
    """Auto-register providers that appeared on a surface without an entry.

    Only the missing-entry class is auto-fixable: kind is inferred from the
    surfaces present, and every missing expected surface is recorded as an
    exception carrying AUTO_EXCEPTION_REASON for review in the auto-extend
    PR. All other drift classes stay hard failures for `check`.
    Returns the list of providers added.
    """
    surfaces = collect_surfaces(root)
    registry = load_registry(root)
    entries = {e["provider"] for e in registry["providers"]}
    added: list[str] = []
    for pid, actual in sorted(surfaces["providers"].items()):
        if pid in entries:
            continue
        kind = "review" if (actual["review_login"] or actual["review_check_app"]) else "llm"
        expected = LLM_SURFACES if kind == "llm" else REVIEW_SURFACES
        entry: dict = {"provider": pid, "kind": kind}
        exceptions = [{"surface": s, "reason": AUTO_EXCEPTION_REASON}
                      for s in expected if not actual[s]]
        if exceptions:
            entry["exceptions"] = exceptions
        registry["providers"].append(entry)
        added.append(pid)
    if added:
        _write_registry(root, registry)
    return added


def apply_onboarding(root: Path, provider: str, kind: str, endpoint: str = "",
                     source: str = "", bot_login: str = "", secret_env: str = "") -> list[str]:
    """Programmatically write a new provider onto every cadence surface.

    Idempotent: a surface that already carries the provider is skipped and
    reported as such. Returns the edit log. Generator post-steps (quota
    coverage feed) are the caller's to run — `main` prints them.
    """
    provider = provider.strip().lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", provider):
        raise ValueError("provider id must be lowercase [a-z0-9_-]")
    if kind == "llm" and (not endpoint or not source):
        raise ValueError("llm apply requires --endpoint and --source (official docs URL)")
    if kind == "review" and not bot_login:
        raise ValueError("review apply requires --bot-login (without the [bot] suffix)")
    if kind not in ("llm", "review"):
        raise ValueError("kind must be 'llm' or 'review'")
    edits: list[str] = []
    registry = load_registry(root)
    if any(e["provider"] == provider for e in registry["providers"]):
        edits.append("registry entry: already present, skipped")
    else:
        registry["providers"].append({"provider": provider, "kind": kind})
        _write_registry(root, registry)
        edits.append("registry entry: added to ops/cadence/provider-onboarding.json")

    if kind == "llm":
        if not endpoint or not source:
            raise ValueError("llm apply requires --endpoint and --source (official docs URL)")
        secret_env = secret_env or f"{provider.upper()}_API_KEY"
        ext_path = root / "scripts/provider_extension_catalogs.py"
        ext = ext_path.read_text(encoding="utf-8")
        if f'"{provider}":' in ext.split("ENDPOINTS = {", 1)[1].split("}", 1)[0]:
            edits.append("catalog endpoint: already present, skipped")
        else:
            ext = ext.replace("ENDPOINTS = {\n",
                              f'ENDPOINTS = {{\n    "{provider}": "{endpoint}",\n', 1)
            ext = ext.replace("SOURCES = {\n",
                              f'SOURCES = {{\n    "{provider}": "{source}",\n', 1)
            ext_path.write_text(ext, encoding="utf-8")
            edits.append("catalog endpoint: added to provider_extension_catalogs ENDPOINTS + SOURCES "
                         "(SECRETS auto-derived by that module)")
        wf_path = root / ".github/workflows/provider-availability.yml"
        wf = wf_path.read_text(encoding="utf-8")
        if f"secrets.{secret_env}" in wf:
            edits.append("availability env: already wired, skipped")
        else:
            anchor = "      GEMINI_HEALTH_MODEL:"
            if anchor not in wf:
                raise ValueError("provider-availability.yml anchor (GEMINI_HEALTH_MODEL) not found")
            wf = wf.replace(anchor, f"      {secret_env}: ${{{{ secrets.{secret_env} }}}}\n" + anchor, 1)
            wf_path.write_text(wf, encoding="utf-8")
            edits.append(f"availability env: wired {secret_env} in provider-availability.yml")
        qm_path = root / "ops/quota/provider-managers.json"
        qm = json.loads(qm_path.read_text(encoding="utf-8"))
        if any(r["provider_family"] == provider for r in qm["provider_families"]):
            edits.append("quota family: already present, skipped")
        else:
            qm["provider_families"].append({
                "provider_family": provider, "status": "public_documentation_only",
                "source": source, "scope": "auto-onboarded; documented scope not yet recorded",
                "reset": "unknown", "signals": []})
            qm["provider_families"] = sorted(qm["provider_families"], key=lambda r: r["provider_family"])
            qm_path.write_text(json.dumps(qm, indent=2) + "\n", encoding="utf-8")
            edits.append("quota family: stub added to ops/quota/provider-managers.json")
        qr_path = root / QUOTA_REGISTRY
        qr = json.loads(qr_path.read_text(encoding="utf-8"))
        if any(s.get("provider", "").lower() == provider and s.get("lane") == "model"
               for s in qr["services"]):
            edits.append("quota registry: model record already present, skipped")
        else:
            qr["services"].append({
                "id": f"{provider}.api", "provider": provider, "lane": "model",
                "metric": "Free tier (auto-onboarded; quota lane to resolve)",
                "limit": None, "unit": "requests", "window": "unknown", "reset": "unknown",
                "zone": "UTC", "source": source, "doc_quote": "NOT ESTABLISHED",
                "live": "none",
                "planned_use": {"safety": 1.0,
                                "note": "auto-onboarded by cadence_provider_onboarding apply; limit not established"}})
            qr_path.write_text(json.dumps(qr, indent=2) + "\n", encoding="utf-8")
            edits.append("quota registry: model-lane record added (limit NOT ESTABLISHED)")
    elif kind == "review":
        if not bot_login:
            raise ValueError("review apply requires --bot-login (without the [bot] suffix)")
        orch_path = root / ".github/workflows/peer-review-orchestrator.yml"
        orch = orch_path.read_text(encoding="utf-8")
        if f"'{provider}'" in orch and f"{bot_login}[bot]" in orch:
            edits.append("orchestrator maps: already present, skipped")
        else:
            login_anchor = "['copilot-pull-request-reviewer[bot]', 'copilot'],"
            app_anchor = "['copilot', 'copilot'],"
            if login_anchor not in orch or app_anchor not in orch:
                raise ValueError("peer-review-orchestrator.yml map anchors not found")
            orch = orch.replace(login_anchor, login_anchor + f"\n              ['{bot_login}[bot]', '{provider}'],", 1)
            orch = orch.replace(app_anchor, app_anchor + f"\n              ['{provider}', '{provider}'],", 1)
            orch_path.write_text(orch, encoding="utf-8")
            edits.append("orchestrator maps: providerLogins + providerCheckApps entries added")
    else:
        raise ValueError("kind must be 'llm' or 'review'")
    return edits


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
    sub.add_parser("autofix", help="auto-register providers missing a registry entry, then render")
    ap = sub.add_parser("apply", help="programmatically onboard a new provider onto every surface")
    ap.add_argument("provider")
    ap.add_argument("--kind", choices=["llm", "review"], required=True)
    ap.add_argument("--endpoint", default="")
    ap.add_argument("--source", default="", help="official docs/rate-limits URL (llm)")
    ap.add_argument("--secret-env", default="")
    ap.add_argument("--bot-login", default="")
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
    if args.cmd == "autofix":
        added = autofix()
        GENERATED.write_text(json.dumps(build_report(), indent=2) + "\n", encoding="utf-8")
        print(f"autofix: added {added if added else 'none'}; matrix re-rendered")
        return 0
    if args.cmd == "apply":
        try:
            edits = apply_onboarding(ROOT, args.provider, args.kind, args.endpoint,
                                     args.source, args.bot_login, args.secret_env)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        for edit in edits:
            print(f"  - {edit}")
        GENERATED.write_text(json.dumps(build_report(), indent=2) + "\n", encoding="utf-8")
        print("  - generated matrix: re-rendered")
        print("post-steps: python3 scripts/provider_quota_coverage.py --output "
              "apps/help-wanted-dashboard/data/provider-quota-coverage.json && "
              "python3 scripts/cadence_provider_onboarding.py check")
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
