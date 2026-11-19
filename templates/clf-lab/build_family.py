#!/usr/bin/env python3
"""DO render families/<family>/{doe.yaml, data/manifest.json} from FAMILIES (generation 0, fractional factorial)."""
import json
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "common"))
import doe_lib  # noqa: E402

REPO = "timerloggedout-spec/termux-monorepo"
L2 = "experiments/doe/live-2-prlane-tuning/snapshots/"
SNAPS = ["feed-2026-10-28T230234Z.json", "feed-2026-10-28T231701Z.json", "feed-2026-10-28T233736Z.json",
         "feed-2026-10-29T005615Z.json", "feed-2026-10-29T114228Z.json", "feed-2026-10-30T113448Z.json",
         "feed-2026-10-31T111001Z.json", "feed-2026-11-01T010229Z.json"]
FAMILIES = {
    "tier1-classifiers-steward": {
        "task": "unit state (live ∨ dormant ∨ dead) from the steward's unit description",
        "label_note": "gold: classifiers-feed/v1 unit `state`; classes with <3 rows drop per run (dead=2 today)",
        "sources": [{"adapter": "classifiers_feed", "path": "ops/classifiers/classifiers-feed.json", "label_field": "state"}],
        "refs": ["ops/classifiers/classifiers-feed.json", "docs/ops/CLASSIFIERS-FEED.md", "docs/ops/TIER1-CLASSIFIER-RECON-2026-10-28.md"],
    },
    "live-2-prlane-tuning": {
        "task": "PR lane (CANDIDATE ∨ EXTRACT ∨ NEED_EVIDENCE ∨ SUPERSEDE) from title ∧ PR metadata tokens",
        "label_note": "gold: lane recorded by vocab-v2 classify_pr in 8 frozen pr-lane-feed snapshots; dedup layer keeps the newest row per PR text",
        "sources": [{"adapter": "pr_lane_snapshots", "paths": [L2 + s for s in SNAPS]}],
        "refs": ["experiments/doe/live-2-prlane-tuning/DESIGN.json", "ml/pipelines/lanes/classify.py", "ml/pipelines/production_classify.py"],
    },
    "nc-1-notation-compliance": {
        "task": "notation compliance (drift ∨ compliant) per corpus unit",
        "label_note": "gold: nc-1 corpus units.jsonl `label` (50 units; prose_about_notation=2 drops per run)",
        "sources": [{"adapter": "notation_units", "path": "experiments/doe/nc-1-notation-compliance/records/corpus/units.jsonl", "label_field": "label"}],
        "refs": ["experiments/doe/nc-1-notation-compliance/DESIGN.json", "experiments/doe/nc-1-notation-compliance/records/corpus/units.jsonl"],
    },
    "bf-1-backfill-methods": {
        "task": "chat intent v2 (request ∨ directive ∨ aside ∨ speculation ∨ question ∨ do)",
        "label_note": ("gold: 11 rows of scripts/classifiers/backfill-v1-v2.json (v2 label). The labeled chat corpus is empty upstream, "
                       "so a SILVER seed is generated each run: chat_intent v2 rules (pinned commit) label sentences from nc-1 chat units "
                       "∧ PR titles of the newest live-2 snapshot. Metrics on silver measure rule distillation; `gold_acc` scores the "
                       "silver-trained model on the 11 gold rows."),
        "sources": [{"adapter": "chat_intent", "gold": "scripts/classifiers/backfill-v1-v2.json", "gold_field": "v2",
                     "rules": "scripts/classifiers/chat_intent.py",
                     "silver_sources": [
                         {"kind": "units_jsonl", "path": "experiments/doe/nc-1-notation-compliance/records/corpus/units.jsonl", "strata": ["chat", "github"]},
                         {"kind": "pr_titles", "path": L2 + SNAPS[-1]}]}],
        "refs": ["experiments/doe/bf-1-backfill-methods/DESIGN.json", "scripts/classifiers/chat_intent.py", "scripts/classifiers/backfill-v1-v2.json"],
    },
}
FACTORS = {
    "model": {"levels": ["logreg", "linear-svm", "nb", "small-gbm"], "params": {
        "logreg": {"C": {"values": [0.3, 1.0, 3.0], "min": 0.001, "max": 1000}},
        "linear-svm": {"C": {"values": [0.1, 0.5, 2.0], "min": 0.001, "max": 1000}},
        "nb": {"alpha": {"values": [0.1, 0.5, 1.0], "min": 0.001, "max": 10}},
        "small-gbm": {"lr": {"values": [0.05, 0.1, 0.2], "min": 0.005, "max": 0.5},
                      "max_iter": {"values": [50, 100, 200], "min": 20, "max": 300, "int": True},
                      "svd": {"values": [32, 64, 96], "min": 8, "max": 128, "int": True}}}},
    "features": {"levels": ["tfidf-word", "tfidf-char", "hashing"], "params": {
        "tfidf-word": {"ngram_max": {"values": [1, 2, 3], "min": 1, "max": 4, "int": True}},
        "tfidf-char": {"ngram_max": {"values": [4, 5, 6], "min": 3, "max": 7, "int": True}},
        "hashing": {"log2_features": {"values": [14, 16, 18], "min": 12, "max": 18, "int": True}}}},
    "layer": {"levels": ["raw", "dedup", "augmented"]},
}

for fam, spec in FAMILIES.items():
    out = HERE / "families" / fam
    (out / "data").mkdir(parents=True, exist_ok=True)
    manifest = {"schema": "clf-lab-manifest/v1", "family": fam, "repo": REPO, "ref": "master", "pin_sha": None,
                "task": spec["task"], "label_note": spec["label_note"], "sources": spec["sources"],
                "issue_refs": ["#5605", "issuecomment-6974657958"], "upstream_refs": spec["refs"]}
    (out / "data" / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    factors = json.loads(json.dumps(FACTORS))
    doe = {"schema": "clf-lab-doe/v1", "family": fam, "generation": 0, "data_sha": None,
           "design": "fractional-factorial", "design_note": "1/3 fraction: (feature_idx + layer_idx) mod 3 = model_idx mod 3",
           "batch_size": 12, "eval": {"folds": 5, "repeats": 2, "seed": 7, "aug_copies": 1, "metric": "macro_f1"},
           "improve": {"top_k": 3, "explore": 2, "min_delta": 0.005},
           "factors": factors}
    doe["cells"] = doe_lib.generation0(factors, doe["design"])
    (out / "doe.yaml").write_text(yaml.safe_dump(doe, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(fam, len(doe["cells"]))
