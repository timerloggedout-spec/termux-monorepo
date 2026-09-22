import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[2]/"scripts"/"ops"))
from hitl_control_plane import bounded_replay,make_projection,propose_command,transition,to_gource

def test_proposal_is_stable():
    a=propose_command("reply-to-comment","https://github.com/o/r/issues/1#issuecomment-2",["sha:abc","comment:2"])
    b=propose_command("reply-to-comment","https://github.com/o/r/issues/1#issuecomment-2",["sha:abc","comment:2"])
    assert a.command_id==b.command_id and a.approval_required and a.state=="DRAFT"

def test_dispatch_requires_approval():
    assert transition("APPROVED","DISPATCHED",approved=True)=="DISPATCHED"
    try: transition("APPROVED","DISPATCHED")
    except PermissionError: pass
    else: raise AssertionError("dispatch bypassed HITL approval")

def test_replay_projection():
    events=[{"event_id":f"e{i}","occurred_at":f"2026-01-01T00:00:0{i}Z","scope":{"entity_id":f"issue:{i}"}} for i in range(4)]
    selected=bounded_replay(events,.25,.75); p=make_projection(selected,"abc1234","interactive")
    assert len(selected)==2 and p.event_count==2 and p.snapshot_id.startswith("snapshot-")

def test_gource_same_range():
    e=[{"event_id":"e1","occurred_at":"2026-01-01T00:00:00Z","actor":{"id":"owner"},"scope":{"entity_id":"pr:7"}}]
    assert "owner|M|pr:7" in to_gource(e)
