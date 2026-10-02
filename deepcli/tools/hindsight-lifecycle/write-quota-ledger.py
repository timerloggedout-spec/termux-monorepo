#!/usr/bin/env python3
"""write-quota-ledger — aggregate all provider quotas into one JSON.

Sources:
  GitHub billing  -> gh api /users/{u}/settings/billing/usage
  Gemini          -> limits.json probe cache + state.json counters
  OpenRouter      -> /api/v1/auth/key + /credits (live)
Output:
  ~/.deepcli/logs/quota-ledger.json
"""
import json, os, subprocess, urllib.request
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
OUT = HOME / ".deepcli/logs/quota-ledger.json"

FREE = {
    "codespaces_compute_core_hours": 120.0,
    "codespaces_storage_gb_month":   15.0,
    "actions_linux_minutes":         2000.0,
    "actions_windows_minutes":       1000.0,
    "actions_macos_minutes":         200.0,
    "actions_storage_gb_hours":      500.0 * 24,  # 500 MB-month approximate, but API gives GB-h
    "packages_storage_gb_hours":     500.0 * 24,
    "gemini_rpd_flash_lite":         500.0,
    "openrouter_rpd_free":           50.0,
}

def next_reset_utc():
    n = datetime.now(timezone.utc)
    nx = datetime(n.year+1,1,1,tzinfo=timezone.utc) if n.month==12 else datetime(n.year,n.month+1,1,tzinfo=timezone.utc)
    return nx

