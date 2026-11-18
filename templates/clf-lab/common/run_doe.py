#!/usr/bin/env python3
"""DO run one batch of DoE cells from doe.yaml ∧ append results to results/ledger.jsonl.

Usage: python run_doe.py [--node NAME] [--max-cells N] [--budget-s 900] [--cell CELL_ID]
CPU-only (2 vCPU / ~1 GiB). Cells already in the ledger for the same generation ∧ data sha are skipped,
so any node (Actions, Hark VM, Muse) can claim the next unrun cells.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import yaml
from joblib import Memory
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.feature_extraction.text import HashingVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "data"))
import layers  # noqa: E402

LEDGER = ROOT / "results" / "ledger.jsonl"
MEM = Memory(str(ROOT / ".cache" / "features"), verbose=0)
MIN_CLASS = 3


def git_sha() -> str:
    env = os.environ.get("GITHUB_SHA")
    if env:
        return env
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip() or "local"
    except OSError:
        return "local"


def build_features(kind: str, level: dict):
    if kind == "tfidf-word":
        return TfidfVectorizer(ngram_range=(1, level.get("ngram_max", 2)), min_df=1, sublinear_tf=True,
                               max_features=level.get("max_features", 20000))
    if kind == "tfidf-char":
        return TfidfVectorizer(analyzer="char_wb", ngram_range=(2, level.get("ngram_max", 5)), sublinear_tf=True,
                               max_features=level.get("max_features", 30000))
    if kind == "hashing":
        return make_pipeline(HashingVectorizer(ngram_range=(1, level.get("ngram_max", 2)), alternate_sign=False,
                                               n_features=2 ** level.get("log2_features", 16), norm=None),
                             TfidfTransformer(sublinear_tf=True))
    raise ValueError(kind)


def build_model(kind: str, level: dict, seed: int):
    if kind == "logreg":
        return LogisticRegression(C=level.get("C", 1.0), max_iter=2000, class_weight="balanced")
    if kind == "linear-svm":
        return LinearSVC(C=level.get("C", 1.0), class_weight="balanced")
    if kind == "nb":
        return ComplementNB(alpha=level.get("alpha", 0.5))
    if kind == "small-gbm":
        return make_pipeline(TruncatedSVD(n_components=level.get("svd", 64), random_state=seed),
                             HistGradientBoostingClassifier(max_iter=level.get("max_iter", 100),
                                                            learning_rate=level.get("lr", 0.1),
                                                            max_depth=level.get("max_depth", 3),
                                                            class_weight="balanced", random_state=seed))
    raise ValueError(kind)


@MEM.cache
def _rows_cached(manifest_json: str, sha: str):
    m = json.loads(manifest_json)
    m["pin_sha"] = sha
    return layers.load_rows(m)[0]


def evaluate(cell: dict, rows: list[dict], cfg: dict) -> dict:
    seed = cfg.get("seed", 7)
    data = layers.layer(rows, cell["layer"])
    gold = [r for r in data if r.get("tier", "gold") == "gold"]
    silver = [r for r in data if r.get("tier") == "silver"]
    pool = data
    labels = [r["label"] for r in pool]
    counts = {c: labels.count(c) for c in set(labels)}
    keep = {c for c, n in counts.items() if n >= MIN_CLASS}
    pool = [r for r in pool if r["label"] in keep]
    X = np.array([r["text"] for r in pool], dtype=object)
    y = np.array([r["label"] for r in pool])
    n_splits = max(2, min(cfg.get("folds", 5), min(counts[c] for c in keep)))
    cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=cfg.get("repeats", 2), random_state=seed)
    f1s, accs = [], []
    for i, (tr, te) in enumerate(cv.split(X, y)):
        xt, yt = list(X[tr]), list(y[tr])
        if cell["layer"] == "augmented":
            xt, yt = layers.augment(xt, yt, seed=seed + i, copies=cfg.get("aug_copies", 1))
        pipe = make_pipeline(build_features(cell["features"], cell.get("features_level", {})),
                             build_model(cell["model"], cell.get("model_level", {}), seed))
        pipe.fit(xt, yt)
        pred = pipe.predict(list(X[te]))
        f1s.append(f1_score(y[te], pred, average="macro", zero_division=0))
        accs.append(accuracy_score(y[te], pred))
    out = {"macro_f1": round(float(np.mean(f1s)), 4), "macro_f1_std": round(float(np.std(f1s)), 4),
           "acc": round(float(np.mean(accs)), 4), "folds": n_splits, "n_rows": len(pool),
           "n_classes": len(keep), "dropped_classes": sorted(set(counts) - keep)}
    if gold and silver:  # silver-trained model scored on gold rows (bf-1 transfer check)
        gl = [r for r in gold if r["label"] in keep]
        if gl:
            pipe = make_pipeline(build_features(cell["features"], cell.get("features_level", {})),
                                 build_model(cell["model"], cell.get("model_level", {}), seed))
            pipe.fit([r["text"] for r in silver if r["label"] in keep], [r["label"] for r in silver if r["label"] in keep])
            out["gold_acc"] = round(float(accuracy_score([r["label"] for r in gl], pipe.predict([r["text"] for r in gl]))), 4)
            out["n_gold"] = len(gl)
    return out


def done_keys() -> set:
    keys = set()
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                keys.add((r.get("gen"), r.get("cell_id"), r.get("data_sha")))
    return keys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", default=os.environ.get("CLF_NODE", "actions"))
    ap.add_argument("--max-cells", type=int, default=None)
    ap.add_argument("--budget-s", type=int, default=900)
    ap.add_argument("--cell", default=None, help="run one cell id only")
    a = ap.parse_args()
    budget = min(a.budget_s, 900)
    doe = yaml.safe_load((ROOT / "doe.yaml").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))
    cfg = doe.get("eval", {})
    sha = doe.get("data_sha") or layers.resolve_sha(manifest)
    if not doe.get("data_sha"):  # pin the generation to one data commit ⇒ cells stay comparable within a gen
        doe["data_sha"] = sha
        (ROOT / "doe.yaml").write_text(yaml.safe_dump(doe, sort_keys=False, allow_unicode=True), encoding="utf-8")
    rows = _rows_cached(json.dumps(manifest, sort_keys=True), sha)
    done = done_keys()
    cells = [c for c in doe["cells"] if (doe["generation"], c["id"], sha) not in done]
    if a.cell:
        cells = [c for c in cells if c["id"] == a.cell]
    cap = a.max_cells or doe.get("batch_size", len(cells))
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    t0, ran = time.time(), 0
    for cell in cells[:cap]:
        if time.time() - t0 > budget:
            print(f"::notice title=budget::stop at {ran} cells (≥{budget}s)")
            break
        c0 = time.time()
        try:
            metrics = evaluate(cell, rows, cfg)
            status = "ok"
        except Exception as e:  # record the failed cell ⇒ improve.py skips it
            metrics, status = {"error": f"{type(e).__name__}: {e}"[:300]}, "error"
        rec = {"ts_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "family": doe["family"],
               "gen": doe["generation"], "cell_id": cell["id"], "model": cell["model"],
               "model_level": cell.get("model_level", {}), "features": cell["features"],
               "features_level": cell.get("features_level", {}), "layer": cell["layer"], "status": status,
               **metrics, "runtime_s": round(time.time() - c0, 2), "data_sha": sha, "commit": git_sha(),
               "node": a.node, "host": platform.node()}
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        ran += 1
        print(f"{cell['id']}: {status} f1={metrics.get('macro_f1')} acc={metrics.get('acc')} {rec['runtime_s']}s")
    left = max(0, len(cells) - ran)
    print(f"::notice title=run_doe::node={a.node} gen={doe['generation']} ran={ran} left={left} rows={len(rows)} data_sha={sha[:7]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
