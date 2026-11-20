#!/usr/bin/env python3
import json, os, sys, datetime

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ALLOC_PATH = os.path.join(BASE, "quota/allocations.json")
REG_PATH   = os.path.join(BASE, "quota/registry.json")

alloc = json.load(open(ALLOC_PATH))
reg   = json.load(open(REG_PATH))

def today_key():
    tz = datetime.timezone(datetime.timedelta(hours=-8))  # PT
    return datetime.datetime.now(tz).strftime("%Y-%m-%d")

def counter_path(provider):
    return f"/tmp/quota/{provider}/{today_key()}.txt"

def load_counter(provider):
    p = counter_path(provider)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    try:
        return int(open(p).read())
    except FileNotFoundError:
        return 0

def save_counter(provider, n):
    open(counter_path(provider), "w").write(str(n))

def main():
    provider = "google_ai_studio"
    used = load_counter(provider)
    limit = alloc["providers"][provider]["free_allowance"]["RPD"]
    if used >= limit:
        print(f"❌ {provider} RPD quota exhausted ({used}/{limit})", file=sys.stderr)
        sys.exit(3)  # smooth‑flow guard
    save_counter(provider, used + 1)
    sys.exit(0)

if __name__ == "__main__":
    main()
