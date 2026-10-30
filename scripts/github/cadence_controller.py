#!/usr/bin/env python3
"""Hourly GitHub Actions gate and quota-aware cadence state controller."""
import argparse
import base64
import datetime as dt
import json
import os
import urllib.error
import urllib.request

UTC = dt.timezone.utc
STATE_PATH = "ops/github-apps/telemetry-cadence-state.json"


def parse_time(value):
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("cadence timestamps must include a timezone")
    return parsed.astimezone(UTC)


def interval_hours(remaining, limit):
    if type(remaining) is not int or type(limit) is not int or limit <= 0 or not 0 <= remaining <= limit:
        raise ValueError("invalid rate-limit headroom")
    ratio = remaining / limit
    if ratio >= 0.75:
        return 3
    if ratio >= 0.50:
        return 6
    if ratio >= 0.25:
        return 12
    return 24


def should_run(state, now=None, force=False):
    if force:
        return True
    due = state.get("next_due_at")
    if not due:
        return True
    return (now or dt.datetime.now(UTC)) >= parse_time(due)


def next_state(document, now=None):
    receipt = document["g4_runtime_receipt"]
    rate = receipt["rate_limit_after"]
    hours = interval_hours(rate["remaining"], rate["limit"])
    observed = parse_time(receipt["observed_at"])
    return {
        "schema_version": 1,
        "last_observed_at": observed.isoformat(),
        "next_due_at": (observed + dt.timedelta(hours=hours)).isoformat(),
        "last_interval_hours": hours,
        "last_remaining": rate["remaining"],
        "last_limit": rate["limit"],
        "last_run_id": receipt["workflow"]["run_id"],
        "last_attempt": receipt["workflow"]["attempt"],
    }


def request_json(url, token, method="GET", payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def persist_state(state, token, repository):
    if not token or not repository or repository.count("/") != 1:
        raise ValueError("GITHUB_TOKEN and owner/name repository are required")
    url = f"https://api.github.com/repos/{repository}/contents/{STATE_PATH}"
    existing = request_json(url, token)
    content = base64.b64encode((json.dumps(state, indent=2, sort_keys=True) + "\n").encode()).decode()
    request_json(url, token, "PUT", {
        "message": "ops(telemetry): update adaptive census cadence",
        "content": content,
        "sha": existing["sha"],
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", default=STATE_PATH)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--record", help="G4 telemetry JSON to record and persist")
    args = parser.parse_args()
    if args.record:
        with open(args.record, encoding="utf-8") as handle:
            document = json.load(handle)
        state = next_state(document)
        persist_state(state, os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY"))
        print(json.dumps(state, sort_keys=True))
        return
    with open(args.state, encoding="utf-8") as handle:
        state = json.load(handle)
    due = should_run(state, force=args.force)
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"due={'true' if due else 'false'}\n")
    print("census due" if due else f"census deferred until {state.get('next_due_at')}")


if __name__ == "__main__":
    main()
