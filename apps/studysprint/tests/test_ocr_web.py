"""Qualifications closure ② (surfaces 0.5.1): OCR in the
webApp intake — tesseract.js (WASM) runs the core's OCR leg
in the browser: photo -> OCR text -> the ingestion grammar,
provenance stamped `ocr`. The "awaiting core OCR" qualifier
(the browser-cannot-run-tesseract platform limit) is retired.

Batteries: the pure helpers in node; the wiring statically;
and an env-gated end-to-end — the SAME photo fixture through
the core's tesseract (study_pipeline.tesseract_ocr) vs the
web port's engine (tesseract.js 5.1.1 in node) — gated on
STUDYSPRINT_OCR_E2E=1 + a tesseract binary + TESSERACT_JS_PATH
pointing at an installed tesseract.js package, because CI
runners carry neither by default. Run locally it is a real
two-engine agreement measurement, not a stub.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
APP = HERE.parent
WEB = APP / "web"
FIXTURE = HERE / "fixtures" / "ocr_page.png"


def test_ocr_wiring_pinned():
    js = (WEB / "app.js").read_text()
    assert "tesseract.js@5.1.1" in js  # pinned engine build
    assert 'provenance: "ocr"' in js  # the core's ocr-image stamp
    assert 'status: "awaiting-ocr-engine"' in js  # honest fallback
    assert "awaiting-core-ocr" not in js  # the qualifier is gone
    assert "createWorker" in js


def test_ocr_pure_helpers_battery():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not available")
    app_js = (WEB / "app.js").read_text()
    start = app_js.index("function computeDayIndex")
    end = app_js.index("/* ---------------- loading")
    helpers = app_js[start:end]
    script = helpers + """
const assert = require("assert");
assert.strictEqual(normalizeOcrText("a  \\n\\n\\n\\nb "), "a\\n\\nb");
const agree = ocrAgreement(
  "Quiz 1 on Oct 14 cell structure",
  "quiz 1 on oct 14 — cell structure!");
assert.ok(agree > 0.8, agree);
assert.strictEqual(ocrAgreement("", "x"), 0);
console.log("ocr helpers ok");
"""
    proc = subprocess.run([node, "-e", script], capture_output=True,
                          text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr


@pytest.mark.skipif(os.environ.get("STUDYSPRINT_OCR_E2E") != "1",
                    reason="OCR e2e env not provisioned "
                           "(STUDYSPRINT_OCR_E2E=1 + tesseract CLI "
                           "+ TESSERACT_JS_PATH)")
def test_ocr_two_engine_agreement(tmp_path):
    import sys
    sys.path.insert(0, str(APP))
    from study_pipeline import tesseract_ocr
    core_text = tesseract_ocr(str(FIXTURE))
    pkg = os.environ["TESSERACT_JS_PATH"]
    lang = os.environ["TESSERACT_LANG_PATH"]
    script = f"""
const path = require("path");
const {{ createWorker }} = require({json.dumps(pkg)});
(async () => {{
  const w = await createWorker("eng", 1,
    {{ langPath: {json.dumps(lang)}, gzip: true,
       cacheMethod: "none", logger: () => {{}} }});
  const {{ data }} = await w.recognize({json.dumps(str(FIXTURE))});
  require("fs").writeFileSync({json.dumps(str(tmp_path / "web.txt"))},
    data.text);
  await w.terminate();
}})().catch((e) => {{ console.error(e.message); process.exit(1); }});
"""
    proc = subprocess.run(["node", "-e", script], capture_output=True,
                          text=True, timeout=300)
    assert proc.returncode == 0, proc.stderr
    web_text = (tmp_path / "web.txt").read_text()
    for needle in ("midterm", "photosynthesis", "quiz",
                   "cell structure"):
        assert needle in core_text.lower(), needle
        assert needle in web_text.lower(), needle
    # token agreement between the two engines over the fixture
    def toks(s):
        return set("".join(c if c.isalnum() else " "
                           for c in s.lower()).split())
    a, b = toks(core_text), toks(web_text)
    agreement = len(a & b) / max(len(a), len(b))
    assert agreement >= 0.85, agreement
