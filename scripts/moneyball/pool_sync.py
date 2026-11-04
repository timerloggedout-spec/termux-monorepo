#!/usr/bin/env python3
"""POOL-SYNC — continuous pool provisioning (MoneyBall Dispatch #3).

Walks the sources of record for the pool classes, folds the
wallet-ledger of record through the CUSTODIED fold/verify
(scripts/moneyball/wallet_ledger.py — invoked, never
reimplemented), and appends `wallet_provisioned` events for
NEW pool nodes only. Fail-closed: any source missing or
malformed, any walker whose derivation does not reproduce its
class's existing pools, or any verify error aborts the run
with NO appends.

Walker discipline (self-validating): a class is append-enabled
only when its walker's expected set COVERS every existing pool
of that class on the current ledger (derivation proven against
the record). Otherwise the class is report-only this run.
Classes whose sources are prose snapshots, off-repo, or on the
custodian's batch path are registered census-only: observed
and reported, never auto-provisioned (registration is data —
a structured source upgrades a class by editing WALKERS).

Depth rule (Amendment 3): one pool per entity at EACH depth of
its source taxonomy; depth + parent carried on the event; pool
ids are path-shaped (pool:<class>:<parent-slug>/<entity> is
expressed in the flat ledger as pool:<class>:<entity> with
parent_wallet naming the parent — the ledger's own convention).

Custody: Swarm (Optimizations & Implementation Assurance)
builds/runs this mechanism; the ledger fold stays
Speculators-build custody (wallet_ledger.py); the census
snapshot lands beside the ledger at
ops/agentic-gambling/site/pool-census.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wallet_ledger as wl  # custodied fold/verify — invoked only

LEDGER = Path("ops/agentic-gambling/site/wallet-ledger.jsonl")
CENSUS = Path("ops/agentic-gambling/site/pool-census.json")

RULE = ("POOL-SYNC continuous provisioning (MoneyBall Dispatch #3, "
        "Web3 release 2026-11-03); Amendment 3 depth rule; "
        "existence only — balances stay measured-0 at provisioning")

# Census-only classes: source of record named; pools observed,
# never auto-provisioned by this mechanism in v1.
CENSUS_ONLY = {
    "moniker": "docs/ops/AGENT-MONIKERS.md (SSOT moniker tables)",
    "role": "docs/ops/AGENT-MONIKERS.md (role table + naming-collapse registry)",
    "profile": "docs/ops/PROFILE-REGISTRY.md §2",
    "doe": "docs/ops/DOE-FAMILY.md register + docs/ops/DOE-DREAMBEANS-POOL.md census",
    "recon": "docs/ops/PROVIDER-AND-LANE-ENUMERATION-AUDIT (snapshot doc)",
    "researcher": "Registry SSOT + people of record (narrative source)",
    "devwork": "GitHub repo census (live API) + goal workspaces census",
    "version": "moneyball VERSIONS.md (cross-repo source)",
    "arm": "DOE-FAMILY selection-arm taxonomy — custodian batch path "
           "(POOL-SYNC option (b): batch-provisioned, sweep-caught)",
    "loop": "owner amendment-5 taxonomy + cull-waterfall rule — custodian "
            "batch path (POOL-SYNC option (b))",
    "explorer": "owner pool-scope directive (single entity)",
    "other": "ops/agentic-gambling/lane.json pooled buckets",
    "(card)": "moneyball DESIGN §3 card pools (grandfathered unscoped)",
    "provider-depth3+": "provider-phrases/phrases.json prefixes "
                        "(depth>=3 legs registered, walker follow-on)",
}


def _load_json(path):
    return json.loads(Path(path).read_text())


def walk_que_lane(root):
    feed = _load_json(root / "apps/tribute-dashboard/data/dispatch-tree-feed.json")
    return {f"pool:que-lane:{lane['lane']}": {"entity_ref": lane["lane"]}
            for lane in feed["data"]["lanes"]}


def walk_provider(root):
    expected = {}
    onboard = _load_json(root / "ops/cadence/provider-onboarding.json")
    for p in onboard.get("providers", []):
        slug = wl._slug(p["provider"])
        expected[f"pool:provider:{slug}"] = {"entity_ref": slug}
    for name in (onboard.get("acknowledged_unmapped_quota_providers") or {}):
        slug = wl._slug(name)
        expected[f"pool:provider:{slug}"] = {"entity_ref": slug}
    feed = _load_json(root / "ops/challenge/desk-feed.json")
    catalog = feed.get("dispatch", {}).get("provider_catalog", {})
    avail = catalog.get("inference_availability", {})
    records = avail.get("records", []) if isinstance(avail, dict) else []
    seen_ids = set()
    for r in records:
        if r["id"] in seen_ids:
            continue
        seen_ids.add(r["id"])
        entity = r["id"].replace(".", "-").replace("_", "-")
        entity = wl._slug(entity)
        parent = wl._slug(r["provider"])
        expected[f"pool:provider:{entity}"] = {
            "entity_ref": entity, "display": r["id"], "depth": 2,
            "parent_entity": parent, "parent_wallet": f"pool:provider:{parent}"}
    return expected


def walk_speculator(root):
    expected = {}
    wallets = _load_json(
        root / "experiments/speculators/token-strategies/WALLETS.json")
    for w in wallets.get("wallets", []):
        name = w.get("participant") or w.get("model") or w.get("name")
        if not name:
            continue
        slug = wl._slug(name)
        expected[f"pool:speculator:{slug}"] = {"entity_ref": slug}
    plan = _load_json(
        root / "experiments/speculators/token-strategies/PLAN.json")
    for row in plan.get("rows", []):
        inst = row.get("instance") or {}
        model = inst.get("model")
        cell = row.get("cell")
        task = row.get("task") or row.get("task_id")
        if not model or not cell:
            continue
        parent = wl._slug(model)
        entity = f"{parent}--{cell}"
        if task:
            entity += f"--{wl._slug(task)}"
        expected[f"pool:speculator:{entity}"] = {
            "entity_ref": entity, "depth": 2,
            "parent_entity": parent,
            "parent_wallet": f"pool:speculator:{parent}"}
    return expected


def walk_desk_lane(root):
    expected = {}
    coord = _load_json(root / "ops/challenge/coordinator.json")
    for ev in coord.get("events", []):
        slug = wl._slug(ev.get("id", ""))
        if slug:
            expected[f"pool:desk-lane:{slug}-desk"] = {
                "entity_ref": f"{slug}-desk"}
    expected["pool:desk-lane:contribution-desk"] = {
        "entity_ref": "contribution-desk"}
    return expected


WALKERS = {
    "que-lane": {"source": "apps/tribute-dashboard/data/dispatch-tree-feed.json "
                           "data.lanes", "walk": walk_que_lane,
                 "exclude": None},
    "provider": {"source": "ops/cadence/provider-onboarding.json + ops/challenge/"
                           "desk-feed.json provider_catalog."
                           "inference_availability.records",
                 "walk": walk_provider,
                 # depth>=3 legs are the registered census-only sub-scope
                 "exclude": lambda e: (e.get("depth") or 0) >= 3},
    "speculator": {"source": "experiments/speculators/token-strategies/"
                             "WALLETS.json + PLAN.json rows",
                   "walk": walk_speculator, "exclude": None},
    "desk-lane": {"source": "ops/challenge/coordinator.json events + "
                            "desk-feed desk",
                  "walk": walk_desk_lane, "exclude": None},
}

STYLES = {
    "pro_rata": "active",
    "capped": {"state": "NOT_ESTABLISHED",
               "note": "cap multiple unruled; activates when ruled "
                       "(DESIGN §3.1)"},
    "first_loss": {"state": "gated",
                   "note": "activation requires >=1 settled pool cycle "
                           "+ owner ruling (DESIGN §3.1)"},
}


def main():
    commit = "--commit" in sys.argv
    root = Path(".")
    events = wl.load(str(root / LEDGER))
    errs, _balances, _genesis = wl.verify(events)
    if errs:
        print(f"FAIL-CLOSED: ledger verify errors: {errs[:3]}")
        return 1
    existing = {}
    for e in events:
        if e.get("class") == "pool":
            existing[e["wallet_id"]] = e
    by_class = {}
    for wid, e in existing.items():
        by_class.setdefault(e.get("pool_class", "(card)"), set()).add(wid)

    receipt = {"ledger_events": len(events), "pools_existing": len(existing),
               "walked": {}, "census_only": {}, "new": []}
    candidates = []
    for cls, spec in WALKERS.items():
        source, walker = spec["source"], spec["walk"]
        try:
            expected = walker(root)
        except Exception as exc:  # fail-closed on any walker error
            print(f"FAIL-CLOSED: walker {cls} errored: {exc}")
            return 1
        exp_ids = set(expected.keys())
        have = by_class.get(cls, set())
        if spec.get("exclude"):
            have = {wid for wid in have if not spec["exclude"](existing[wid])}
        missing_from_walk = have - exp_ids
        new = exp_ids - have
        proven = not missing_from_walk
        receipt["walked"][cls] = {
            "source": source, "expected": len(exp_ids),
            "existing": len(have), "derivation_proven": proven,
            "unwalked_existing": sorted(missing_from_walk)[:5],
            "new": sorted(new)}
        if proven:
            for wid in sorted(new):
                candidates.append((wid, cls, source, expected[wid]))
        elif new:
            print(f"NOTE: {cls} walker unproven (misses "
                  f"{len(missing_from_walk)} existing) — report-only")
    for cls, source in CENSUS_ONLY.items():
        key = None if cls == "(card)" else cls
        receipt["census_only"][cls] = {
            "source": source,
            "existing": len(by_class.get(key, set())) if key else 4}
    receipt["census_only"]["provider-depth3+"]["existing"] = sum(
        1 for e in existing.values()
        if e.get("pool_class") == "provider" and (e.get("depth") or 0) >= 3)

    if candidates and commit:
        prev = events[-1]["receipt"]["payload_hash"]
        seq = len(events)
        ts = __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        lines = []
        for wid, cls, source, meta in candidates:
            seq += 1
            ev = {"seq": seq, "ts": ts, "type": "wallet_provisioned",
                  "wallet_id": wid, "class": "pool", "pool_class": cls,
                  "entity_ref": meta["entity_ref"], "kind": "paper|test",
                  "unit": "soft_quota_token (observational)",
                  "delta": 0, "balance_after": 0, "members": 0,
                  "styles": STYLES,
                  "ref": {"kind": "pool_sync", "source": source,
                          "rule": RULE}}
            for k in ("display", "depth", "parent_entity", "parent_wallet"):
                if k in meta:
                    ev[k] = meta[k]
            h = wl.payload_hash(ev)
            ev["receipt"] = {"receipt_id": f"wr-{seq:04d}-{h[:12]}",
                             "wallet_id": wid, "event_seq": seq,
                             "payload_hash": h, "prev_receipt_hash": prev}
            prev = h
            events.append(ev)
            lines.append(json.dumps(ev, sort_keys=True))
            receipt["new"].append(wid)
        errs2, _b, _g = wl.verify(events)
        if errs2:
            print(f"FAIL-CLOSED: post-append verify errors: {errs2[:3]}")
            return 1
        with open(root / LEDGER, "a") as fh:
            fh.write("\n".join(lines) + "\n")
    elif candidates:
        receipt["new"] = [c[0] for c in candidates]
        print("DRY-RUN: candidates not appended")

    census = {"schema": "moneyball-pool-census/v1",
              "ledger_events": len(events),
              "pools": len(existing) + len(receipt["new"]),
              "by_class": {k: len(v) for k, v in sorted(by_class.items())},
              "walked": receipt["walked"],
              "census_only": receipt["census_only"],
              "new_this_run": receipt["new"]}
    old = None
    if (root / CENSUS).exists():
        old = json.loads((root / CENSUS).read_text())
    comparable = {k: v for k, v in census.items()}
    if old and all(old.get(k) == v for k, v in comparable.items()
                   if k != "walked"):
        print("census unchanged — snapshot not rewritten")
    elif commit:
        (root / CENSUS).write_text(json.dumps(census, indent=1) + "\n")
        print("census snapshot written")
    print(json.dumps({"pools_existing": receipt["pools_existing"],
                      "new": receipt["new"],
                      "walked": {k: (v["expected"], v["existing"],
                                     v["derivation_proven"])
                                 for k, v in receipt["walked"].items()}},
                     indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
