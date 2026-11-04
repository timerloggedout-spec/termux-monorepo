"""#4673 (qualifications closure, surfaces 0.5.1): the webApp
gains the SR exports — browser ports of the core's .apkg and
Obsidian vault writers, battery-pinned to the core's writers
over the same fixture cards. APK inherits via the bundle.

The .apkg battery asserts SEMANTIC parity (card set, fields,
tags, model/deck identity via the core's _stable_id, referential
integrity, sqlite integrity_check) — byte parity with genanki's
file is not claimed (ids/guids/timestamps are generation-time
values in both writers). The Obsidian battery asserts byte
parity of the whole note set.
"""
import json
import shutil
import sqlite3
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
APP = HERE.parent
sys.path.insert(0, str(APP))

from study_sr import SRCard, export_obsidian_vault  # noqa: E402

WEB = APP / "web"
FIXTURE = [
    {"card_id": "8c01afbd0c5aacc5",
     "front": "What does the cell membrane do?",
     "back": "Controls what enters and leaves the cell.",
     "tags": ["cell structure"]},
    {"card_id": "deadbeef00000002", "front": "Front two?",
     "back": "Back two.", "tags": ["mitosis", "cell structure"]},
]
STATES = {"8c01afbd0c5aacc5": {"due": "2026-11-05",
                              "interval_days": 2.5}}


def _node_exports(tmp_path):
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not available")
    app_js = (WEB / "app.js").read_text()
    start = app_js.index("function computeDayIndex")
    end = app_js.index("/* ---------------- loading")
    helpers = app_js[start:end]
    script = helpers + f"""
const fs = require("fs");
const cards = {json.dumps(FIXTURE)};
fs.writeFileSync({json.dumps(str(tmp_path / "web.apkg"))},
  Buffer.from(buildApkgBytes(cards, "StudySprint")));
fs.writeFileSync({json.dumps(str(tmp_path / "web-vault.zip"))},
  Buffer.from(buildObsidianZip(cards, {json.dumps(STATES)}, "fsrs")));
const big = [];
for (let i = 0; i < 40; i++) big.push({{card_id: "card" + i,
  front: "Q" + i + " " + "x".repeat(i === 7 ? 9000 : 20),
  back: "A" + i, tags: ["topic one"]}});
fs.writeFileSync({json.dumps(str(tmp_path / "web-big.apkg"))},
  Buffer.from(buildApkgBytes(big, "StudySprint")));
console.log("exports written");
"""
    proc = subprocess.run([node, "-e", script], capture_output=True,
                          text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr


def _read_apkg(path):
    z = zipfile.ZipFile(path)
    assert z.namelist() == ["collection.anki2", "media"]
    db_path = str(path) + ".db"
    Path(db_path).write_bytes(z.read("collection.anki2"))
    db = sqlite3.connect(db_path)
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    return db


def test_apkg_port_matches_core_writer(tmp_path):
    pytest.importorskip("genanki")
    from study_sr import export_apkg
    _node_exports(tmp_path)
    cards = [SRCard(c["card_id"], c["front"], c["back"], c["tags"])
             for c in FIXTURE]
    export_apkg(cards, tmp_path / "core.apkg")
    core = _read_apkg(tmp_path / "core.apkg")
    web = _read_apkg(tmp_path / "web.apkg")

    def notes(db):
        return sorted(db.execute(
            "SELECT tags, flds, sfld FROM notes").fetchall())
    assert notes(web) == notes(core)
    assert sorted(web.execute("SELECT did, ord FROM cards")) == \
        sorted(core.execute("SELECT did, ord FROM cards"))
    cmodels = json.loads(core.execute(
        "SELECT models FROM col").fetchone()[0])
    wmodels = json.loads(web.execute(
        "SELECT models FROM col").fetchone()[0])
    assert list(wmodels) == list(cmodels)  # _stable_id identity
    wmodel = list(wmodels.values())[0]
    cmodel = list(cmodels.values())[0]
    for key in ("name", "flds", "tmpls", "type", "sortf", "req"):
        assert wmodel[key] == cmodel[key], key
    cdecks = json.loads(core.execute(
        "SELECT decks FROM col").fetchone()[0])
    wdecks = json.loads(web.execute(
        "SELECT decks FROM col").fetchone()[0])
    assert wdecks["1"] == cdecks["1"]
    wdeck = [v for k, v in wdecks.items() if k != "1"][0]
    cdeck = [v for k, v in cdecks.items() if k != "1"][0]
    for key in ("name", "conf", "dyn", "usn"):
        assert wdeck[key] == cdeck[key], key
    orphans = web.execute(
        "SELECT COUNT(*) FROM cards c LEFT JOIN notes n "
        "ON c.nid = n.id WHERE n.id IS NULL").fetchone()[0]
    assert orphans == 0


def test_apkg_port_scales_with_overflow(tmp_path):
    _node_exports(tmp_path)
    big = _read_apkg(tmp_path / "web-big.apkg")
    assert big.execute("SELECT COUNT(*) FROM notes").fetchone()[0] == 40
    assert big.execute("SELECT COUNT(*) FROM cards").fetchone()[0] == 40
    long_fld = big.execute(
        "SELECT LENGTH(flds) FROM notes WHERE sfld LIKE 'Q7 %'"
    ).fetchone()[0]
    assert long_fld > 9000  # payload overflow pages exercised


def test_obsidian_port_byte_parity(tmp_path):
    _node_exports(tmp_path)
    cards = [SRCard(c["card_id"], c["front"], c["back"], c["tags"])
             for c in FIXTURE]
    vault = tmp_path / "vault"
    export_obsidian_vault(cards, vault, states=STATES,
                          scheduler="fsrs")
    core_files = {str(p.relative_to(vault)): p.read_text()
                  for p in vault.rglob("*.md")}
    z = zipfile.ZipFile(tmp_path / "web-vault.zip")
    web_files = {name: z.read(name).decode()
                 for name in z.namelist()}
    assert web_files == core_files


def test_sr_view_carries_export_controls():
    html = (WEB / "index.html").read_text()
    assert 'id="sr-export-apkg"' in html
    assert 'id="sr-export-obsidian"' in html
    app_js = (WEB / "app.js").read_text()
    assert "buildApkgBytes(state.data.sr.cards" in app_js
    assert "buildObsidianZip(state.data.sr.cards" in app_js
