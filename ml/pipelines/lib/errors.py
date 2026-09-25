class PipelineError(Exception):
    """Base keep-alive error."""


class GateBlocked(PipelineError):
    def __init__(self, number: object, reasons: list[str]) -> None:
        super().__init__(f"PR {number} blocked: {', '.join(reasons)}")
        self.number = number
        self.reasons = reasons


class FixtureError(PipelineError):
    pass
