from pathlib import Path
import json
import sqlite3
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/"docs/proposals/active/domain-composition-matrix/seed.json"
VALIDATOR=ROOT/"scripts/ci/validate_domain_composition.py"
BUILDER=ROOT/"scripts/domain_composition/build_db.py"

def test_seed_is_valid():
    r=subprocess.run([sys.executable,str(VALIDATOR)],cwd=ROOT,capture_output=True,text=True)
    assert r.returncode==0, r.stderr
    assert "domain-composition: OK" in r.stdout

def test_domain_specific_notation_is_not_collapsed():
    d=json.loads(SEED.read_text(encoding="utf-8"))
    surfaces={(x["domain_id"],x["surface"]) for x in d["notations"]}
    assert ("category_theory","f ; g") in surfaces
    assert ("lean","f ≫ g") in surfaces
    assert ("haskell","m >>= f") in surfaces

def test_every_rule_resolves_to_declared_entities():
    d=json.loads(SEED.read_text(encoding="utf-8"))
    entities={x["entity_type_id"] for x in d["entity_types"]}
    for rule in d["composition_rules"]:
        assert rule["source_entity_type_id"] in entities
        assert rule["target_entity_type_id"] in entities
        if rule.get("result_entity_type_id"):
            assert rule["result_entity_type_id"] in entities

def test_sqlite_materialization_is_queryable(tmp_path):
    db_path=tmp_path/"domain-composition.sqlite"
    r=subprocess.run([sys.executable,str(BUILDER)],cwd=ROOT,capture_output=True,text=True,check=True,env={**__import__("os").environ,"PYTHONPATH":str(ROOT)})
    assert "domain-composition.sqlite" in r.stdout
    generated=ROOT/"docs/proposals/active/domain-composition-matrix/domain-composition.sqlite"
    assert generated.exists()
    with sqlite3.connect(generated) as db:
        assert db.execute("select count(*) from composition_rule").fetchone()[0] == 3
        assert db.execute("select count(*) from entity_type").fetchone()[0] == 4
        assert db.execute("select count(*) from evidence").fetchone()[0] == 1
    generated.unlink()
