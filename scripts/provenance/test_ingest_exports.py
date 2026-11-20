"""#5555 — provenance ingest: classify-on-ingest ⊕ Actions join ⊕ consumer digest."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import export_digest as dg  # noqa: E402
import ingest_exports as ing  # noqa: E402

SESSION = {
    "id": "s1", "createTime": "2026-11-17T10:00:00Z",
    "prompt": "Add a regression test for auto_claim and open a PR",
    "outputs": [{"pullRequest": {"url": "https://github.com/o/r/pull/5552", "title": "test: add", "headRef": "jules/x"}}],
    "activities": [
        {"id": "a1", "createTime": "2026-11-17T10:01:00Z", "planGenerated": {"plan": {"steps": [{"title": "write test"}]}}},
        {"id": "a2", "createTime": "2026-11-17T10:02:00Z", "agentMessaged": {"agentMessage": "Pushed commit " + "a" * 40}},
        {"id": "a3", "userMessaged": {"userMessage": "token ghp_" + "Z" * 30 + " thanks"}},
    ],
}
CHAT = {"id": "c1", "messages": [{"role": "user", "content": "how is #5523 doing?"}, {"role": "assistant", "content": "fine"}]}
RUNS = [{"id": 9, "name": "ci", "conclusion": "success", "head_sha": "a" * 40, "head_branch": "jules/x",
         "pull_requests": [{"number": 5552}]}]


def _write(tmp_path):
    (tmp_path / "jules.json").write_text(json.dumps({"sessions": [SESSION]}), encoding="utf-8")
    (tmp_path / "chat.json").write_text(json.dumps(CHAT), encoding="utf-8")
    return tmp_path


def test_every_record_classified_on_ingest(tmp_path):
    recs = ing.ingest(_write(tmp_path), "jules-harvest/2026-11-17", RUNS, now="t")
    assert len(recs) == 6
    for r in recs:
        ids = {c["classifier_id"] for c in r["classifications"]}
        assert "chat_intent" in ids
        for c in r["classifications"]:
            assert {"classifier_id", "classifier_version", "label", "confidence"} <= set(c)
    jules = [r for r in recs if r["origin"] == "jules.json"]
    assert all(any(c["classifier_id"] == "ml.pipelines.lanes.classify" for c in r["classifications"]) for r in jules)


def test_classes_and_actions_join(tmp_path):
    recs = {r["native_id"]: r for r in ing.ingest(_write(tmp_path), "ns", RUNS, now="t")}
    assert recs["s1#prompt"]["export_class"] == "thinking"
    assert recs["a3"]["export_class"] == "message"
    assert recs["a2"]["actions"]["verdict"] == "consistent" and recs["a2"]["actions"]["run_count"] == 1
    assert recs["c1#m0"]["actions"]["verdict"] == "claim-unevidenced"
    assert recs["c1#m1"]["actions"]["verdict"] == "no-claim"


def test_credentials_scrubbed_to_hash(tmp_path):
    recs = {r["native_id"]: r for r in ing.ingest(_write(tmp_path), "ns", RUNS, now="t")}
    r = recs["a3"]
    assert "ghp_" not in r["excerpt"] and r["credentials"] and len(r["credentials"][0]["sha256"]) == 64


def test_record_ids_stable_and_namespaced(tmp_path):
    a = ing.ingest(_write(tmp_path), "ns-a", RUNS, now="t")
    b = ing.ingest(tmp_path, "ns-a", RUNS, now="t")
    c = ing.ingest(tmp_path, "ns-b", RUNS, now="t")
    assert [r["record_id"] for r in a] == [r["record_id"] for r in b]
    assert {r["record_id"] for r in a}.isdisjoint({r["record_id"] for r in c})


def test_digest_consumer_reads_and_receipts(tmp_path):
    recs = ing.ingest(_write(tmp_path), "ns", RUNS, now="t")
    src = tmp_path / "records.jsonl"
    src.write_text("".join(json.dumps(r) + "\n" for r in recs), encoding="utf-8")
    out, reads = tmp_path / "digest.json", tmp_path / "reads.jsonl"
    assert dg.main(["--records", str(src), "--out", str(out), "--reads", str(reads)]) == 0
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["records"] == 6 and "excerpt" not in out.read_text(encoding="utf-8")
    receipt = json.loads(reads.read_text(encoding="utf-8").splitlines()[-1])
    assert receipt["consumer"] == dg.CONSUMER_ID and receipt["records"] == 6


def test_muse_side_chat_discovery_terms_are_versioned_and_namespaced(tmp_path):
    source = tmp_path / "muse-side-chat.json"
    source.write_text(json.dumps({
        "id": "muse-1",
        "messages": [{
            "role": "user",
            "content": "Moniker collision marketing naming anon anonymous 4n0nSEC 4n∅N 4n∅nSEC profiles",
        }],
    }), encoding="utf-8")
    muse = ing.ingest(source, "muse-side-chat/2026-11-18", now="t")
    classifier = next(c for c in muse[0]["classifications"]
                      if c["classifier_id"] == "muse_side_chat_seo")
    assert classifier["classifier_version"] == ing.MUSE_DISCOVERY_VERSION
    assert classifier["terms"] == [
        "moniker", "collision", "marketing", "naming", "anon",
        "4n0nSEC", "4n∅N", "4n∅nSEC", "profiles",
    ]
    generic = ing.ingest(source, "chat-export/2026-11-18", now="t")
    assert all(c["classifier_id"] != "muse_side_chat_discovery"
               for c in generic[0]["classifications"])
    summary = dg.digest(muse)
    assert summary["groups"][0]["discovery_terms"]["4n∅N"] == 1
