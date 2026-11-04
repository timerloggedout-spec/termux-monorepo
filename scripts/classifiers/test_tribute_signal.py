import tribute_signal as ts

M = "maintainer"
C = "contributor"


def pr(**kw):
    base = {"pr_ref": "x/y#1", "repo": "x/y", "number": 1, "title": "t",
            "state": "open", "comments": [], "reviews": [], "timeline": []}
    base.update(kw)
    return base


def com(i, role, body, at="2026-01-01T00:00:00Z"):
    return {"id": i, "author": "a", "author_role": role, "body": body,
            "created_at": at}


def rev(i, role, state, body, at="2026-01-01T00:00:00Z"):
    return {"id": i, "author": "a", "author_role": role, "state": state,
            "body": body, "created_at": at}


def test_rejection_placeholder():
    v = ts.classify(pr(comments=[com(1, M, "This is just a placeholder, closing.")],
                       state="closed_unmerged"))
    assert v["primary_signal"] == "explicit-rejection"
    assert v["rejection_subtype"] == "placeholder"
    assert v["confidence_overall"] == "high"


def test_rejection_quality():
    v = ts.classify(pr(comments=[com(1, M, "This looks AI-generated, low quality.")]))
    assert v["primary_signal"] == "explicit-rejection"
    assert v["rejection_subtype"] == "quality"


def test_close_alone_not_rejection():
    v = ts.classify(pr(state="closed_unmerged",
                       comments=[com(1, M, "Superseded by #42, thanks anyway.")]))
    assert v["primary_signal"] != "explicit-rejection"


def test_cleanup():
    v = ts.classify(pr(comments=[com(1, M, "Please remove the generated file and clean up the stray file.")]))
    assert "cleanup" in v["rules_fired"]


def test_adjustment_loop_made():
    v = ts.classify(pr(
        reviews=[rev(1, M, "CHANGES_REQUESTED", "Please fix the failing test",
                     at="2026-01-01T00:00:00Z")],
        timeline=[{"type": "committed", "at": "2026-01-02T00:00:00Z",
                   "actor": "dev"}],
    ))
    assert v["adjustment"]["required"] is True
    assert v["adjustment"]["happened"] is True
    assert v["primary_signal"] == "adjustment-made"


def test_adjustment_needed_open():
    v = ts.classify(pr(reviews=[rev(1, M, "CHANGES_REQUESTED", "")]))
    assert v["primary_signal"] == "adjustment-needed"
    assert v["adjustment"]["happened"] is False
    assert v["confidence_overall"] == "medium"  # state-only evidence


def test_positive_approval():
    v = ts.classify(pr(reviews=[rev(1, M, "APPROVED", "LGTM, thank you!")],
                       state="merged"))
    assert v["primary_signal"] == "positive"


def test_neutral_silence():
    v = ts.classify(pr(state="open"))
    assert v["primary_signal"] == "neutral"


def test_contributor_words_not_signal():
    v = ts.classify(pr(comments=[com(1, C, "This is spam and low quality")]))
    assert v["primary_signal"] == "neutral"


def test_bot_words_not_signal():
    v = ts.classify(pr(comments=[com(1, "bot", "placeholder check failed",
                                     )]))
    assert v["primary_signal"] == "neutral"


def test_rejection_beats_positive_precedence():
    v = ts.classify(pr(comments=[
        com(1, M, "Thanks for the effort"),
        com(2, M, "Closing: this is a placeholder with no changes."),
    ], state="closed_unmerged"))
    assert v["primary_signal"] == "explicit-rejection"
    assert "positive" in v["rules_fired"]


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for f in fns:
        f()
        print("ok", f.__name__)
    print(len(fns), "passed")
