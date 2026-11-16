import importlib.util, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "telemetry_ingest", ROOT / "scripts/telemetry_ingest/ingest.py")
ing = importlib.util.module_from_spec(spec); spec.loader.exec_module(ing)

def build():
    return ing.build(ROOT)

def test_sinks_separate_and_aligned():
    env, pay, rec = build()
    assert env and len(env) == len(pay)
    assert all(e["sink"] == "provenance" for e in env)
    assert all(p["sink"] == "hindsight" for p in pay)
    assert [e["evidence_hash"] for e in env] == [p["metadata"]["evidence_hash"] for p in pay]

def test_coverage_complete_no_missing():
    _, _, rec = build()
    cov = rec["coverage"]
    assert cov["missing"] == [], cov
    assert cov["ingested_providers"] == cov["expected_providers"] > 100

def test_evidence_hash_recomputes():
    env, _, _ = build()
    for e in env[:25]:
        body = {k: v for k, v in e.items() if k != "evidence_hash"}
        assert ing.sha256_bytes(ing.canonical(body).encode()) == e["evidence_hash"]

def test_excluded_are_recorded_not_counted():
    env, _, rec = build()
    excluded = rec["coverage"]["excluded"]
    assert excluded, "agent-stack HOLD integrations must be recorded as excluded"
    skipped = [e for e in env if e["status"] == "skipped"]
    assert len(skipped) == len(excluded)
    assert all(e["outcome"] == "excluded_recorded" for e in skipped)

def test_missing_source_is_partial_never_success(tmp_path):
    env, pay, rec = ing.build(tmp_path)
    assert env == [] and pay == []
    assert rec["sources"], "sources are still reported"
    assert all(s["status"] == "partial" for s in rec["sources"])
    assert rec["coverage"]["expected_providers"] == 0

def test_no_secret_shapes_in_outputs():
    env, pay, _ = build()
    prov, hind, _ = ing.render(env, pay, {"schema": "x"}, "t")
    ing.guard_no_secrets(prov, "prov"); ing.guard_no_secrets(hind, "hind")

def test_outputs_deterministic():
    a = ing.render(*build(), now="t")
    b = ing.render(*build(), now="t")
    assert a == b
