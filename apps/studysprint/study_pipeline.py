"""StudySprint reading pipeline — FEATURES §1b in full (RFP-D1-3, #4111).

The syllabus makes the plan; the assigned readings are the material.
This module is the six-stage chain of record:

    finder -> OCR -> structure -> term bank -> term emphasis
           -> hypothes.is annotation

- **Finder** locates an edition from legal open sources (OpenLibrary,
  archive.org) and presents it for the student's one-tap confirm —
  never plan from an unconfirmed edition (the evidence rule applies
  to books too).
- **OCR intake** takes uploads in any form: text/markdown natively,
  photos/scans through an OCR engine (tesseract when present, or an
  injected engine), PDFs/EPUB through an injected text extractor
  (MinerU-class), so a photographed chapter is a first-class chapter.
- **Structure extraction** turns the document into chapters ->
  sections from its headings/TOC; reading assignments map to chapter
  + section ranges, not page blobs.
- **Term bank** mines the book's Index + Glossary per chapter:
  (term, glossary definition, index page refs, sections it appears
  in). The bank is the spine — it feeds term emphasis, quiz
  generation, SR cards, and flagging, and it implements the reader
  core's TermLookupFn hook (study_reader.py shipped the hook with no
  bank behind it; this is the bank).
- **Term emphasis** marks bank terms wherever they appear and gives
  the tap payload (definition, sections, SR card).
- **Hypothes.is layer** — annotations as W3C Web Annotation JSON-LD,
  portable by construction. Evaluation of the three options recorded
  on #3697: (1) revive/rebase the owned client_fork — a dormant
  (2026-08) web client surface; (2) hosted hypothes.is embed — a
  view-layer choice; (3) **API-only annotations over reader sections
  — implemented here**: the pipeline's data layer speaks the
  hypothes.is API + the W3C model, and either client surface can
  render on top of it unchanged. Flagged terms become annotations
  (the Term Emphasis tie-in).

Offline by default: every network/OCR touch is an injected callable;
the defaults (urllib, tesseract) engage only when a caller runs the
stage live. Receipts follow the app's stamped style.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from study_reader import Section
from study_sr import build_cards

PIPELINE_RECEIPT_SCHEMA = "studysprint-pipeline-receipt/v1"


def _iso(dt: datetime | None = None) -> str:
    dt = dt or datetime.now(timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _receipt(stage: str, now: datetime | None = None, **fields) -> dict:
    out = {"schema": PIPELINE_RECEIPT_SCHEMA, "stage": stage,
           "observed_at": _iso(now)}
    out.update(fields)
    return out


# ---------------------------------------------------------------- finder

def _default_http_get(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"User-Agent": "StudySprint/0.4 (reading pipeline)"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def _openlibrary_candidates(text_ref: dict, http_get) -> list:
    import urllib.parse
    if text_ref.get("isbn"):
        url = ("https://openlibrary.org/isbn/"
               f"{urllib.parse.quote(str(text_ref['isbn']))}.json")
        try:
            doc = http_get(url)
        except Exception:
            doc = None
        if doc and doc.get("title"):
            return [{"title": doc["title"],
                     "authors": [a.get("key", "") for a in
                                 doc.get("authors") or []],
                     "source": "openlibrary",
                     "identifier": f"ISBN {text_ref['isbn']}",
                     "format": "edition-record",
                     "url": f"https://openlibrary.org{doc.get('key', '')}",
                     "license_note": "catalog record; edition access "
                                     "via the student's library"}]
    q = urllib.parse.quote(str(text_ref.get("title", "")))
    url = f"https://openlibrary.org/search.json?title={q}&limit=5"
    doc = http_get(url)
    out = []
    for d in (doc or {}).get("docs", []):
        out.append({"title": d.get("title", ""),
                    "authors": d.get("author_name", []),
                    "source": "openlibrary",
                    "identifier": (d.get("isbn") or [d.get("key", "")])[0],
                    "format": "edition-record",
                    "url": f"https://openlibrary.org{d.get('key', '')}",
                    "license_note": "catalog record; edition access via "
                                    "the student's library"})
    return out


def _archive_candidates(text_ref: dict, http_get) -> list:
    import urllib.parse
    title = urllib.parse.quote(str(text_ref.get("title", "")))
    url = ("https://archive.org/advancedsearch.php"
           f"?q=title:({title})&fl[]=identifier&fl[]=title"
           "&fl[]=creator&rows=5&output=json")
    doc = http_get(url)
    out = []
    for d in ((doc or {}).get("response") or {}).get("docs", []):
        ident = d.get("identifier", "")
        out.append({"title": d.get("title", ""),
                    "authors": [d.get("creator", "")] if
                    d.get("creator") else [],
                    "source": "archive.org",
                    "identifier": ident,
                    "format": "pdf/epub (archive.org lending/full view "
                              "per item rights)",
                    "url": f"https://archive.org/details/{ident}",
                    "license_note": "archive.org item; access per the "
                                    "item's rights statement"})
    return out


def find_editions(text_ref: dict, http_get=None, now=None) -> dict:
    """Find candidate editions of a syllabus text from legal open
    sources. Returns a stamped receipt whose candidates are
    UNCONFIRMED — the student confirms the edition before anything
    plans from it."""
    http_get = http_get or _default_http_get
    candidates = []
    for finder in (_openlibrary_candidates, _archive_candidates):
        try:
            candidates.extend(finder(text_ref, http_get))
        except Exception:
            continue  # a source being down never blocks the others
    return _receipt(
        "finder", now, status="awaiting_confirmation",
        text_ref={k: text_ref.get(k) for k in ("title", "isbn", "author")
                  if text_ref.get(k)},
        candidates=candidates, confirmed=None,
        sha256=hashlib.sha256(json.dumps(
            candidates, sort_keys=True).encode()).hexdigest())


def confirm_edition(finder_receipt: dict, index: int, now=None) -> dict:
    """The student's one-tap confirm: mark one candidate as THE
    edition. Planning may only consume a confirmed edition."""
    candidates = finder_receipt.get("candidates") or []
    if not 0 <= index < len(candidates):
        raise ValueError(
            f"edition index {index} out of range ({len(candidates)} "
            "candidates)")
    chosen = dict(candidates[index])
    chosen["confirmed"] = True
    return _receipt("finder-confirm", now, status="confirmed",
                    edition=chosen)


# -------------------------------------------------------------- OCR intake

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


def tesseract_ocr(path) -> str:
    """Default OCR engine: tesseract via subprocess (Apache-2.0)."""
    exe = shutil.which("tesseract")
    if exe is None:
        raise RuntimeError(
            "OCR requires tesseract on PATH (or pass ocr_fn=...); "
            "see FEATURES §1b refs (tesseract / PaddleOCR)")
    done = subprocess.run([exe, str(path), "stdout"],
                          capture_output=True, text=True, timeout=120)
    if done.returncode != 0:
        raise RuntimeError(f"tesseract failed: {done.stderr[:200]}")
    return done.stdout


def ingest_upload(path, ocr_fn=None, pdf_text_fn=None, now=None) -> dict:
    """Ingest one upload in any form into pipeline text.

    .txt/.md read natively; images go through OCR (a photographed
    chapter is a first-class chapter); .pdf/.epub go through the
    injected extractor (MinerU-class structured extraction). Returns
    a stamped receipt {kind, chars, text}."""
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix in (".txt", ".md"):
        text, kind = p.read_text(encoding="utf-8"), "text"
    elif suffix in IMAGE_SUFFIXES:
        text = (ocr_fn or tesseract_ocr)(p)
        kind = "ocr-image"
    elif suffix in (".pdf", ".epub"):
        if pdf_text_fn is None:
            raise RuntimeError(
                f"{suffix} intake needs a structured text extractor "
                "(pass pdf_text_fn=...; FEATURES §1b ref: MinerU)")
        text, kind = pdf_text_fn(p), f"extracted-{suffix[1:]}"
    else:
        raise ValueError(f"unsupported upload type: {suffix or '(none)'}")
    return _receipt("ingest", now, kind=kind, source=p.name,
                    chars=len(text), text=text,
                    sha256=hashlib.sha256(text.encode()).hexdigest())


# ------------------------------------------------------- structure extract

_CHAPTER_RE = re.compile(
    r"^(?:chapter|part)\s+(\d+|[ivx]+)\s*[:.\-]?\s*(.*)$", re.I)
_MD_HEADING = re.compile(r"^(#{1,3})\s+(.*)$")


def extract_structure(text: str) -> dict:
    """Extract chapters -> sections from a document's headings.

    Markdown headings (# chapter, ## section) and plain-text
    "Chapter N: Title" lines both work. Every reading assignment can
    then map to a chapter + section range instead of a page blob.
    Returns {"chapters": [{title, sections: [{title, text}]}]}; a
    document with no chapter marks yields one implicit chapter."""
    chapters = []
    chapter = None
    section = None

    def flush_section():
        nonlocal section
        if section is not None and chapter is not None:
            section["text"] = "\n".join(section.pop("_lines")).strip()
            chapter["sections"].append(section)
        section = None

    def flush_chapter():
        nonlocal chapter
        flush_section()
        if chapter is not None:
            chapters.append(chapter)
        chapter = None

    for line in (text or "").splitlines():
        md = _MD_HEADING.match(line)
        ch = _CHAPTER_RE.match(line.strip())
        if md and len(md.group(1)) == 1:
            flush_chapter()
            chapter = {"title": md.group(2).strip(), "sections": []}
            section = {"title": md.group(2).strip(), "_lines": []}
        elif ch:
            flush_chapter()
            title = (f"Chapter {ch.group(1)}"
                     + (f": {ch.group(2).strip()}" if ch.group(2) else ""))
            chapter = {"title": title.strip(), "sections": []}
            section = {"title": title.strip(), "_lines": []}
        elif md and len(md.group(1)) == 2:
            flush_section()
            if chapter is None:
                chapter = {"title": "Document", "sections": []}
            section = {"title": md.group(2).strip(), "_lines": []}
        else:
            if chapter is None:
                chapter = {"title": "Document", "sections": []}
            if section is None:
                section = {"title": chapter["title"], "_lines": []}
            section["_lines"].append(line)
    flush_chapter()
    if not chapters:
        chapters = [{"title": "Document",
                     "sections": [{"title": "Document",
                                   "text": (text or "").strip()}]}]
    return {"chapters": chapters}


def to_reader_sections(structure: dict) -> list:
    """Map a structure onto study_reader's Section objects so the
    RSVP reader consumes pipeline output directly."""
    out = []
    for ch in structure.get("chapters", []):
        for sec in ch.get("sections", []):
            out.append(Section(
                section_id=hashlib.sha256(
                    f"{ch['title']}|{sec['title']}".encode()
                ).hexdigest()[:12],
                title=sec["title"], content=sec.get("text", ""),
                chapter=ch["title"]))
    return out


# --------------------------------------------------------------- term bank

_GLOSSARY_RE = re.compile(r"^([A-Z][\w \-/()']{1,60}?)\s*(?::|—|--)\s+(.+)$")
_INDEX_RE = re.compile(r"^(.+?)[\s.]*?(\d+(?:\s*[-,]\s*\d+)*)\s*$")


def _parse_glossary(glossary_text: str) -> dict:
    out = {}
    for line in (glossary_text or "").splitlines():
        m = _GLOSSARY_RE.match(line.strip())
        if m:
            out[m.group(1).strip().lower()] = {
                "term": m.group(1).strip(),
                "definition": m.group(2).strip()}
    return out


def _parse_index(index_text: str) -> dict:
    out = {}
    for line in (index_text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        m = _INDEX_RE.match(line)
        if m and not m.group(1).strip().isdigit():
            pages = [int(x) for x in
                     re.findall(r"\d+", m.group(2))]
            if pages:
                out[m.group(1).strip().lower()] = pages
    return out


def build_term_bank(structure: dict, glossary_text: str = "",
                    index_text: str = "", now=None) -> dict:
    """Mine the Index + Glossary into a PER-CHAPTER term bank:
    {chapters: [{chapter, terms: [{term, definition, index_pages,
    sections}]}]}. Glossary terms are the spine; a term joins a
    chapter when it appears in that chapter's text. Deterministic,
    offline."""
    glossary = _parse_glossary(glossary_text)
    index = _parse_index(index_text)
    chapters_out = []
    total = 0
    for ch in structure.get("chapters", []):
        found = {}
        for sec in ch.get("sections", []):
            text = sec.get("text", "")
            for key, entry in glossary.items():
                if re.search(rf"\b{re.escape(key)}\b", text, re.I):
                    slot = found.setdefault(key, {
                        "term": entry["term"],
                        "definition": entry["definition"],
                        "index_pages": index.get(key, []),
                        "sections": []})
                    if sec["title"] not in slot["sections"]:
                        slot["sections"].append(sec["title"])
        terms = sorted(found.values(), key=lambda t: t["term"].lower())
        total += len(terms)
        chapters_out.append({"chapter": ch["title"], "terms": terms})
    receipt = _receipt("term-bank", now, terms=total,
                       chapters=len(chapters_out))
    return {"receipt": receipt, "chapters": chapters_out}


def make_term_lookup(term_bank: dict):
    """Build the study_reader TermLookupFn backed by this bank:
    term -> {term, definition, index_refs, card_ready} or None."""
    flat = {}
    for ch in term_bank.get("chapters", []):
        for t in ch.get("terms", []):
            flat[t["term"].lower()] = t

    def lookup(term: str):
        hit = flat.get(str(term).strip().lower())
        if hit is None:
            return None
        return {"term": hit["term"], "definition": hit["definition"],
                "index_refs": hit.get("index_pages", []),
                "card_ready": True}

    return lookup


def term_bank_cards(term_bank: dict) -> list:
    """The bank feeds SR directly: glossary entries are term cards."""
    items = []
    for ch in term_bank.get("chapters", []):
        for t in ch.get("terms", []):
            items.append({"term": t["term"],
                          "definition": t["definition"],
                          "topic": ch["chapter"]})
    return build_cards(items, source={"kind": "term_bank"})


# ------------------------------------------------------------ term emphasis

def emphasize_terms(text: str, term_bank: dict) -> dict:
    """Split text into segments, marking bank terms. Returns
    {segments: [{text, term?}], terms_found} — the render layer
    emphasizes marked segments in every view (plan, reader, quiz)."""
    terms = {}
    for ch in term_bank.get("chapters", []):
        for t in ch.get("terms", []):
            terms[t["term"].lower()] = t["term"]
    if not terms or not text:
        return {"segments": [{"text": text}] if text else [],
                "terms_found": []}
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(t) for t in
                          sorted(terms, key=len, reverse=True)) + r")\b",
        re.I)
    segments, found, last = [], [], 0
    for m in pattern.finditer(text):
        if m.start() > last:
            segments.append({"text": text[last:m.start()]})
        segments.append({"text": m.group(0), "term": terms[m.group(0)
                                                          .lower()]})
        if terms[m.group(0).lower()] not in found:
            found.append(terms[m.group(0).lower()])
        last = m.end()
    if last < len(text):
        segments.append({"text": text[last:]})
    return {"segments": segments, "terms_found": found}


def term_tap_payload(term: str, term_bank: dict) -> dict:
    """Tap a term -> its definition, its sections, its SR card (the
    obsidian-lexis pattern: highlight, atomic card on tap)."""
    for ch in term_bank.get("chapters", []):
        for t in ch.get("terms", []):
            if t["term"].lower() == str(term).strip().lower():
                cards = build_cards(
                    [{"term": t["term"], "definition": t["definition"]}],
                    source={"kind": "term_bank", "chapter": ch["chapter"]})
                return {"term": t["term"], "definition": t["definition"],
                        "index_pages": t.get("index_pages", []),
                        "sections": t.get("sections", []),
                        "chapter": ch["chapter"],
                        "sr_card": cards[0].to_dict() if cards else None}
    raise ValueError(f"term not in bank: {term!r}")


# --------------------------------------------------------- hypothes.is leg

W3C_ANNOTATION_CONTEXT = "http://www.w3.org/ns/anno.jsonld"
HYPOTHESIS_API = "https://api.hypothes.is/api"


def make_annotation(source_uri: str, quote: str, body_text: str = "",
                    tags=None, annotation_id: str = "") -> dict:
    """Build a W3C Web Annotation (JSON-LD) anchored by a
    TextQuoteSelector — the hypothes.is native model, so annotations
    are portable structured data, not a scrape."""
    import uuid
    ann = {
        "@context": W3C_ANNOTATION_CONTEXT,
        "id": annotation_id or f"urn:uuid:{uuid.uuid4()}",
        "type": "Annotation",
        "motivation": "commenting" if body_text else "highlighting",
        "created": _iso(),
        "target": {
            "source": source_uri,
            "selector": {"type": "TextQuoteSelector", "exact": quote},
        },
        "tags": list(tags or []),
    }
    if body_text:
        ann["body"] = [{"type": "TextualBody", "value": body_text,
                        "purpose": "commenting"}]
    return ann


def annotation_to_card(annotation: dict) -> dict:
    """One tap: a hypothes.is selection becomes an SR card
    (front = the selected quote, back = the annotation body)."""
    target = annotation.get("target") or {}
    quote = ((target.get("selector") or {}).get("exact") or "").strip()
    bodies = annotation.get("body") or []
    back = ""
    for b in bodies:
        if isinstance(b, dict) and b.get("value"):
            back = b["value"]
            break
    if not quote:
        raise ValueError("annotation carries no TextQuoteSelector quote")
    cards = build_cards(
        [{"front": quote, "back": back or quote,
          "tags": list(annotation.get("tags") or [])}],
        source={"kind": "hypothesis-annotation",
                "source_uri": target.get("source", "")})
    return cards[0].to_dict()


def flagged_term_annotation(term_entry: dict, source_uri: str) -> dict:
    """Term Emphasis tie-in: a flagged term becomes a pre-filled
    annotation (tag `term`, body = the bank definition)."""
    return make_annotation(
        source_uri, term_entry["term"],
        body_text=term_entry.get("definition", ""),
        tags=["term", "studysprint"])


class HypothesisClient:
    """Minimal hypothes.is API client (option 3: API-only annotations
    over reader sections). The token comes from the caller or the
    HYPOTHESIS_API_TOKEN environment variable; it is sent as the
    Authorization header and never logged or receipted. Transport is
    injectable for tests."""

    def __init__(self, token: str | None = None, http=None,
                 api_base: str = HYPOTHESIS_API):
        import os
        self.token = token or os.environ.get("HYPOTHESIS_API_TOKEN", "")
        self.api_base = api_base.rstrip("/")
        self._http = http or self._urllib_http

    def _urllib_http(self, method: str, url: str, payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))

    def create_annotation(self, annotation: dict) -> dict:
        if not self.token:
            raise RuntimeError(
                "hypothes.is writes need an API token "
                "(HYPOTHESIS_API_TOKEN)")
        target = annotation.get("target") or {}
        payload = {
            "uri": target.get("source", ""),
            "text": " ".join(
                b.get("value", "") for b in annotation.get("body") or []
                if isinstance(b, dict)),
            "tags": list(annotation.get("tags") or []),
            "target": [{
                "source": target.get("source", ""),
                "selector": [target.get("selector") or {}],
            }],
        }
        return self._http("POST", f"{self.api_base}/annotations", payload)

    def search_annotations(self, uri: str, limit: int = 20) -> dict:
        import urllib.parse
        q = urllib.parse.urlencode({"uri": uri, "limit": limit})
        return self._http("GET", f"{self.api_base}/search?{q}")


def run_pipeline(text_ref: dict, upload_path=None, glossary_text: str = "",
                 index_text: str = "", http_get=None, ocr_fn=None,
                 pdf_text_fn=None, now=None) -> dict:
    """Run the full chain end-to-end and return the stamped bundle:
    finder receipt (unconfirmed until the student confirms) is kept
    separate from the content stages, which run on the upload the
    student provided/confirmed."""
    finder = find_editions(text_ref, http_get=http_get, now=now)
    bundle = {"finder": finder}
    if upload_path is not None:
        ingest = ingest_upload(upload_path, ocr_fn=ocr_fn,
                               pdf_text_fn=pdf_text_fn, now=now)
        structure = extract_structure(ingest.pop("text"))
        bank = build_term_bank(structure, glossary_text, index_text,
                               now=now)
        bundle.update({"ingest": ingest, "structure": structure,
                       "term_bank": bank,
                       "reader_sections": len(to_reader_sections(
                           structure)),
                       "sr_cards": len(term_bank_cards(bank))})
    bundle["receipt"] = _receipt(
        "pipeline", now,
        stages=sorted(k for k in bundle if k != "receipt"))
    return bundle


# ------------------------------------------------- syllabus parse (D)

_WEEKDAY_WORDS = {
    "mon": "Mon", "monday": "Mon", "tue": "Tue", "tues": "Tue",
    "tuesday": "Tue", "wed": "Wed", "wednesday": "Wed",
    "thu": "Thu", "thur": "Thu", "thurs": "Thu", "thursday": "Thu",
    "fri": "Fri", "friday": "Fri", "sat": "Sat", "saturday": "Sat",
    "sun": "Sun", "sunday": "Sun",
}
_COURSE_RE = re.compile(r"\b([A-Z]{2,4})\s*(\d{2,4}[A-Z]?)\b")
_TIME_RANGE_RE = re.compile(
    r"(\d{1,2}):(\d{2})\s*([AaPp][Mm])?\s*[-\u2013]\s*"
    r"(\d{1,2}):(\d{2})\s*([AaPp][Mm])?")
_TIME_RE = re.compile(r"(\d{1,2}):(\d{2})\s*([AaPp][Mm])?")
_ISO_DATE_RE = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
_MONTH_DATE_RE = re.compile(
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+"
    r"(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(20\d{2}))?", re.I)
_ROOM_RE = re.compile(r"\b(?:Room|Rm\.?)\s*([A-Za-z0-9-]+)", re.I)
_KIND_RE = re.compile(r"\b(quiz|midterm|final)\b", re.I)
_MONTHS = {m: i + 1 for i, m in enumerate(
    ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep",
     "oct", "nov", "dec"))}


def _to_24h(hour: int, minute: int, ampm: str | None) -> str:
    if ampm:
        ap = ampm.lower()
        if ap == "pm" and hour != 12:
            hour += 12
        elif ap == "am" and hour == 12:
            hour = 0
    return f"{hour:02d}:{minute:02d}"


def _place_parts(text: str):
    """(building, room) from the text after a time/date fragment."""
    room = None
    m = _ROOM_RE.search(text)
    if m:
        room = m.group(1)
        text = (text[:m.start()] + text[m.end():])
    building = re.sub(r"^[\s,;@\-–—]+|[\s,;]+$", "", text)
    building = re.sub(r"\s+", " ", building).strip(" ,;")
    return (building or None), room


def parse_syllabus_text(text: str, now: datetime | None = None) -> dict:
    """Parse syllabus text (incl. OCR output) into a study_calendar
    intake doc {classes, assessments} — CONSERVATIVE line grammar:

    - a course code (e.g. `BIO 101`) on a line sets the course for
      the records that follow it;
    - a line with weekday names + a time range is a class meeting
      (building/room read from the text after the range);
    - a line naming quiz|midterm|final + a date (ISO or
      `Nov 20[, 2026]`) is an assessment.

    Lines that match nothing are returned as `unmatched` — the
    parser never guesses a record it cannot ground. Output feeds
    study_calendar.intake_calendar unchanged (build D, #4242).
    """
    now = now or datetime.now(timezone.utc)
    classes, assessments, unmatched = [], [], []
    course = None
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        cm = _COURSE_RE.search(line)
        if cm:
            course = f"{cm.group(1)} {cm.group(2)}"
        days = [d for token in re.findall(r"[A-Za-z]+", line)
                if (d := _WEEKDAY_WORDS.get(token.lower()))]
        tr = _TIME_RANGE_RE.search(line)
        if days and tr:
            start = _to_24h(int(tr.group(1)), int(tr.group(2)),
                            tr.group(3) or tr.group(6))
            end = _to_24h(int(tr.group(4)), int(tr.group(5)),
                          tr.group(6) or tr.group(3))
            building, room = _place_parts(line[tr.end():])
            classes.append({"course": course, "days": days,
                            "start": start, "end": end,
                            "building": building, "room": room})
            continue
        km = _KIND_RE.search(line)
        dm = _ISO_DATE_RE.search(line) or _MONTH_DATE_RE.search(line)
        if km and dm:
            if dm.re is _ISO_DATE_RE:
                date = dm.group(0)
            else:
                year = int(dm.group(3) or now.year)
                date = (f"{year:04d}-{_MONTHS[dm.group(1).lower()[:3]]:02d}"
                        f"-{int(dm.group(2)):02d}")
            tm = _TIME_RE.search(line[dm.end():]) or \
                _TIME_RE.search(line)
            when = (_to_24h(int(tm.group(1)), int(tm.group(2)),
                            tm.group(3)) if tm else None)
            building, room = _place_parts(line[dm.end():])
            assessments.append({"course": course,
                                "kind": km.group(1).lower(),
                                "date": date, "time": when,
                                "building": building, "room": room})
            continue
        unmatched.append(line)
    return {"doc": {"classes": classes, "assessments": assessments},
            "counts": {"classes": len(classes),
                       "assessments": len(assessments),
                       "unmatched": len(unmatched)},
            "unmatched": unmatched}


def place_syllabus(parsed: dict, confirmed: bool = False,
                   now: datetime | None = None) -> dict:
    """CONFIRM-GATED placement of a parsed syllabus.

    No confirmation => NO placement: the records are reported as
    awaiting the student's confirm and nothing enters the
    calendar. Confirmed => the doc goes through
    study_calendar.intake_calendar and the calendar receipt is
    the placement record."""
    from study_calendar import intake_calendar
    now = now or datetime.now(timezone.utc)
    counts = parsed.get("counts") or {}
    if not confirmed:
        return _receipt("syllabus-placement", now, placed=False,
                        awaiting="student-confirm",
                        classes=counts.get("classes", 0),
                        assessments=counts.get("assessments", 0))
    calendar = intake_calendar(parsed["doc"], now)
    return _receipt("syllabus-placement", now, placed=True,
                    calendar=calendar)


def run_syllabus_upload(path, confirmed: bool = False, ocr_fn=None,
                        pdf_text_fn=None,
                        now: datetime | None = None) -> dict:
    """Upload => ingest => syllabus parse => confirm-gated
    placement. Provenance is stamped on every receipt: text that
    arrived through OCR carries `source: ocr`."""
    now = now or datetime.now(timezone.utc)
    ingest = ingest_upload(path, ocr_fn=ocr_fn,
                           pdf_text_fn=pdf_text_fn, now=now)
    text = ingest.pop("text")
    source = "ocr" if ingest.get("kind") == "ocr-image" else "upload"
    parsed = parse_syllabus_text(text, now=now)
    placement = place_syllabus(parsed, confirmed=confirmed, now=now)
    return {"ingest": ingest, "provenance": {"source": source},
            "parse": {"counts": parsed["counts"],
                      "unmatched": parsed["unmatched"]},
            "placement": placement,
            "receipt": _receipt("syllabus-upload", now, flow="syllabus",
                                placed=placement.get("placed", False),
                                provenance=source)}


def ingest_any(path, confirmed: bool = False, ocr_fn=None,
               pdf_text_fn=None, now: datetime | None = None) -> dict:
    """THE one core ingestion path every surface calls (build D):
    an upload that parses as a syllabus takes the syllabus flow
    (records + confirm-gated placement); anything else takes the
    textbook content flow (structure => term bank => SR cards).
    The edition finder stays a separate leg (run_pipeline)."""
    now = now or datetime.now(timezone.utc)
    probe = ingest_upload(path, ocr_fn=ocr_fn, pdf_text_fn=pdf_text_fn,
                          now=now)
    text = probe.pop("text")
    parsed = parse_syllabus_text(text, now=now)
    if parsed["counts"]["classes"] or parsed["counts"]["assessments"]:
        placement = place_syllabus(parsed, confirmed=confirmed,
                                   now=now)
        source = ("ocr" if probe.get("kind") == "ocr-image"
                  else "upload")
        return {"flow": "syllabus", "ingest": probe,
                "provenance": {"source": source},
                "parse": {"counts": parsed["counts"],
                          "unmatched": parsed["unmatched"]},
                "placement": placement,
                "receipt": _receipt("ingest-any", now, flow="syllabus",
                                    placed=placement.get("placed",
                                                           False))}
    structure = extract_structure(text)
    # a single-file textbook carries its back matter inline: a
    # bare "Glossary" / "Index" heading switches the sink, and
    # that text becomes the term bank's spine (build_term_bank's
    # contract: glossary terms join the chapters they appear in)
    glossary_lines, index_lines, sink = [], [], None
    for line in text.splitlines():
        head = line.strip().lower().rstrip(":")
        if head == "glossary":
            sink = glossary_lines
            continue
        if head == "index":
            sink = index_lines
            continue
        if sink is not None:
            sink.append(line)
    bank = build_term_bank(structure, "\n".join(glossary_lines),
                           "\n".join(index_lines), now=now)
    cards = term_bank_cards(bank)
    return {"flow": "textbook", "ingest": probe,
            "provenance": {"source": "ocr" if probe.get("kind")
                           == "ocr-image" else "upload"},
            "structure": {"chapters": len(structure.get("chapters")
                                           or [])},
            "term_bank": {"terms": bank["receipt"]["terms"]},
            "sr_cards": len(cards),
            "receipt": _receipt("ingest-any", now, flow="textbook",
                                sr_cards=len(cards))}


__all__ = [
    "find_editions", "confirm_edition", "ingest_upload", "tesseract_ocr",
    "extract_structure", "to_reader_sections", "build_term_bank",
    "make_term_lookup", "term_bank_cards", "emphasize_terms",
    "term_tap_payload", "make_annotation", "annotation_to_card",
    "flagged_term_annotation", "HypothesisClient", "run_pipeline",
    "parse_syllabus_text", "place_syllabus", "run_syllabus_upload",
    "ingest_any",
    "PIPELINE_RECEIPT_SCHEMA",
]
