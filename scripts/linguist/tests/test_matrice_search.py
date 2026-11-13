import json, pathlib, subprocess, sys
TOOL = pathlib.Path(__file__).resolve().parents[1] / "matrice_search.py"

def run(args, seed):
    return subprocess.run([sys.executable, str(TOOL), "--seed", str(seed), *args],
                          capture_output=True, text=True)

def seed_file(tmp_path):
    seed = {"schema_version": 1, "sources": [],
            "concepts": [{"concept_id": "demo.alpha", "domain_id": "demo", "preferred_label": "alpha",
                          "definition": "first", "status": "candidate", "version": 1, "source_ids": ["s"]}],
            "labels": [{"label_id": "lbl-alpha", "concept_id": "demo.alpha", "text": "alp",
                        "label_type": "symbolic_notation", "language": "en", "audience": "expert",
                        "register": "formal", "status": "candidate", "source_ids": ["s"]}],
            "mappings": []}
    p = tmp_path / "seed.json"; p.write_text(json.dumps(seed)); return p

def test_search(tmp_path):
    r = run(["search", "alp"], seed_file(tmp_path))
    assert r.returncode == 0 and "demo.alpha" in r.stdout

def test_screen_collision(tmp_path):
    p = seed_file(tmp_path)
    e = tmp_path / "e.json"
    e.write_text(json.dumps({"concept_id": "demo.alpha", "domain_id": "demo"}))
    r = run(["screen", str(e)], p); assert r.returncode == 1

def test_add_and_validate(tmp_path):
    p = seed_file(tmp_path)
    e = tmp_path / "e.json"
    e.write_text(json.dumps({"concept": {"concept_id": "demo.beta", "domain_id": "demo",
                                         "preferred_label": "beta", "definition": "second",
                                         "version": 1, "source_ids": ["s"]}}))
    assert run(["add", str(e)], p).returncode == 0
    assert run(["validate"], p).returncode == 0
