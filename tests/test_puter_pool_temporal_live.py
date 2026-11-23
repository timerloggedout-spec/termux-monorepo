from __future__ import annotations

import asyncio
import json
import os
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import pytest
from temporalio.client import Client
from temporalio.worker import Worker

from scripts.temporal.puter_pool_observation.activities import collect_puter_pool_observation
from scripts.temporal.puter_pool_observation.contracts import PuterPoolObservationInput
from scripts.temporal.puter_pool_observation.workflow import PuterPoolObservationWorkflow, TASK_QUEUE


class PoolHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        payloads = {
            "/v1/models": {"object": "list", "data": [{"id": "synthetic-model"}]},
            "/api/stats": {
                "totalAccounts": 3, "activeAccounts": 2, "disabledAccounts": 1,
                "exhaustedAccounts": 0, "errorAccounts": 0, "totalRequests": 14,
                "successfulRequests": 12, "failedRequests": 2, "averageLatency": 180,
                "uptime": 600, "strategy": "least-used",
            },
            "/api/queue": {"queuedRequests": 1, "activeRequests": 1},
            "/healthz": {"status": "ok"},
            "/readyz": {"status": "ready", "activeAccounts": 2},
        }
        body = json.dumps(payloads.get(self.path, {})).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        return


def test_temporal_workflow_collects_and_correlates_live_local_pool(monkeypatch, tmp_path):
    async def run_workflow():
        server = ThreadingHTTPServer(("127.0.0.1", 0), PoolHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        event_path = tmp_path / "agent_telemetry_stream.json"
        runtime_path = tmp_path / "puter-pool-runtime.json"
        monkeypatch.setenv("PUTER_POOL_BASE_URL", f"http://127.0.0.1:{server.server_port}")
        monkeypatch.setenv("PUTER_POOL_API_KEY", "synthetic-test-key")
        monkeypatch.setenv("PUTER_POOL_EVENT_OUT", str(event_path))
        monkeypatch.setenv("PUTER_POOL_RUNTIME_OUT", str(runtime_path))
        address = os.environ.get("TEMPORAL_ADDRESS", "127.0.0.1:7233")
        workflow_id = "puter-pool-ci-" + uuid.uuid4().hex[:12]
        client = await Client.connect(address)
        request = PuterPoolObservationInput(
            task_or_entry_ref="QUE-CI-1",
            doe_run_id="DOE-CI-1",
            workflow_run_id="GHA-CI-1",
            run_attempt=1,
            interval_seconds=60,
        )
        try:
            async with Worker(
                client,
                task_queue=TASK_QUEUE,
                workflows=[PuterPoolObservationWorkflow],
                activities=[collect_puter_pool_observation],
                activity_executor=ThreadPoolExecutor(max_workers=2),
            ):
                handle = await client.start_workflow(
                    PuterPoolObservationWorkflow.run,
                    request,
                    id=workflow_id,
                    task_queue=TASK_QUEUE,
                )
                result = {}
                for _ in range(100):
                    result = await handle.query(PuterPoolObservationWorkflow.last_result)
                    if result:
                        break
                    await asyncio.sleep(0.2)
                assert result, "Temporal activity produced no observation"
                await handle.signal(PuterPoolObservationWorkflow.stop)
                final = await handle.result()
                assert final["event_id"] == result["event_id"]
            event = json.loads(event_path.read_text(encoding="utf-8").splitlines()[-1])
            runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
            assert event["provider"] == "g4f/Puter"
            assert event["attributes"]["task_or_entry_ref"] == "QUE-CI-1"
            assert event["attributes"]["doe_run_id"] == "DOE-CI-1"
            assert event["attributes"]["temporal_workflow_id"] == workflow_id
            assert event["attributes"]["total_requests"] == 14
            assert runtime["pool"]["model_ids"] == ["synthetic-model"]
            assert runtime["correlation"]["workflow_run_id"] == "GHA-CI-1"
            assert runtime["quota"]["used"] is None
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    asyncio.run(run_workflow())
