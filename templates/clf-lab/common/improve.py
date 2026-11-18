#!/usr/bin/env python3
"""DO advance the DoE: rank finished cells, keep the champion, write the next doe.yaml generation.

Each pass: (1) champion.json ⇐ best ok cell across the ledger (promote iff Δmacro-F1 ≥ min_delta);
(2) when every cell of the current generation has a ledger row, archive doe.yaml under doe/history/
and write generation+1 = neighbors of the top-k cells (±1 level, new edge levels, layer ∧ feature swaps)
plus `explore` untried factor combinations as alternatives. Data pin resets ⇒ next run re-pins master.
"""
from __future__ import annotations

import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import doe_lib  # noqa: E402

LEDGER = ROOT / "results" / "ledger.jsonl"
CHAMP = ROOT / "champion.json"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    doe = yaml.safe_load((ROOT / "doe.yaml").read_text(encoding="utf-8"))
    rows = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()] if LEDGER.exists() else []
    ok = [r for r in rows if r.get("status") == "ok" and r.get("macro_f1") is not None]
    rank = lambda r: (r["macro_f1"], -r.get("macro_f1_std", 0), -r.get("runtime_s", 0))  # noqa: E731
    imp = doe.get("improve", {})
    champ = json.loads(CHAMP.read_text(encoding="utf-8")) if CHAMP.exists() else {}
    if ok:
        best = max(ok, key=rank)
        cur = champ.get("macro_f1", -1.0)
        if not champ or best["macro_f1"] >= cur + imp.get("min_delta", 0.005):
            hist = champ.get("history", [])
            if champ:
                hist.append({k: champ.get(k) for k in ("cell_id", "gen", "macro_f1", "promoted_ts")})
            champ = {k: best.get(k) for k in ("family", "cell_id", "gen", "model", "model_level", "features",
                                              "features_level", "layer", "macro_f1", "macro_f1_std", "acc",
                                              "gold_acc", "n_rows", "data_sha", "commit", "node")}
            champ.update({"promoted_ts": now(), "history": hist[-20:]})
            CHAMP.write_text(json.dumps(champ, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"::notice title=champion::{champ['cell_id']} f1={champ['macro_f1']}")
    gen = doe["generation"]
    done = {r["cell_id"] for r in rows if r.get("gen") == gen}
    pending = [c["id"] for c in doe["cells"] if c["id"] not in done]
    if pending:
        print(f"::notice title=improve::gen={gen} pending={len(pending)} ⇒ hold generation")
        return 0
    gen_ok = sorted([r for r in ok if r.get("gen") == gen], key=rank, reverse=True)
    tried = {doe_lib.signature(r) for r in rows if "model" in r}
    factors = doe["factors"]
    minted: list = []
    proposals, seen = [], set(tried)
    for r in gen_ok[: imp.get("top_k", 3)]:
        for n in doe_lib.neighbors(r, factors, minted):
            n = {k: n[k] for k in ("model", "model_level", "features", "features_level", "layer")}
            sig = doe_lib.signature(n)
            if sig not in seen:
                seen.add(sig)
                proposals.append(n)
    rnd = random.Random(f"{doe['family']}:{gen}")
    rnd.shuffle(proposals)
    budget = doe.get("batch_size", 12)
    k_explore = imp.get("explore", 2)
    cells = proposals[: max(0, budget - k_explore)]
    cells += doe_lib.explore(factors, seen, rnd, budget - len(cells))
    if not cells:
        print("::notice title=improve::design space exhausted at current levels ⇒ hold")
        return 0
    for c in cells:
        c["id"] = doe_lib.cell_id(gen + 1, c)
    hist_dir = ROOT / "doe" / "history"
    hist_dir.mkdir(parents=True, exist_ok=True)
    (hist_dir / f"gen-{gen:04d}.yaml").write_text(yaml.safe_dump(doe, sort_keys=False, allow_unicode=True), encoding="utf-8")
    doe.update({"generation": gen + 1, "data_sha": None, "parent_top": [r["cell_id"] for r in gen_ok[: imp.get("top_k", 3)]],
                "minted_levels": minted, "generated_ts": now(), "cells": cells})
    (ROOT / "doe.yaml").write_text(yaml.safe_dump(doe, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"::notice title=improve::gen {gen}→{gen + 1} cells={len(cells)} minted={len(minted)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
