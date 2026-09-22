class GateBlocked(RuntimeError):
    """Promote packet refused."""


class SnapshotError(RuntimeError):
    """Fixture / snapshot unreadable."""


class StageHalted(RuntimeError):
    """DAG halted on FAILED stage."""
