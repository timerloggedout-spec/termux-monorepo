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
import urllib.error
import urllib.request

API = "https://api.github.com/repos/timerloggedout-spec/termux-monorepo/actions/secrets"
MAX_PAGES = 20


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
                report.update(status="observed", reason=None, names=sorted(names))
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