def gh_billing():
    be = HOME / ".config/gh/broker.env"
    if not be.exists(): return None
    tok = ""
    for line in be.read_text().splitlines():
        if "GH_BROKER_TOKEN" in line:
            tok = line.split("=",1)[1].strip().strip('"').strip("'").replace("export ","")
            break
    if not tok: return None
    n = datetime.now(timezone.utc)
    url = f"https://api.github.com/users/timerloggedout-spec/settings/billing/usage?year={n.year}&month={n.month}"
    req = urllib.request.Request(url, headers={"Authorization": f"token {tok}", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except Exception:
        return None

def agg_github(items):
    out = {"codespaces_compute_hours":0.0, "codespaces_compute_sku":"",
           "codespaces_storage_gb_hours":0.0,
           "actions_linux_minutes":0.0, "actions_slim_minutes":0.0,
           "actions_windows_minutes":0.0, "actions_macos_minutes":0.0,
           "actions_storage_gb_hours":0.0, "gross_usd":0.0, "net_usd":0.0}
    for i in items:
        p = (i.get("product") or "").lower()
        s = (i.get("sku") or "").lower()
        q = float(i.get("quantity") or 0)
        g = float(i.get("grossAmount") or 0)
        nt = float(i.get("netAmount") or 0)
        out["gross_usd"] += g; out["net_usd"] += nt
        if "codespaces" in p:
            if "compute" in s:
                out["codespaces_compute_hours"] += q
                out["codespaces_compute_sku"] = i.get("sku","")
            elif "storage" in s:
                out["codespaces_storage_gb_hours"] += q
        elif "actions" in p:
            if "linux" in s and "slim" in s: out["actions_slim_minutes"] += q
            elif "linux" in s: out["actions_linux_minutes"] += q
            elif "windows" in s: out["actions_windows_minutes"] += q
            elif "macos" in s: out["actions_macos_minutes"] += q
            elif "storage" in s: out["actions_storage_gb_hours"] += q
    # compute core-hours from SKU: 4-core SKU * hours
    if "4-core" in out["codespaces_compute_sku"]:
        out["codespaces_compute_core_hours"] = out["codespaces_compute_hours"] * 4
    elif "8-core" in out["codespaces_compute_sku"]:
        out["codespaces_compute_core_hours"] = out["codespaces_compute_hours"] * 8
    elif "2-core" in out["codespaces_compute_sku"]:
        out["codespaces_compute_core_hours"] = out["codespaces_compute_hours"] * 2
    else:
        out["codespaces_compute_core_hours"] = out["codespaces_compute_hours"] * 2
    return out

def openrouter():
    tok = ""
    for p in [HOME / ".config/gh/broker.env", HOME / ".deepcli/hindsight.env"]:
        if p.exists():
            for line in p.read_text().splitlines():
                if line.startswith("OPENROUTER_API_KEY="):
                    tok = line.split("=",1)[1].strip().strip('"').strip("'")
                    break
    if not tok: return {}
    out = {}
    try:
        req = urllib.request.Request("https://openrouter.ai/api/v1/auth/key", headers={"Authorization": f"Bearer {tok}"})
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.load(r).get("data") or {}
            out["limit"] = d.get("limit")
            out["usage"] = d.get("usage")
            out["remaining"] = d.get("limit_remaining")
            rl = d.get("rate_limit") or {}
            out["rpm"] = rl.get("requests")
    except Exception: pass
    try:
        req = urllib.request.Request("https://openrouter.ai/api/v1/credits", headers={"Authorization": f"Bearer {tok}"})
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.load(r).get("data") or {}
            out["credits_total"] = d.get("total_credits")
            out["credits_used"] = d.get("total_usage")
    except Exception: pass
    return out

def gemini_usage():
    lim = HOME.parent / "tmp" / "hs-stack" / "limits.json"
    st  = HOME.parent / "tmp" / "hs-stack" / "state.json"
    out = {"probe_cache_models": 0, "available_200": 0, "per_model": {}}
    # on Termux, /tmp doesn't exist; use the codespace path if we're not there
    for p in [Path("/tmp/hs-stack/limits.json"), HOME / ".deepcli/tmp/hs-stack/limits.json"]:
        if p.exists():
            try:
                d = json.loads(p.read_text())
                ms = d.get("models") or {}
                out["probe_cache_models"] = len(ms)
                out["available_200"] = sum(1 for m in ms.values() if m.get("http")==200)
                out["per_model"] = {k:{"http":v.get("http"),"rpd":v.get("rpd",0)} for k,v in ms.items()}
            except Exception: pass
            break
    for p in [Path("/tmp/hs-stack/state.json"), HOME / ".deepcli/tmp/hs-stack/state.json"]:
        if p.exists():
            try:
                d = json.loads(p.read_text())
                out["state"] = d
            except Exception: pass
            break
    return out

print("gathering…")
b = gh_billing()
gh = agg_github(b.get("usageItems", [])) if b else {}
orq = openrouter()
gem = gemini_usage()
reset = next_reset_utc()

ledger = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "next_reset_utc": reset.isoformat(),
    "days_until_reset": (reset - datetime.now(timezone.utc)).days,
    "github": gh,
    "openrouter": orq,
    "gemini": gem,
    "free_tier": FREE,
    "gates": {
        "codespaces_compute": {
            "used": gh.get("codespaces_compute_core_hours", 0),
            "limit": FREE["codespaces_compute_core_hours"],
            "pct": 100 * gh.get("codespaces_compute_core_hours", 0) / FREE["codespaces_compute_core_hours"],
            "reset": reset.isoformat(),
        },
        "codespaces_storage": {
            "used": gh.get("codespaces_storage_gb_hours", 0) / 720.0,  # -> gb-month approx
            "limit": FREE["codespaces_storage_gb_month"],
            "reset": reset.isoformat(),
        },
        "actions_linux": {
            "used": gh.get("actions_linux_minutes", 0),
            "limit": FREE["actions_linux_minutes"],
            "pct": 100 * gh.get("actions_linux_minutes", 0) / FREE["actions_linux_minutes"],
            "reset": reset.isoformat(),
        },
        "openrouter_rpd": {
            "used": orq.get("usage", 0),
            "limit": orq.get("limit") or FREE["openrouter_rpd_free"],
            "remaining": orq.get("remaining"),
            "reset": reset.isoformat(),
        },
    },
    "would_have_paid_usd": gh.get("gross_usd", 0),
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(ledger, indent=2, default=str))
print(f"wrote {OUT}")
print(f"  codespaces compute: {gh.get('codespaces_compute_core_hours',0):.1f} / {FREE['codespaces_compute_core_hours']:.0f} core-h ({ledger['gates']['codespaces_compute']['pct']:.1f}%)")
print(f"  actions linux:      {gh.get('actions_linux_minutes',0):.0f} / {FREE['actions_linux_minutes']:.0f} min")
print(f"  would-have-paid:    ${gh.get('gross_usd',0):.2f}")
print(f"  reset in:           {ledger['days_until_reset']}d")
