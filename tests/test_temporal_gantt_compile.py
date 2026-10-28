"""N4 Gantt compiler tests."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "gantt_compile", ROOT / "scripts" / "temporal" / "gantt_compile.py")
gc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gc)

PLAN = """oracle facts | T0 | T0 | -
panel rounds | T0 | T0 | oracle facts
shadow lane (5% traffic) | T0+1d | T0+7d | panel rounds
promote or park | T0+7d | T0+7d | shadow lane (5% traffic)"""


def test_linear_plan_compiles():
    out = gc.compile_text(PLAN)
    assert out["valid"] and out["violations"] == []
    assert out["stages"] == ["oracle facts", "panel rounds",
                             "shadow lane (5% traffic)", "promote or park"]
    assert out["critical_path_stages"] == 4
    assert out["dependency_closure"]["promote or park"] == [
        "oracle facts", "panel rounds", "shadow lane (5% traffic)"]


def test_cycle_and_unknown_dep_fail():
    bad = "a | T0 | T0 | b\nb | T0 | T0 | a"
    out = gc.compile_text(bad)
    assert not out["valid"] and any("cycle" in v for v in out["violations"])
    out2 = gc.compile_text("a | T0 | T0 | ghost")
    assert not out2["valid"] and any("unknown dependency" in v for v in out2["violations"])


def test_empty_plan_fails():
    assert not gc.compile_text("no phases here")["valid"]
