#!/usr/bin/env python3
"""V4 contract-first suite: one schema, validators in 2 languages.

Runs the Python and JavaScript evidence-envelope validators over one
payload set and asserts: (1) the valid payload passes both; (2) every
invalid payload is rejected by BOTH languages; (3) the two languages
return identical violation lists; (4) a multi-broken payload yields
AGGREGATED violations (>1), never first-fail. Exit 0 = suite pass.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_envelope import validate as validate_py  # noqa: E402

SHA = "a" * 64
VALID = {"workflow_id": "kill-resume-unit-1", "unit_id": "unit-1",
         "receipt_sha256": SHA, "receipt_count": 1,
         "history_sha256": "b" * 64, "unknown_outcomes": []}
PAYLOADS = {
    "valid": VALID,
    "missing_fields": {"workflow_id": "x"},
    "bad_digests": {**VALID, "receipt_sha256": "XYZ", "history_sha256": "short"},
    "bad_count": {**VALID, "receipt_count": -2},
    "extra_property": {**VALID, "surprise": True},
    "multi_broken": {"unit_id": "", "receipt_sha256": "nope",
                     "receipt_count": "one", "unknown_outcomes": {}},
}


def validate_js(payload: dict) -> list[str]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(payload, fh)
        path = fh.name
    out = subprocess.run(["node", str(Path(__file__).resolve().parent / "validate_envelope.js"), path],
                         capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        raise RuntimeError(f"node validator failed: {out.stderr}")
    return json.loads(out.stdout)


def main() -> int:
    results = {}
    failures = []
    for name, payload in PAYLOADS.items():
        py, js = validate_py(payload), validate_js(payload)
        agree = py == js
        results[name] = {"py_violations": len(py), "js_violations": len(js), "agree": agree}
        if not agree:
            failures.append(f"{name}: language divergence py={py} js={js}")
        if name == "valid" and (py or js):
            failures.append(f"valid payload rejected: py={py} js={js}")
        if name != "valid" and (not py or not js):
            failures.append(f"{name}: invalid payload accepted")
    if results["multi_broken"]["py_violations"] < 4:
        failures.append(f"multi_broken not aggregated: {results['multi_broken']}")
    print(json.dumps({"verdict": "PASS" if not failures else "FAIL",
                      "results": results, "failures": failures}, indent=1))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
