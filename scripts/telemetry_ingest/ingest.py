#!/usr/bin/env python3
"""Telemetry ingest: HindSight (separate) + Provenance (separate).

Reads every telemetry source surface named in sources.json (same directory),
and emits, as two strictly separate sinks:

  provenance -> ops/telemetry/provenance-ledger.jsonl
      One evidence envelope per (source, unit): foresight-spine identities
      (resource_id/item_id/lane_id), source path + SHA-256, evidence_hash
      over canonical JSON. Append-style, deterministic, stdlib only.
  hindsight  -> ops/telemetry/hindsight-payloads.jsonl
      One retain payload per (source, unit), in the repo's HindSight client
      contract shape (deepcli/_v1_hindsight.py: POST /retain with
      {bank_id, content, metadata}). Content carries ids/counts/hashes
      only -- never values, prompts, or credentials.

Plus ops/telemetry/ingest-receipt.json: per-source emitted/partial/skipped
status, coverage of the provider union (quota registry + cadence
onboarding + g4f harvest), and explicit excluded entries (e.g. agent-stack
integrations on HOLD have no live telemetry -- recorded, never dropped
silently, never counted as ingested). Missing sources are `partial`,
never zero/success (docs/ops/AUTOMATED-TELEMETRY-AUDIT.md).

Usage:
  ingest.py [--root .] [--out-dir ops/telemetry] [--now ISO8601]
            [--retain-live] [--check]

--retain-live POSTs each payload to $HINDSIGHT_BASE_URL/retain with
$HINDSIGHT_API_KEY (Bearer) and bank $HINDSIGHT_BANK_ID; absent env =
skipped (recorded in the receipt), HTTP failures recorded per count.
--check regenerates in memory and fails if the committed ledger/payloads
differ (receipt generated_at / live-retain fields are excluded).
"""
from __future__ import annotations

import argparse, hashlib, json, os, re, sys, urllib.request, urllib.error
from pathlib import Path

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{12,}"),
    re.compile(r"\b(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
]

def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def norm_provider(name) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(name).strip().lower()).strip("-")

def guard_no_secrets(text: str, where: str) -> None:
    for pat in SECRET_PATTERNS:
        if pat.search(text):
            raise SystemExit(f"secret-shaped content refused in {where}")

# ---------- extractors: each returns (units, expected_providers) ----------
# unit = {"kind": str, "id": str, "provider": str|None, "records": int|None,
#         "status": "observed"|"skipped", "excluded_reason": str|None}

def _unit(kind, uid, provider, records, status="observed", reason=None):
    return {"kind": kind, "id": str(uid), "provider": norm_provider(provider) if provider else None,
            "records": records, "status": status, "excluded_reason": reason}

def ex_quota_services(data, _path):
    units, expected = [], set()
    for svc in data.get("services", []):
        prov = svc.get("provider") or "unknown"
        expected.add(norm_provider(prov))
        units.append(_unit("quota_service", svc.get("id"), prov, 1))
    return units, expected

def ex_cadence(data, _path):
    units, expected = [], set()
    for p in data.get("providers", []):
        prov = p.get("provider") or "unknown"
        expected.add(norm_provider(prov))
        units.append(_unit("cadence_provider", prov, prov, 1))
    return units, expected

def ex_agent_stack(data, _path):
    units = []
    for integ in data.get("integrations", []):
        status = str(integ.get("status", "")).upper()
        if status in ("HOLD", "REJECT"):
            units.append(_unit("integration", integ.get("id"), integ.get("id"), None,
                               status="skipped",
                               reason=f"agent_stack status={status}: no live telemetry to ingest"))
        else:
            units.append(_unit("integration", integ.get("id"), integ.get("id"), 1))
    return units, set()

def ex_g4f(data, _path):
    units, expected = [], set()
    provs = data.get("providers", [])
    if isinstance(provs, dict):
        items = [{"name": k, **(v if isinstance(v, dict) else {})} for k, v in provs.items()]
    else:
        items = provs
    for p in items:
        name = p.get("name") or p.get("id") or p.get("provider") or "unknown"
        expected.add(norm_provider(name))
        models = p.get("models")
        rec = len(models) if isinstance(models, list) else None
        units.append(_unit("g4f_provider", name, name, rec))
    return units, expected

def ex_generic_json(data, path):
    rec = None
    if isinstance(data, dict):
        rec = len(data)
    elif isinstance(data, list):
        rec = len(data)
    return [_unit("record", Path(path).stem, Path(path).stem, rec)], set()

