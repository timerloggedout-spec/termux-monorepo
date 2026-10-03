from scripts.routing_topology import Participant, execute_route


def test_series_records_actual_execution():
    seen = []

    def a(value):
        seen.append(("a", value))
        return value + 1

    def b(value):
        seen.append(("b", value))
        return value * 2

    evidence = execute_route(
        "series",
        [Participant("a", a), Participant("b", b)],
        2,
    )

    assert evidence["execution_status"] == "EXECUTED"
    assert evidence["executed_participants"] == ["a", "b"]
    assert evidence["outputs"] == [3, 6]
    assert seen == [("a", 2), ("b", 3)]


def test_parallel_is_bounded_and_observable():
    evidence = execute_route(
        "parallel",
        [Participant("a", lambda x: x + "a"), Participant("b", lambda x: x + "b")],
        "x",
        max_workers=2,
    )

    assert evidence["execution_status"] == "EXECUTED"
    assert set(evidence["executed_participants"]) == {"a", "b"}
    assert set(evidence["outputs"]) == {"xa", "xb"}
    assert evidence["rounds"] == 1


def test_volley_stops_on_explicit_condition():
    evidence = execute_route(
        "volley",
        [Participant("a", lambda x: x + 1), Participant("b", lambda x: x + 1)],
        0,
        max_rounds=5,
        stop=lambda value, round_no: value >= 3,
    )

    assert evidence["execution_status"] == "EXECUTED"
    assert evidence["executed_participants"] == ["a", "b", "a"]
    assert evidence["rounds"] == 3
    assert evidence["outputs"][-1] == 3


def test_failure_is_not_reported_as_success():
    def broken(_):
        raise RuntimeError("boom")

    evidence = execute_route("single", [Participant("broken", broken)], None)

    assert evidence["execution_status"] == "FAILED"
    assert evidence["errors"] == [{"participant": "broken", "error_class": "RuntimeError"}]


def test_dynamic_selector_changes_execution_without_provider_priority():
    participants = [
        Participant("left", lambda _: "left"),
        Participant("right", lambda _: "right"),
    ]
    evidence = execute_route(
        "dynamic",
        participants,
        {"choose": "right"},
        selector=lambda rows, ctx: next(p for p in rows if p.name == ctx["choose"]),
    )

    assert evidence["executed_participants"] == ["right"]
    assert evidence["outputs"] == ["right"]
