from pathlib import Path


ACTION = Path(".github/actions/model-router/action.yml")
CONSUMERS = [
    Path(".github/workflows/gemini-triage.yml"),
    Path(".github/workflows/gemini-review.yml"),
    Path(".github/workflows/gemini-invoke.yml"),
    Path(".github/workflows/gemini-after-peers.yml"),
]


def test_model_router_action_exposes_observe_only_contract():
    source = ACTION.read_text(encoding="utf-8")
    assert "capability-spine-observe:" in source
    assert "default: 'true'" in source
    assert "decision:" in source
    assert "decision-summary:" in source
    assert "CAPABILITY_SPINE_OBSERVE" in source


def test_all_existing_router_consumers_publish_only_the_bounded_summary():
    for workflow in CONSUMERS:
        source = workflow.read_text(encoding="utf-8")
        assert "Record capability-spine observe decision" in source, workflow
        assert "steps.router.outputs.decision-summary" in source, workflow
        assert "Execution selection remains unchanged during AR-17 observation." in source or \
            "The verified peer gate and existing second-pass execution route remain authoritative." in source
        assert "steps.router.outputs.provider" in source, workflow


def test_event_classifier_remains_an_event_classifier_not_a_second_router():
    source = Path(".github/workflows/gemini-dispatch.yml").read_text(encoding="utf-8")
    assert "command', 'defer-peers'" in source
    assert "uses: ./.github/actions/model-router" not in source
