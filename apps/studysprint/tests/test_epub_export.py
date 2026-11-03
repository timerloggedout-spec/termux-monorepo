"""EPUB reader-edition export (#4472; spec #4463 §6 pins):
container shape, spine order, chapter grouping, the Terms
chapter in both its branches (cited bank / honest empty),
and no scripts anywhere in the package."""
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

APP_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_ROOT))

from study_sr import export_epub, terms_from_bank  # noqa: E402

SECTIONS = [
    {"section_id": "s1", "title": "Cells", "chapter": "Week 1",
     "content": "The cell membrane controls entry.\n\nIt is selective."},
    {"section_id": "s2", "title": "Transport", "chapter": "Week 1",
     "content": "Diffusion moves molecules down a gradient."},
    {"section_id": "s3", "title": "Energy", "chapter": "Week 2",
     "content": "ATP carries energy in the cell."},
]
BANK = {"chapters": [
    {"chapter": "Week 1", "terms": [
        {"term": "Cell membrane", "definition": "the cell boundary",
         "index_pages": [42, 57]},
        {"term": "Diffusion", "definition": "net movement down a gradient",
         "index_pages": [43]}]},
    {"chapter": "Week 2", "terms": [
        {"term": "Cell membrane", "definition": "the cell boundary",
         "index_pages": [61]}]}]}


def _build(tmp_path, **kw):
    out = tmp_path / "book.epub"
    receipt = export_epub(SECTIONS, out, title="BIO 101",
                          surface_version="0.2.0", **kw)
    return out, receipt


def test_container_shape_mimetype_first_and_stored(tmp_path):
    out, receipt = _build(tmp_path)
    with zipfile.ZipFile(out) as z:
        infos = z.infolist()
        assert infos[0].filename == "mimetype"
        assert infos[0].compress_type == zipfile.ZIP_STORED
        assert z.read("mimetype") == b"application/epub+zip"
        names = set(z.namelist())
        assert {"META-INF/container.xml", "OEBPS/content.opf",
                "OEBPS/nav.xhtml", "OEBPS/toc.ncx",
                "OEBPS/style.css"} <= names
    assert receipt["chapters"] == 2 and receipt["sections"] == 3
    import hashlib
    assert receipt["sha256"] == hashlib.sha256(
        out.read_bytes()).hexdigest()


def test_spine_order_and_chapter_grouping(tmp_path):
    out, _ = _build(tmp_path)
    with zipfile.ZipFile(out) as z:
        opf = ET.fromstring(z.read("OEBPS/content.opf"))
        ns = {"opf": "http://www.idpf.org/2007/opf"}
        spine = [r.get("idref") for r in opf.find("opf:spine", ns)]
        assert spine == ["title", "ch1", "ch2", "terms"]
        ch1 = z.read("OEBPS/chapter1.xhtml").decode()
        ch2 = z.read("OEBPS/chapter2.xhtml").decode()
    assert 'id="s1"' in ch1 and 'id="s2"' in ch1 and "Energy" not in ch1
    assert 'id="s3"' in ch2


def test_terms_chapter_cites_pages_as_text(tmp_path):
    out, receipt = _build(tmp_path, terms=terms_from_bank(BANK))
    assert receipt["terms"] == 2  # merged across chapters
    with zipfile.ZipFile(out) as z:
        terms = z.read("OEBPS/terms.xhtml").decode()
    assert "Cell membrane" in terms and "the cell boundary" in terms
    # merged page refs from both chapters, cited as text
    assert "source pp. 42, 57, 61" in terms
    assert "source pp. 43" in terms
    assert "<a " not in terms  # provenance is data, never a link


def test_terms_chapter_honest_when_no_bank(tmp_path):
    out, receipt = _build(tmp_path)
    assert receipt["terms"] == 0
    with zipfile.ZipFile(out) as z:
        terms = z.read("OEBPS/terms.xhtml").decode()
    assert "no glossary or index" in terms
    assert "source pp." not in terms


def test_no_scripts_and_all_xhtml_wellformed(tmp_path):
    out, _ = _build(tmp_path, terms=terms_from_bank(BANK))
    with zipfile.ZipFile(out) as z:
        for name in z.namelist():
            data = z.read(name).decode("utf-8", "ignore")
            assert "<script" not in data.lower(), name
            if name.endswith((".xhtml", ".opf", ".ncx", ".xml")):
                ET.fromstring(z.read(name))  # raises if malformed


def test_tui_export_button_writes_the_edition(tmp_path):
    import asyncio
    from tui import StudySprintTUI

    async def scenario():
        app = StudySprintTUI(root=APP_ROOT, export_dir=tmp_path)
        async with app.run_test(size=(110, 42)) as pilot:
            await pilot.pause()
            tab = app.query_one("#--content-tab-tab-export")
            await pilot.click(tab)
            await pilot.pause()
            await pilot.click("#export-epub")
            await pilot.pause()
            out = tmp_path / "studysprint-reader.epub"
            assert out.exists()
            status = str(app.query_one("#export-status").content)
            assert "Reader edition:" in status
            assert "terms indexed" in status
            with zipfile.ZipFile(out) as z:
                assert z.read("mimetype") == b"application/epub+zip"

    asyncio.run(scenario())
