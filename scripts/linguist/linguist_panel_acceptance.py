#!/usr/bin/env python3
"""Acceptance gate for the Linguist Admin Panel (linguist.html vs linguist-panel-feed.json).
Usage: python3 scripts/linguist/linguist_panel_acceptance.py <linguist.html> <linguist-panel-feed.json>
Exit 0 = static gates G1-G4 + layers + feed-absent pass. First run against pre-re-pin master failed exactly G1-G4 + layers (2026-10-27 census); PASS 8/8 on PR #1891/#1892 landed page."""
import json, re, sys
html = open(sys.argv[1] if len(sys.argv)>1 else "linguist.html").read()
feed = json.load(open(sys.argv[2] if len(sys.argv)>2 else "linguist-panel-feed.json"))
checks = []
def ck(name, ok, detail=""): checks.append((name, bool(ok), detail))
ck("G1 fetch path = linguist-panel-feed.json", "data/linguist-panel-feed.json" in html and "linguist-feed.json\"" not in html.replace("linguist-panel-feed.json",""))
ck("G2 flat feed access (feed.data ?? feed fallback or flat)", ("?? feed" in html) or ("feed.data" not in html))
ck("G3 family.table array consumed", bool(re.search(r"(fam|family|f)\.table", html)) and ".from" in html and ".to" in html)
ck("G4 direction_panel used for logic", "direction_panel" in html)
ck("Feed sanity: 15 fam / 288 entries", len(feed["families"])==15 and len(feed["entries"])==288, f'{len(feed["families"])}/{len(feed["entries"])}')
ck("Layers: kind-layer switch present", all(k in html for k in ["cipher","compression","leet","notation","other"]))
ck("Layers: archwiz count-only guarded", "entries_included" in html and "count-only" in html and "disabled" in html)
ck("D feed-absent state retained", "absent" in html.lower() or "not available" in html.lower() or "failed" in html.lower())
for n,ok,d in checks: print(("PASS" if ok else "FAIL"), n, d)
print("RESULT:", "PASS" if all(o for _,o,_ in checks) else "FAIL")
sys.exit(0 if all(o for _,o,_ in checks) else 1)
