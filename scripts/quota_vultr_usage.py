#!/usr/bin/env python3
"""Vultr usage collector - wires the vultr provider row into the
quota usage-series (owner order via D2 seat, routed 2026-11-03).

Two burn legs + one balance gap:

1. instances - USD burn = plans-API rate x live instance hours.
   Rates are pulled from https://api.vultr.com/v2/plans AT READ TIME
   (public endpoint, no key). Never hardcode rates here: the D2 prep
   packet's $0.036/$0.071 figures were monthly-cap-derived and STALE
   vs the API's hourly_cost (vhp-2c-4gb-amd $0.033/h,
   vhp-4c-8gb-amd $0.066/h, verified live 2026-11-03). Destroyed
   instances stop the meter: hours run created_at -> destroyed_at
   (or -> now while the instance lives). Known limit: Vultr caps a
   month's charge at monthly_cost; this leg prices raw meter hours
   per the routed formula and does not apply the cap.
2. serverless - USD burn = sum over models of
   (tokens_in x rate_in + tokens_out x rate_out) / 1e6, with the
   per-model rates pulled from the API/Console at read time.
3. account balance - explicit GAP until the owner's Vultr API key
   lands (vault provisioning item, owner's hand in Console).

Legs 1 (instance list) and 2 (usage + rates) need that same account
key (env VULTR_API_KEY, value never printed). Until it lands they
stay state="gap" with the reason recorded - honest blanks, never
invented numbers, and no endpoint is guessed: the serverless usage
endpoint is verified when the key exists, not before.

Output: ops/quota/vultr-usage.json (quota-vultr-usage/v1), consumed
by scripts/quota_usage_pack.py (series5_vultr) and surfaced by
scripts/quota_usage_series.py. The instances leg APPENDS one point
per run ({t, v} = cumulative burn-to-date USD) and preserves prior
points, like the pack's series1 model.

Usage: python3 scripts/quota_vultr_usage.py [--root .]
       [--instances-file PATH] [--now ISO8601]
stdlib only.
"""
import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PLANS_URL = "https://api.vultr.com/v2/plans"
OUT_REL = "ops/quota/vultr-usage.json"
KEY_GAP_REASON = ("account API key not provisioned - owner's Vultr "
                  "API key is a vault provisioning item (Console); "
                  "leg stays an explicit gap until it lands")


