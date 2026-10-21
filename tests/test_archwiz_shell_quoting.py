import importlib.util
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "archwiz" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_safe_call(module, method, args, path_fragments, expected_args):
    captured = []
    def fake_run(command, **kwargs):
        captured.append(command)
        return "", "", 0
    with patch.object(module, "run", side_effect=fake_run):
        getattr(module, method)(args)
    assert len(captured) == 1
    command = captured[0]
    tokens = module.shlex.split(command)
    assert ";" not in tokens
    for arg in expected_args:
        assert arg in tokens
    for frag in path_fragments:
        assert frag in tokens


def test_aether_dep_quotes_attacker_argument_and_script_path():
    module = load("aether")
    module.LLM_MAP = "/tmp/a path; touch /tmp/pathpwn"
    assert_safe_call(module, "cmd_dep", ["x; touch /tmp/pwned"],
                     [module.LLM_MAP + "/depgraph.sh"], ["x; touch /tmp/pwned"])


def test_forge_dep_quotes_attacker_argument_and_script_path():
    module = load("forge")
    module.LLM_MAP = "/tmp/a path; touch /tmp/pathpwn"
    assert_safe_call(module, "cmd_dep", ["x; touch /tmp/pwned"],
                     [module.LLM_MAP + "/depgraph.sh"], ["x; touch /tmp/pwned"])


def test_aether_bookmark_and_lexicon_quote_each_argument():
    module = load("aether")
    args = ["name; touch /tmp/pwned", "$(touch /tmp/pwned)"]
    for method, path in (("cmd_bookmark", module.ARCHWIZ + "/lexicon_mark.py"),
                         ("cmd_lexicon", module.HOME + "/workspace/compression_sandbox/cedrlang/cid.py")):
        assert_safe_call(module, method, args, [path], args)
