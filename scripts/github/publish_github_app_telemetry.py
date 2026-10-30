#!/usr/bin/env python3
"""Publish sanitized telemetry as an immutable, run-addressed GitHub observation."""
import argparse
import base64
import datetime as dt
import json
import os
import urllib.error
import urllib.request


def publish(document, token, repository, run_id, attempt):
    receipt = document.get("g4_runtime_receipt", {})
    observed = dt.datetime.fromisoformat(receipt["observed_at"].replace("Z", "+00:00"))
    if observed.tzinfo is None:
        raise ValueError("observation timestamp must include timezone")
    identity = receipt.get("workflow", {})
    if identity.get("run_id") != run_id or identity.get("attempt") != attempt:
        raise ValueError("receipt workflow identity does not match publishing run")
    path = f"ops/github-apps/observations/{observed:%Y/%m/%d}/run-{run_id}-attempt-{attempt}.json"
    encoded = base64.b64encode((json.dumps(document, indent=2, sort_keys=True) + "\n").encode()).decode()
    body = json.dumps({
        "message": f"ops(telemetry): publish Collector observation {run_id}/{attempt}",
        "content": encoded,
    }).encode()
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/contents/{path}",
        data=body,
        method="PUT",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"immutable observation publication failed with HTTP {exc.code}") from None
    return path, result.get("commit", {}).get("sha")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    token = os.environ.get("GITHUB_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repository:
        parser.error("GITHUB_TOKEN and GITHUB_REPOSITORY are required")
    run_id = int(os.environ["GITHUB_RUN_ID"])
    attempt = int(os.environ.get("GITHUB_RUN_ATTEMPT", "1"))
    with open(args.input, encoding="utf-8") as handle:
        document = json.load(handle)
    path, commit = publish(document, token, repository, run_id, attempt)
    print(f"Published immutable observation: {path} ({commit})")


if __name__ == "__main__":
    main()
