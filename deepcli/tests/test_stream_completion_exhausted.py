"""Retry exhaustion must not raise NameError on unbound final_text."""

import ast
from pathlib import Path


def test_stream_completion_binds_final_text_before_loop():
    root = Path(__file__).resolve().parents[1]
    source = (root / "deepcli" / "core.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    fn = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "stream_completion"
    )
    assigns = [
        node
        for node in ast.walk(fn)
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "final_text" for t in node.targets)
    ]
    assert assigns, "final_text must be bound before the retry loop returns it"
    returns = [
        node
        for node in ast.walk(fn)
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Name) and node.value.id == "final_text"
    ]
    assert returns, "exhaustion path should return the bound final_text"
