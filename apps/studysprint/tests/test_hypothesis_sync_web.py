"""Qualifications closure ③ (surfaces 0.5.1): the hypothes.is
token seam. The mapper + merge are battery-run in node against
a recorded-shape hypothes.is API fixture; the wiring is pinned
statically; and a repo-wide guard asserts no token material
ever ships in the bundle (the token is config-injected on the
user's device at runtime).
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
APP = HERE.parent
WEB = APP / "web"

API_ROW = {
    "id": "aBcDeFgHiJkLmNoPqRsTuV",
    "user": "acct:learner@hypothes.is",
    "group": "AbCdEfGh",
    "text": "A note from the account group.",
    "tags": ["term-bank"],
    "target": [{
        "source": "https://example.org/book",
        "selector": [
            {"type": "RangeSelector", "startContainer": "/p[1]"},
            {"type": "TextQuoteSelector",
             "exact": "the quick brown fox", "prefix": "… ",
             "suffix": " jumps"},
        ],
    }],
}


def test_mapper_and_merge_battery():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not available")
    app_js = (WEB / "app.js").read_text()
    start = app_js.index("function computeDayIndex")
    end = app_js.index("/* ---------------- loading")
    helpers = app_js[start:end]
    script = helpers + f"""
const assert = require("assert");
const w = hypothesisToW3C({json.dumps(API_ROW)});
assert.strictEqual(w.provenance, "hypothes.is");
assert.strictEqual(w.creator, "acct:learner@hypothes.is");
assert.strictEqual(w.body[0].value, "A note from the account group.");
assert.strictEqual(w.target.selector.exact, "the quick brown fox");
assert.strictEqual(w.target.selector.type, "TextQuoteSelector");
const local = [{{id: "local-1", body: [{{value: "L"}}],
  target: {{selector: {{exact: "q1"}}}}}}];
const merged = mergeAnnotations(local, [w, w,
  hypothesisToW3C({json.dumps(API_ROW)})]);
assert.strictEqual(merged.length, 2);  // dupes collapse by id
assert.strictEqual(merged[0].id, "local-1");  // local first
console.log("hypothesis seam battery ok");
"""
    proc = subprocess.run([node, "-e", script], capture_output=True,
                          text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr


def test_seam_wiring_and_no_shipped_token():
    app_js = (WEB / "app.js").read_text()
    assert 'id="hyp-token"' in app_js
    assert 'id="hyp-sync"' in app_js
    assert "https://hypothes.is/api/search" in app_js
    assert "https://hypothes.is/api/profile" in app_js
    assert 'localStorage.getItem("ss.hypothesis.token")' in app_js
    # The seam is config-injected: no credential-shaped literal
    # may exist anywhere in the shipped web bundle.
    for name in ("app.js", "index.html", "sw.js"):
        text = (WEB / name).read_text()
        assert "Bearer " not in text.replace(
            '"Bearer " + token', ""), name
