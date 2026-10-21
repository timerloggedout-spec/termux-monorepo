"""Offline workflow contracts: no provider call or credentials are needed."""
import itertools
from pathlib import Path

import yaml


PATH = Path(__file__).resolve().parents[1] / ".github/workflows/provider-batch.yml"


def workflow():
    return yaml.safe_load(PATH.read_text())


def enabled(expression, *, event, trusted, flags):
    expression = expression.replace(
        "github.ref == format('refs/heads/{0}', github.event.repository.default_branch)",
        str(trusted),
    ).replace("github.event_name == 'workflow_dispatch'", str(event == "workflow_dispatch"))
    for name, value in flags.items():
        expression = expression.replace("inputs." + name, str(value))
    return eval(expression.replace("&&", " and ").replace("!", " not "), {"__builtins__": {}}, {})


def test_private_quota_is_manual_default_off_and_no_schedule():
    doc = workflow()
    events = doc.get("on", doc.get(True))  # YAML 1.1 treats 'on' as a boolean.
    assert "schedule" not in events
    assert events["workflow_dispatch"]["inputs"]["observe_openrouter_quota"] == {
        "description": "One private read-only OpenRouter current-key GET; status only, no inference or artifacts",
        "type": "boolean", "default": False,
    }
    job = doc["jobs"]["private_openrouter_quota"]
    assert job["permissions"] == {"contents": "read"}
    assert job["needs"] == "contracts"
    assert job["steps"][0]["with"] == {"ref": "${{ github.sha }}", "persist-credentials": False}


def test_all_flag_combinations_isolate_private_read_from_other_provider_jobs():
    jobs = workflow()["jobs"]
    names = ["observe_openrouter_quota", "diagnose_free_limits", "execute_free_smoke", "observe_public_research"]
    for values in itertools.product((False, True), repeat=4):
        flags = dict(zip(names, values))
        for event in ("workflow_dispatch", "pull_request", "push", "schedule"):
            for trusted in (False, True):
                active = {name: enabled(jobs[name]["if"], event=event, trusted=trusted, flags=flags)
                          for name in ("private_openrouter_quota", "diagnose", "observe")}
                expected = event == "workflow_dispatch" and trusted and values == (True, False, False, False)
                assert bool(active["private_openrouter_quota"]) == expected
                if flags["observe_openrouter_quota"]:
                    assert not active["diagnose"] and not active["observe"]


def test_private_job_has_one_get_cli_no_artifact_and_ephemeral_private_output():
    job = workflow()["jobs"]["private_openrouter_quota"]
    assert len(job["steps"]) == 2
    step = job["steps"][1]
    assert step["env"] == {"OPENROUTER_API_KEY": "${{ secrets.OPENROUTER_API_KEY }}"}
    run = step["run"]
    assert "umask 077" in run and "mktemp -d" in run
    assert "trap 'rm -rf -- \"$private_dir\"' EXIT" in run
    assert run.count("provider_quota_service.py") == 1
    assert "--service openrouter.key" in run and "--observe" in run
    assert '--private-out "$private_dir/observation.json"' in run
    for forbidden in ("cat ", "upload-artifact", "GITHUB_STEP_SUMMARY", "provider_free_smoke", "quota_poll", "curl", "tee "):
        assert forbidden not in run
    assert "secrets." not in str(workflow()["jobs"]["contracts"])


def test_new_contracts_run_on_pull_requests_and_pushes():
    doc = workflow()
    events = doc.get("on", doc.get(True))
    commands = str(doc["jobs"]["contracts"])
    for filename in ("tests/test_provider_quota_openrouter.py", "tests/test_provider_quota_private_workflow.py"):
        assert filename in commands
        assert filename in events["pull_request"]["paths"]
        assert filename in events["push"]["paths"]


def test_observation_registry_does_not_change_legacy_routing_weights():
    import datetime as dt
    import json
    from scripts import provider_quota_service, quota_poll

    root = PATH.parents[2]
    registry = json.loads((root / "ops/quota/registry.json").read_text())
    row = next(s for s in registry["services"] if s["id"] == "openrouter.key")
    assert row["lane"] == "model-observation"
    record = quota_poll.record(row, None, dt.datetime.now(dt.timezone.utc))
    assert record["lane_id"] not in {"quota-model", "quota-deploy", "quota-data"}
    assert "openrouter.key" not in quota_poll.LIVE
    assert all(fn.__module__ != provider_quota_service.__name__ for fn in quota_poll.MULTI)