def ex_github_telemetry_sources(text, _path):
    units = []
    in_sources, seen = False, set()
    for line in text.splitlines():
        if line.startswith("sources:"):
            in_sources = True; continue
        if in_sources:
            m = re.match(r"^  ([A-Za-z0-9_]+):\s*$", line)
            if m and m.group(1) not in seen:
                seen.add(m.group(1))
                units.append(_unit("github_telemetry_source", m.group(1), "github", None))
            elif line and not line.startswith(" "):
                break
    return units, {"github"}

def ex_agent_stream(text, _path):
    units, providers = {}, set()
    n = 0
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        n += 1
        try:
            row = json.loads(line)
        except Exception:
            continue
        prov = row.get("provider") or row.get("model_provider") or "unknown"
        providers.add(norm_provider(prov))
        units.setdefault(norm_provider(prov), 0)
        units[norm_provider(prov)] += 1
    out = [_unit("agent_stream_provider", k, k, v) for k, v in sorted(units.items())]
    if not out:
        out = [_unit("agent_stream", "agent_telemetry_stream", None, n)]
    return out, providers

EXTRACTORS = {
    "quota_services": ex_quota_services,
    "cadence_providers": ex_cadence,
    "agent_stack": ex_agent_stack,
    "g4f_providers": ex_g4f,
    "generic_json": ex_generic_json,
    "github_telemetry_sources": ex_github_telemetry_sources,
    "agent_stream": ex_agent_stream,
    "dashboard_feed": ex_generic_json,
}

def load_source(root: Path, spec: dict):
    """Return (per-file results, expected_providers). Missing = partial."""
    results = []
    if spec.get("glob"):
        files = sorted(root.glob(spec["glob"]))
        files = [f for f in files if f.is_file() and f.suffix in (".json", ".jsonl")]
        if not files:
            return [{"path": spec["glob"], "status": "partial", "units": [], "sha256": None}], set()
        expected = set()
        for f in files:
            res, exp = load_one(root, f, spec)
            results.append(res); expected |= exp
        return results, expected
    f = root / spec["path"]
    if not f.is_file():
        return [{"path": spec["path"], "status": "partial", "units": [], "sha256": None}], set()
    res, exp = load_one(root, f, spec)
    return [res], exp

def load_one(root: Path, f: Path, spec: dict):
    raw = f.read_bytes()
    rel = str(f.relative_to(root)) if f.is_relative_to(root) else str(f)
    ext = spec["extractor"]
    try:
        if ext in ("github_telemetry_sources", "agent_stream") or f.suffix == ".jsonl":
            data = raw.decode(errors="replace")
            if f.suffix == ".jsonl" and ext == "dashboard_feed":
                lines = [ln for ln in data.splitlines() if ln.strip()]
                units = [_unit("record", f.stem, f.stem, len(lines))]
                return {"path": rel, "status": "emitted", "units": units, "sha256": sha256_bytes(raw)}, set()
            units, expected = EXTRACTORS[ext](data, rel)
        else:
            units, expected = EXTRACTORS[ext](json.loads(raw), rel)
        status = "emitted"
    except Exception as exc:  # parse failure = partial, never success
        units, expected, status = [], set(), "partial"
        print(f"warning: {rel}: {exc}", file=sys.stderr)
    return {"path": rel, "status": status, "units": units, "sha256": sha256_bytes(raw)}, expected

