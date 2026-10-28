import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "ace_watch"))
from check import classify  # noqa: E402

BASELINE = ("<html><body><p>Agent Compute Engine will be available in "
            "preview in the coming months.</p></body></html>")


def test_baseline_state_no_signal():
    r = classify(BASELINE)
    assert r["moved"] is False and r["signals"] == []
    assert r["baseline_intact"] is True


def test_ga_language_signals():
    r = classify(BASELINE + "<p>Agent Compute Engine is now generally available.</p>")
    assert r["moved"] and "ga" in r["signals"]


def test_preview_open_signals():
    r = classify(BASELINE + "<p>The preview is now open to all customers.</p>")
    assert r["moved"] and "preview_open" in r["signals"]


def test_script_and_style_stripped():
    html = "<script>generally available</script><style>now in preview</style>" + BASELINE
    r = classify(html)
    assert r["moved"] is False
