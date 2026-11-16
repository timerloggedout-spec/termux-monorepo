"""Offline tests for the reading pipeline (study_pipeline.py, §1b).

Every public function is covered; all network/OCR touches are
injected fakes — no live calls.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from study_pipeline import (HypothesisClient, annotation_to_card,  # noqa: E402
                            build_term_bank, confirm_edition,
                            emphasize_terms, extract_structure,
                            find_editions, flagged_term_annotation,
                            ingest_upload, make_annotation,
                            make_term_lookup, run_pipeline,
                            term_bank_cards, term_tap_payload,
                            to_reader_sections)

NOW = datetime(2026, 11, 3, 9, 0, tzinfo=timezone.utc)

DOC = """# Chapter 1: Cells

Cells are the unit of life. The cell membrane controls entry.

## Membrane transport

The cell membrane is selective. Photosynthesis is not here.

# Chapter 2: Energy

Photosynthesis converts light into chemical energy in the cell.
"""

GLOSSARY = """Cell membrane: Controls what enters and leaves the cell.
Photosynthesis — Conversion of light energy into chemical energy.
"""

INDEX = """cell membrane 12, 14
photosynthesis .... 31
"""


def fake_http_get(url):
    if "openlibrary.org/search.json" in url:
        return {"docs": [{"title": "Biology 101",
                          "author_name": ["A. Author"],
                          "isbn": ["9780000000001"],
                          "key": "/works/OL1W"}]}
    if "archive.org/advancedsearch" in url:
        return {"response": {"docs": [
            {"identifier": "biology101", "title": "Biology 101",
             "creator": "A. Author"}]}}
    raise AssertionError(f"unexpected url {url}")


def test_finder_candidates_unconfirmed_and_confirm():
    receipt = find_editions({"title": "Biology 101"}, http_get=fake_http_get,
                            now=NOW)
    assert receipt["stage"] == "finder"
    assert receipt["status"] == "awaiting_confirmation"
    assert receipt["confirmed"] is None
    sources = {c["source"] for c in receipt["candidates"]}
    assert sources == {"openlibrary", "archive.org"}
    chosen = confirm_edition(receipt, 0, now=NOW)
    assert chosen["status"] == "confirmed"
    assert chosen["edition"]["confirmed"] is True
    try:
        confirm_edition(receipt, 99)
    except ValueError:
        pass
    else:
        raise AssertionError("out-of-range confirm must raise")


def test_finder_isbn_path_and_source_failure_isolated():
    def flaky(url):
        if "archive.org" in url:
            raise RuntimeError("down")
        return {"docs": []}

    r = find_editions({"title": "X"}, http_get=flaky, now=NOW)
    assert r["candidates"] == []  # down source never blocks the finder

    def isbn_get(url):
        assert "/isbn/" in url
        return {"title": "Biology 101", "key": "/books/OL1M",
                "authors": [{"key": "/authors/OL1A"}]}

    r2 = find_editions({"isbn": "9780000000001"}, http_get=isbn_get, now=NOW)
    assert r2["candidates"][0]["identifier"] == "ISBN 9780000000001"


def test_ingest_text_native_and_ocr_and_pdf(tmp_path):
    p = tmp_path / "chapter.txt"
    p.write_text(DOC)
    out = ingest_upload(p, now=NOW)
    assert out["kind"] == "text" and out["chars"] == len(DOC)

    img = tmp_path / "page.png"
    img.write_bytes(b"\x89PNG")
    out2 = ingest_upload(img, ocr_fn=lambda path: "scanned text", now=NOW)
    assert out2["kind"] == "ocr-image" and out2["text"] == "scanned text"

    pdf = tmp_path / "book.pdf"
    pdf.write_bytes(b"%PDF")
    try:
        ingest_upload(pdf)
    except RuntimeError as e:
        assert "extractor" in str(e)
    else:
        raise AssertionError("pdf without an extractor must raise")
    out3 = ingest_upload(pdf, pdf_text_fn=lambda path: "extracted")
    assert out3["kind"] == "extracted-pdf"


def test_extract_structure_chapters_sections():
    st = extract_structure(DOC)
    assert [c["title"] for c in st["chapters"]] == [
        "Chapter 1: Cells", "Chapter 2: Energy"]
    ch1 = st["chapters"][0]
    assert [s["title"] for s in ch1["sections"]] == [
        "Chapter 1: Cells", "Membrane transport"]
    assert "cell membrane controls" in ch1["sections"][0]["text"]

    plain = "Chapter 3: Loops\nBody text.\nChapter 4: Functions\nMore."
    st2 = extract_structure(plain)
    assert [c["title"] for c in st2["chapters"]] == [
        "Chapter 3: Loops", "Chapter 4: Functions"]


def test_to_reader_sections_maps_reader_type():
    sections = to_reader_sections(extract_structure(DOC))
    assert len(sections) == 3
    assert sections[0].chapter == "Chapter 1: Cells"
    assert sections[0].tokens  # tokenized by the reader Section


def _bank():
    return build_term_bank(extract_structure(DOC), GLOSSARY, INDEX, now=NOW)


def test_term_bank_per_chapter_shape():
    bank = _bank()
    by_chapter = {c["chapter"]: c["terms"] for c in bank["chapters"]}
    ch1 = {t["term"]: t for t in by_chapter["Chapter 1: Cells"]}
    assert ch1["Cell membrane"]["definition"].startswith("Controls")
    assert ch1["Cell membrane"]["index_pages"] == [12, 14]
    assert "Membrane transport" in ch1["Cell membrane"]["sections"]
    ch2 = {t["term"] for t in by_chapter["Chapter 2: Energy"]}
    assert ch2 == {"Photosynthesis", "Cell membrane"} or \
        ch2 == {"Photosynthesis"}  # cell appears in ch2 text too
    assert bank["receipt"]["stage"] == "term-bank"


def test_make_term_lookup_matches_reader_hook():
    lookup = make_term_lookup(_bank())
    hit = lookup("cell membrane")
    assert hit["definition"].startswith("Controls")
    assert hit["index_refs"] == [12, 14]
    assert hit["card_ready"] is True
    assert lookup("nonexistent term") is None


def test_term_bank_cards_feed_sr():
    cards = term_bank_cards(_bank())
    fronts = {c.front for c in cards}
    assert "Cell membrane" in fronts and "Photosynthesis" in fronts


def test_emphasize_terms_segments():
    out = emphasize_terms("The cell membrane is selective.", _bank())
    marked = [s for s in out["segments"] if s.get("term")]
    assert marked and marked[0]["text"].lower() == "cell membrane"
    assert out["terms_found"] == ["Cell membrane"]
    joined = "".join(s["text"] for s in out["segments"])
    assert joined == "The cell membrane is selective."


def test_term_tap_payload_has_card():
    payload = term_tap_payload("Photosynthesis", _bank())
    assert payload["definition"].startswith("Conversion")
    assert payload["sr_card"]["front"] == "Photosynthesis"
    try:
        term_tap_payload("nope", _bank())
    except ValueError:
        pass
    else:
        raise AssertionError("unknown term must raise")


def test_annotation_w3c_shape_and_to_card():
    ann = make_annotation("https://example.org/book", "cell membrane",
                          body_text="Controls entry and exit.",
                          tags=["term"])
    assert ann["type"] == "Annotation"
    assert ann["target"]["selector"]["exact"] == "cell membrane"
    assert ann["motivation"] == "commenting"
    card = annotation_to_card(ann)
    assert card["front"] == "cell membrane"
    assert card["back"] == "Controls entry and exit."
    hl = make_annotation("https://example.org/book", "quote only")
    assert hl["motivation"] == "highlighting"


def test_flagged_term_annotation_tie_in():
    bank = _bank()
    entry = bank["chapters"][0]["terms"][0]
    ann = flagged_term_annotation(entry, "https://example.org/book")
    assert "term" in ann["tags"]
    assert ann["target"]["selector"]["exact"] == entry["term"]


def test_hypothesis_client_create_and_search():
    calls = []

    def fake_http(method, url, payload=None):
        calls.append((method, url, payload))
        return {"id": "ann-1"} if method == "POST" else {"rows": []}

    client = HypothesisClient(token="tok", http=fake_http)
    ann = make_annotation("https://example.org/book", "cell membrane",
                          body_text="def")
    out = client.create_annotation(ann)
    assert out["id"] == "ann-1"
    method, url, payload = calls[0]
    assert method == "POST" and url.endswith("/annotations")
    assert payload["uri"] == "https://example.org/book"
    assert payload["target"][0]["selector"][0]["exact"] == "cell membrane"
    client.search_annotations("https://example.org/book")
    assert calls[1][0] == "GET" and "search?" in calls[1][1]

    tokenless = HypothesisClient(token="", http=fake_http)
    try:
        tokenless.create_annotation(ann)
    except RuntimeError as e:
        assert "API token" in str(e)
    else:
        raise AssertionError("tokenless create must raise")


def test_run_pipeline_bundle(tmp_path):
    p = tmp_path / "chapter.txt"
    p.write_text(DOC)
    bundle = run_pipeline({"title": "Biology 101"}, upload_path=p,
                          glossary_text=GLOSSARY, index_text=INDEX,
                          http_get=fake_http_get, now=NOW)
    assert bundle["finder"]["status"] == "awaiting_confirmation"
    assert bundle["reader_sections"] == 3
    assert bundle["sr_cards"] >= 2
    assert bundle["receipt"]["stage"] == "pipeline"
    json.dumps(bundle)  # the whole bundle is JSON-serializable


# ---- build D (#4242): syllabus parse + confirm-gated placement ----

SYLLABUS_TEXT = """BIO 101 — Intro Biology
Lectures: Mon Wed 10:00-11:15, Science Building, Room 204
Lab: Fri 13:00-14:30, Science Building, Room 110
Midterm: 2026-11-20 18:00, Science Building
Final exam: Dec 12, 9:00 AM, Science Building
Bring a pencil.
"""


def test_parse_syllabus_text_records():
    from study_pipeline import parse_syllabus_text
    parsed = parse_syllabus_text(SYLLABUS_TEXT)
    assert parsed["counts"]["classes"] == 2
    assert parsed["counts"]["assessments"] == 2
    first = parsed["doc"]["classes"][0]
    assert first["course"] == "BIO 101"
    assert first["days"] == ["Mon", "Wed"]
    assert first["start"] == "10:00" and first["end"] == "11:15"
    assert first["building"] == "Science Building"
    assert first["room"] == "204"
    kinds = {a["kind"] for a in parsed["doc"]["assessments"]}
    assert kinds == {"midterm", "final"}
    final = [a for a in parsed["doc"]["assessments"]
             if a["kind"] == "final"][0]
    assert final["date"].endswith("-12-12")
    assert final["time"] == "09:00"
    assert "Bring a pencil." in parsed["unmatched"]


def test_place_syllabus_is_confirm_gated():
    from study_pipeline import parse_syllabus_text, place_syllabus
    parsed = parse_syllabus_text(SYLLABUS_TEXT)
    held = place_syllabus(parsed, confirmed=False)
    assert held["placed"] is False
    assert held["awaiting"] == "student-confirm"
    assert "calendar" not in held
    placed = place_syllabus(parsed, confirmed=True)
    assert placed["placed"] is True
    cal = placed["calendar"]
    assert cal["receipt"]["classes"] == 2
    assert cal["receipt"]["assessments"] == 2


def test_run_syllabus_upload_ocr_provenance(tmp_path):
    from study_pipeline import run_syllabus_upload
    img = tmp_path / "syllabus.png"
    img.write_bytes(b"fake-png")
    out = run_syllabus_upload(img, ocr_fn=lambda p: SYLLABUS_TEXT)
    assert out["provenance"] == {"source": "ocr"}
    assert out["ingest"]["kind"] == "ocr-image"
    assert out["placement"]["placed"] is False  # no confirm given
    out2 = run_syllabus_upload(img, confirmed=True,
                               ocr_fn=lambda p: SYLLABUS_TEXT)
    assert out2["placement"]["placed"] is True


def test_ingest_any_dispatches_by_content(tmp_path):
    from study_pipeline import ingest_any
    syl = tmp_path / "syllabus.txt"
    syl.write_text(SYLLABUS_TEXT, encoding="utf-8")
    out = ingest_any(str(syl))
    assert out["flow"] == "syllabus"
    assert out["placement"]["placed"] is False
    book = tmp_path / "chapter.txt"
    book.write_text(
        "Chapter 1: Cells\nThe cell is the unit of life.\n"
        "Glossary\nCell: the unit of life\n", encoding="utf-8")
    out = ingest_any(str(book))
    assert out["flow"] == "textbook"
    assert out["sr_cards"] >= 1


def test_cli_ingest_command(tmp_path):
    import json as _json
    import subprocess
    import sys as _sys
    syl = tmp_path / "syllabus.txt"
    syl.write_text(SYLLABUS_TEXT, encoding="utf-8")
    proc = subprocess.run(
        [_sys.executable, str(ROOT / "demo.py"), "ingest", str(syl)],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    out = _json.loads(proc.stdout)
    assert out["flow"] == "syllabus"
    assert out["placement"]["placed"] is False
    proc = subprocess.run(
        [_sys.executable, str(ROOT / "demo.py"), "ingest", str(syl),
         "--confirm"], capture_output=True, text=True)
    out = _json.loads(proc.stdout)
    assert out["placement"]["placed"] is True
