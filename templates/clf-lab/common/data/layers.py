"""DO load a family's labeled rows and build the data layers {raw, dedup, augmented}.

Rows: {"text": str, "label": str, "tier": "gold"|"silver", "src": str}.
Sources come from data/manifest.json (public termux-monorepo raw paths, pinned per run to one commit).
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "data"
API = "https://api.github.com/repos/{repo}/commits/{ref}"
RAW = "https://raw.githubusercontent.com/{repo}/{sha}/{path}"


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "clf-lab"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok and urllib.parse.urlparse(url).hostname == "api.github.com":
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def resolve_sha(manifest: dict) -> str:
    pin = os.environ.get("CLF_DATA_SHA") or manifest.get("pin_sha")
    if pin:
        return pin
    body = json.loads(_get(API.format(repo=manifest["repo"], ref=manifest.get("ref", "master"))))
    return body["sha"]


def fetch(manifest: dict, sha: str, path: str) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    key = CACHE / (hashlib.sha1(f"{sha}:{path}".encode()).hexdigest() + ".txt")
    if key.exists():
        return key.read_text(encoding="utf-8")
    text = _get(RAW.format(repo=manifest["repo"], sha=sha, path=path)).decode("utf-8")
    key.write_text(text, encoding="utf-8")
    return text


def _bucket(x, edges):
    for e in edges:
        if x <= e:
            return f"le{e}"
    return f"gt{edges[-1]}"


# ---- family adapters: each returns list[row] ---------------------------------

def adapt_classifiers_feed(manifest, sha, src):
    feed = json.loads(fetch(manifest, sha, src["path"]))
    rows = []
    for u in feed.get("units", []):
        text = " | ".join([u.get("name", ""), u.get("group_name", ""), " ; ".join(u.get("outputs", [])),
                           u.get("converged_basis", ""), f"multi_output={len(u.get('outputs', [])) > 1}"])
        rows.append({"text": text, "label": str(u.get(src.get("label_field", "state"))), "tier": "gold",
                     "src": f"{src['path']}#{u.get('id')}"})
    return rows


def adapt_pr_lane_snapshots(manifest, sha, src):
    rows = []
    paths = list(src.get("paths") or [])
    for p in paths:
        snap = json.loads(fetch(manifest, sha, p))
        for pr in snap.get("prs", []):
            gates = pr.get("gates") or {}
            tokens = [f"author={pr.get('author')}", f"base={pr.get('base_ref')}", f"merge={pr.get('mergeable_state')}",
                      f"draft={pr.get('draft')}", f"age={_bucket(pr.get('age_days') or 0, [1, 3, 7, 14, 30, 60])}",
                      f"files={_bucket(pr.get('changed_files') or 0, [1, 3, 10, 30, 100, 1000])}"]
            tokens += [f"gate_{k}={v}" for k, v in sorted(gates.items())]
            rows.append({"text": f"{pr.get('title', '')} || {' '.join(tokens)}", "label": pr.get("lane", "?"),
                         "tier": "gold", "src": f"{p}#pr{pr.get('number')}", "key": f"pr{pr.get('number')}"})
    return rows


def adapt_notation_units(manifest, sha, src):
    rows = []
    for line in fetch(manifest, sha, src["path"]).splitlines():
        if line.strip():
            u = json.loads(line)
            rows.append({"text": f"[{u.get('stratum')}] {u.get('text', '')}", "label": u.get(src.get("label_field", "label")),
                         "tier": "gold", "src": f"{src['path']}#{u.get('unit_id')}"})
    return rows


def adapt_chat_intent(manifest, sha, src):
    """Gold = backfill-v1-v2 rows (v2 label). Silver = chat_intent v2 rules over repo sentences (weak labels)."""
    rows = []
    gold = json.loads(fetch(manifest, sha, src["gold"]))
    for r in gold.get("rows", []):
        rows.append({"text": r["text"], "label": r[src.get("gold_field", "v2")], "tier": "gold", "src": src["gold"]})
    code = fetch(manifest, sha, src["rules"])
    ns: dict = {}
    exec(compile(code, src["rules"], "exec"), ns)  # rules module from the pinned public commit
    classify = ns["classify"]
    seen = {r["text"] for r in rows}
    for sp in src.get("silver_sources", []):
        body = fetch(manifest, sha, sp["path"])
        texts = []
        if sp["kind"] == "units_jsonl":
            for line in body.splitlines():
                if line.strip():
                    u = json.loads(line)
                    if u.get("stratum") in sp.get("strata", [u.get("stratum")]):
                        texts += re.split(r"(?<=[.!?])\s+|\n+", u.get("text", ""))
        elif sp["kind"] == "pr_titles":
            texts = [pr.get("title", "") for pr in json.loads(body).get("prs", [])]
        for t in texts:
            t = re.sub(r"[*`#>]", "", t).strip()
            if 3 <= len(t.split()) <= 40 and t not in seen:
                seen.add(t)
                rows.append({"text": t, "label": classify(t)["intent"], "tier": "silver", "src": sp["path"]})
    return rows


ADAPTERS = {"classifiers_feed": adapt_classifiers_feed, "pr_lane_snapshots": adapt_pr_lane_snapshots,
            "notation_units": adapt_notation_units, "chat_intent": adapt_chat_intent}


def load_rows(manifest: dict) -> tuple[list[dict], str]:
    sha = resolve_sha(manifest)
    rows = []
    for src in manifest["sources"]:
        rows += ADAPTERS[src["adapter"]](manifest, sha, src)
    rows = [r for r in rows if r.get("text") and r.get("label") not in (None, "", "None")]
    return rows, sha


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", t.lower()).strip()


def layer(rows: list[dict], name: str) -> list[dict]:
    """raw ⇒ all rows; dedup ∧ augmented ⇒ one row per normalized text (keep last). Augmentation runs per train fold."""
    if name == "raw":
        return list(rows)
    keyed = {}
    for r in rows:
        keyed[_norm(r["text"])] = r  # later rows (newer snapshots) win
    return list(keyed.values())


def augment(texts, labels, seed=0, copies=1, p_drop=0.15):
    """DO token-dropout ∧ adjacent-swap copies (train fold only ⇒ ∅ leakage)."""
    rnd = random.Random(seed)
    at, al = list(texts), list(labels)
    for _ in range(copies):
        for t, y in zip(texts, labels):
            toks = t.split()
            if len(toks) < 3:
                continue
            toks = [w for w in toks if rnd.random() > p_drop] or toks
            if len(toks) > 2:
                i = rnd.randrange(len(toks) - 1)
                toks[i], toks[i + 1] = toks[i + 1], toks[i]
            at.append(" ".join(toks))
            al.append(y)
    return at, al
