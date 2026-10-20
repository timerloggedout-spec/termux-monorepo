#!/usr/bin/env python3
"""MSM-012: observe credential names, never retrieve or serialize secret values.

Only the fixed production repository's metadata endpoint is contacted. Run from
trusted default-branch Actions with an existing authorized administration token.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import tempfile
import sys
import urllib.error
import urllib.request

try:
    from scripts import provider_model_catalog
except ImportError:
    # Actions invokes this file directly; resolve only the checked-out scripts.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import provider_model_catalog  # type: ignore

API = "https://api.github.com/repos/timerloggedout-spec/termux-monorepo/actions/secrets"
MAX_PAGES = 20


def provider_credentials(names) -> list[dict]:
    """Map recognized secret names to catalog providers without exposing values."""
    recognized = set(names)
    entries = []
    for provider, canonical in provider_model_catalog.SECRETS.items():
        aliases = provider_model_catalog.SECRET_ALIASES.get(provider, (canonical,))
        # Catalog aliases are authoritative; canonical is always recognized.
        recognized_aliases = tuple(dict.fromkeys((canonical, *aliases)))
        configured = [name for name in recognized_aliases if name in recognized]
        entries.append({
            "provider": provider,
            "environment_variable": canonical,
            "configured_secret_names": configured,
            "status": "configured_entitlement_unverified" if configured else "missing_secret",
        })
    return entries


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def observe(token: str | None) -> dict:
    report = {"schema": "provider-secret-names/v1", "repository": "timerloggedout-spec/termux-monorepo",
              "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
              "status": "unavailable", "reason": "missing_inventory_credential", "names": []}
    if not token:
        return report
    opener = urllib.request.build_opener(NoRedirect)
    names = set()
    try:
        for page in range(1, MAX_PAGES + 1):
            request = urllib.request.Request(f"{API}?per_page=100&page={page}", headers={
                "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "provider-secret-names/1"})
            with opener.open(request, timeout=30) as response:
                body = response.read(1024 * 1024 + 1)
            if len(body) > 1024 * 1024:
                raise ValueError("response_too_large")
            payload = json.loads(body)
            if not isinstance(payload, dict) or not isinstance(payload.get("secrets"), list):
                raise ValueError("invalid_response")
            rows = payload["secrets"]
            for row in rows:
                name = row.get("name") if isinstance(row, dict) else None
                if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,255}", name):
                    raise ValueError("invalid_name")
                names.add(name)
            if len(rows) < 100:
                report.update(status="observed", reason=None, names=sorted(names),
                              provider_credentials=provider_credentials(names))
                return report
        raise ValueError("pagination_limit")
    except urllib.error.HTTPError as exc:
        report["reason"] = f"http_status_{exc.code}"
    except (OSError, ValueError, TypeError):
        # Never serialize exception bodies/URLs/headers or any response fields.
        report["reason"] = "inventory_transport_or_response_failure"
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    report = observe(os.environ.get("GH_TOKEN"))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temporary = handle.name
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)
    print(json.dumps({"status": report["status"], "reason": report["reason"], "name_count": len(report["names"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