def fetch_json(url, token=None):
    req = urllib.request.Request(url, headers={
        "Accept": "application/json", "User-Agent": "quota-vultr-usage"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def pull_plans(fetch=fetch_json):
    """All plans, paginated, indexed by id: {hourly, monthly, type}."""
    rates, url = {}, PLANS_URL
    for _ in range(10):
        d = fetch(url)
        for p in d.get("plans", []):
            rates[p["id"]] = {"hourly": p.get("hourly_cost"),
                              "monthly": p.get("monthly_cost"),
                              "type": p.get("type")}
        nxt = ((d.get("meta") or {}).get("links") or {}).get("next")
        if not nxt:
            break
        url = f"{PLANS_URL}?cursor={nxt}"
    return rates


def parse_ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc)


def instance_burn(inst, rates, now):
    """USD for one instance: hourly rate x meter hours. The meter
    stops at destruction (a stopped-but-alive instance still bills;
    only destroy stops it). Unknown plan or bad stamps -> None."""
    rate = (rates.get(inst.get("plan")) or {}).get("hourly")
    if rate is None or not inst.get("date_created"):
        return None
    start = parse_ts(inst["date_created"])
    end = parse_ts(inst["date_destroyed"]) if inst.get(
        "date_destroyed") else now
    hours = max(0.0, (end - start).total_seconds() / 3600.0)
    return round(hours * rate, 4)


def instances_burn(instances, rates, now):
    per, total, unknown = [], 0.0, 0
    for inst in instances:
        b = instance_burn(inst, rates, now)
        if b is None:
            unknown += 1
            continue
        total += b
        per.append({"id": inst.get("id"), "plan": inst.get("plan"),
                    "burn_usd": b})
    return round(total, 4), per, unknown


def serverless_burn(usage_rows, rates):
    """usage_rows: [{model, tokens_in, tokens_out}]; rates per model
    {in_per_1m, out_per_1m} pulled at read time. -> USD."""
    total = 0.0
    for row in usage_rows:
        r = rates[row["model"]]
        total += (row.get("tokens_in", 0) * r["in_per_1m"]
                  + row.get("tokens_out", 0) * r["out_per_1m"]) / 1e6
    return round(total, 4)


def build(root, now, key=None, instances_file=None, fetch=fetch_json):
    prev = {}
    p = Path(root) / OUT_REL
    if p.exists():
        prev = json.loads(p.read_text())

    doc = {"schema": "quota-vultr-usage/v1",
           "generated_by": "scripts/quota_vultr_usage.py",
           "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ")}

    # Plans leg: public, always pulled at read time. On pull failure
    # keep the prior rates and mark them stale - never invent, never
    # silently present old rates as fresh.
    try:
        rates = pull_plans(fetch)
        doc["plans"] = {"source": PLANS_URL,
                        "pulled_at": doc["generated_at"],
                        "stale": False, "rates": rates}
    except Exception as e:
        old = prev.get("plans") or {}
        doc["plans"] = {"source": PLANS_URL,
                        "pulled_at": old.get("pulled_at"),
                        "stale": True,
                        "stale_reason": f"plans pull failed: {e}",
                        "rates": old.get("rates", {})}
        rates = doc["plans"]["rates"]

    legs = {}

    # Instances leg.
    instances = None
    if instances_file:
        instances = json.loads(
            Path(instances_file).read_text())["instances"]
    elif key:
        try:
            instances = fetch("https://api.vultr.com/v2/instances",
                              key).get("instances", [])
        except Exception as e:
            legs["instances"] = {
                "state": "gap", "unit": "USD", "kind": "estimated",
                "reason": f"instances read failed: {e}"}
    if instances is not None and "instances" not in legs:
        total, per, unknown = instances_burn(instances, rates, now)
        points = list((prev.get("legs") or {}).get(
            "instances", {}).get("points") or [])
        stamp = doc["generated_at"]
        if not points or points[-1].get("t") != stamp:
            points.append({"t": stamp, "v": total})
        leg = {"state": "established", "unit": "USD",
               "kind": "estimated",
               "formula": "sum over instances of plans[plan].hourly "
                          "x meter hours (date_created -> "
                          "date_destroyed|now); destroyed instances "
                          "stop the meter",
               "points": points, "instances": per,
               "burn_to_date_usd": total}
        if unknown:
            leg["unpriced_instances"] = unknown
        legs["instances"] = leg
    elif "instances" not in legs:
        legs["instances"] = {
            "state": "gap", "unit": "USD", "kind": "estimated",
            "formula": "sum over instances of plans[plan].hourly "
                       "x meter hours (date_created -> "
                       "date_destroyed|now)",
            "reason": KEY_GAP_REASON, "points": []}

    # Serverless leg: usage + per-model rates are read-time account
    # data; the usage endpoint is verified once the key exists.
    legs["serverless"] = {
        "state": "gap", "unit": "USD", "kind": "measured",
        "formula": "sum over models of (tokens_in x rate_in + "
                   "tokens_out x rate_out) / 1e6; per-model rates "
                   "pulled from the API/Console at read time",
        "reason": KEY_GAP_REASON if not key else
                  "usage endpoint verification pending (key present; "
                  "no endpoint is guessed)",
        "points": []}

    # Account balance: explicit gap by owner routing until the key.
    legs["account_balance"] = {
        "state": "gap", "unit": "USD",
        "reason": "account-API balance leg stays an explicit gap "
                  "until the owner's API key lands in the vault "
                  "(provisioning item, owner's hand in Console)"}

    doc["legs"] = legs
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--instances-file", default=None)
    ap.add_argument("--now", default=None)
    a = ap.parse_args()
    now = parse_ts(a.now) if a.now else datetime.now(timezone.utc)
    doc = build(a.root, now, key=os.environ.get("VULTR_API_KEY"),
                instances_file=a.instances_file)
    out = Path(a.root) / OUT_REL
    out.write_text(json.dumps(doc, indent=1) + "\n")
    print("vultr-usage:", doc["generated_at"],
          "| plans:", len(doc["plans"]["rates"]),
          "stale" if doc["plans"]["stale"] else "fresh",
          "| instances:", doc["legs"]["instances"]["state"],
          "| serverless:", doc["legs"]["serverless"]["state"])


if __name__ == "__main__":
    sys.exit(main())
