"""Perpetual, signal-stoppable Temporal observation for the Puter Pool datastore."""
from __future__ import annotations

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from .contracts import PuterPoolObservationInput

TASK_QUEUE = "puter-pool-observability"


@workflow.defn
class PuterPoolObservationWorkflow:
    def __init__(self) -> None:
        self._stop_requested = False
        self._last_observation: dict = {}

    @workflow.signal
    def stop(self) -> None:
        self._stop_requested = True

    @workflow.query
    def last_result(self) -> dict:
        return self._last_observation

    @workflow.run
    async def run(self, request: PuterPoolObservationInput) -> dict:
        if not 60 <= request.interval_seconds <= 3600:
            raise ValueError("interval_seconds must be between 60 and 3600")
        if request.run_attempt < 1:
            raise ValueError("run_attempt must be positive")
        while not self._stop_requested:
            self._last_observation = await workflow.execute_activity(
                "collect_puter_pool_observation",
                request,
                start_to_close_timeout=timedelta(seconds=45),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=2),
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=2,
                ),
            )
            if not self._stop_requested:
                try:
                    await workflow.wait_condition(
                        lambda: self._stop_requested,
                        timeout=timedelta(seconds=request.interval_seconds),
                    )
                except TimeoutError:
                    pass
        return self._last_observation