def build(root: Path):
    manifest = json.loads((Path(__file__).parent / "sources.json").read_text())
    envelopes, payloads, receipt_sources = [], [], []
    expected, ingested, excluded = set(), set(), []
    for spec in manifest["sources"]:
        results, exp = load_source(root, spec)
        expected |= exp
        for res in results:
            receipt_sources.append({"id": spec["id"], "path": res["path"],
                                    "sha256": res["sha256"], "status": res["status"],
                                    "units": len(res["units"])})
            for u in res["units"]:
                base = {"source_id": spec["id"], "source_path": res["path"],
                        "source_sha256": res["sha256"], "unit_kind": u["kind"],
                        "unit_id": u["id"], "provider": u["provider"],
                        "records": u["records"], "status": u["status"]}
                if u["status"] == "skipped":
                    excluded.append({"source_id": spec["id"], "unit_id": u["id"],
                                     "reason": u["excluded_reason"]})
                elif u["provider"]:
                    ingested.add(u["provider"])
                env = {"schema": "telemetry-provenance/v1", "sink": "provenance",
                       "resource_id": f"telemetry:{spec['id']}:{u['id']}",
                       "item_id": f"telemetry:{spec['id']}:{u['id']}",
                       "lane_id": "telemetry-ingest", **base,
                       "outcome": "ingested" if u["status"] == "observed" else "excluded_recorded"}
                env["evidence_hash"] = sha256_bytes(canonical(env).encode())
                envelopes.append(env)
                content = (f"Telemetry ingest [{spec['id']}] unit={u['id']} kind={u['kind']} "
                           f"provider={u['provider']} records={u['records']} status={u['status']} "
                           f"source={res['path']} source_sha256={res['sha256']} "
                           f"evidence_hash={env['evidence_hash']}")
                if u["status"] == "skipped":
                    content += f" excluded_reason={u['excluded_reason']}"
                payloads.append({"schema": "telemetry-hindsight/v1", "sink": "hindsight",
                                 "bank_id": "${HINDSIGHT_BANK_ID}", "content": content,
                                 "metadata": {"source_id": spec["id"], "unit_id": u["id"],
                                              "provider": u["provider"],
                                              "evidence_hash": env["evidence_hash"]}})
    envelopes.sort(key=lambda e: (e["source_id"], e["unit_id"]))
    payloads.sort(key=lambda p: (p["metadata"]["source_id"], p["metadata"]["unit_id"]))
    missing = sorted(expected - ingested)
    receipt = {"schema": "telemetry-ingest-receipt/v1",
               "sources": receipt_sources,
               "sinks": {"provenance": {"records": len(envelopes),
                                        "path": "ops/telemetry/provenance-ledger.jsonl"},
                         "hindsight": {"payloads": len(payloads),
                                       "path": "ops/telemetry/hindsight-payloads.jsonl",
                                       "live_retain": {"attempted": 0, "ok": 0, "failed": 0,
                                                       "skipped_reason": "not requested"}}},
               "coverage": {"expected_providers": len(expected),
                            "ingested_providers": len(sorted(expected & ingested)),
                            "missing": missing, "excluded": excluded}}
    return envelopes, payloads, receipt

def retain_live(payloads, receipt):
    base = os.environ.get("HINDSIGHT_BASE_URL")
    bank = os.environ.get("HINDSIGHT_BANK_ID")
    live = receipt["sinks"]["hindsight"]["live_retain"]
    if not base or not bank:
        live["skipped_reason"] = "HINDSIGHT_BASE_URL or HINDSIGHT_BANK_ID not set"
        return
    live["skipped_reason"] = None
    key = os.environ.get("HINDSIGHT_API_KEY")
    for p in payloads:
        live["attempted"] += 1
        body = json.dumps({"bank_id": bank, "content": p["content"],
                           "metadata": p["metadata"]}).encode()
        req = urllib.request.Request(base.rstrip("/") + "/retain", data=body,
                                     headers={"Content-Type": "application/json"})
        if key:
            req.add_header("Authorization", f"Bearer {key}")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                live["ok" if resp.status < 400 else "failed"] += 1
        except Exception:
            live["failed"] += 1

def render(envelopes, payloads, receipt, now):
    receipt = dict(receipt); receipt["generated_at"] = now
    prov = "".join(canonical(e) + "\n" for e in envelopes)
    hind = "".join(canonical(p) + "\n" for p in payloads)
    guard_no_secrets(prov, "provenance-ledger")
    guard_no_secrets(hind, "hindsight-payloads")
    return prov, hind, json.dumps(receipt, indent=1, sort_keys=True) + "\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out-dir", default="ops/telemetry")
    ap.add_argument("--now", default="1970-01-01T00:00:00Z")
    ap.add_argument("--retain-live", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    root, out = Path(args.root), Path(args.root) / args.out_dir
    envelopes, payloads, receipt = build(root)
    if args.retain_live:
        retain_live(payloads, receipt)
    prov, hind, rec = render(envelopes, payloads, receipt, args.now)
    if args.check:
        ok = True
        for name, want in (("provenance-ledger.jsonl", prov), ("hindsight-payloads.jsonl", hind)):
            got = (out / name).read_text() if (out / name).is_file() else ""
            if got != want:
                print(f"STALE: {name}", file=sys.stderr); ok = False
        print("check", "PASS" if ok else "FAIL",
              f"provenance={len(envelopes)} hindsight={len(payloads)} "
              f"coverage={receipt['coverage']}")
        return 0 if ok and not receipt["coverage"]["missing"] else 1
    out.mkdir(parents=True, exist_ok=True)
    (out / "provenance-ledger.jsonl").write_text(prov)
    (out / "hindsight-payloads.jsonl").write_text(hind)
    (out / "ingest-receipt.json").write_text(rec)
    print(f"provenance={len(envelopes)} hindsight={len(payloads)} "
          f"coverage={receipt['coverage']['ingested_providers']}/{receipt['coverage']['expected_providers']} "
          f"missing={receipt['coverage']['missing']} excluded={len(receipt['coverage']['excluded'])}")
    return 0 if not receipt["coverage"]["missing"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
