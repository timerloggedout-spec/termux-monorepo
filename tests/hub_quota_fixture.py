"""Test-only canonical quota records; fake providers still traverse real admission."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

from fastapi.testclient import TestClient
from llm_api_hub.server.admission import QuotaAdmission


def seed_quota(path: Path, models, *, remaining=1000):
    now = datetime.now(timezone.utc)
    # Stable reset window allows refresh/in-flight accounting to be exercised.
    reset = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    rows = [{"account": "fixture-free-account", "provider": model.split("/", 1)[0],
             "model": model, "scope": "fixture-account-requests",
             "free_account_verified": True, "evidence_status": "confirmed", "horizon": "H0",
             "observed_at": now.isoformat(), "reset_at": reset.isoformat(),
             "remaining": remaining, "remaining_tokens": 1000000}
            for model in sorted(set(models))]
    path.write_text(json.dumps({"schema_version": 1, "records": rows}), encoding="utf-8")
    return QuotaAdmission(records_path=path, db_path=path.with_suffix(".sqlite"))


class SeededQuotaClient(TestClient):
    """Install explicit fake quota for each requested test model, never skip reserve."""
    def __init__(self, module, directory):
        self.quota_path = Path(directory) / "quota.json"
        self.models = set()
        module.admission = seed_quota(self.quota_path, [])
        super().__init__(module.app)

    def request(self, method, url, **kwargs):
        body = kwargs.get("json")
        if method.upper() == "POST" and str(url).endswith("/v1/chat/completions") and isinstance(body, dict):
            model = body.get("model")
            if isinstance(model, str):
                self.models.add(model)
                seed_quota(self.quota_path, self.models)
        return super().request(method, url, **kwargs)
