"""Leaderboard — persistent per-(role, task, provider, model) scoring."""
from __future__ import annotations
import json, os, time
from pathlib import Path
from typing import Any

_DEFAULT = Path.home() / ".deepcli" / "leaderboard.json"


class Leaderboard:
    def __init__(self, path: str | os.PathLike | None = None):
        self.path = Path(path) if path else _DEFAULT
        self.data: dict[str, Any] = {}
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text())
            except Exception:
                self.data = {}

    def _key(self, role: str, task: str, provider: str, model: str) -> str:
        return f"{role}::{task}::{provider}::{model}"

    def record(self, role: str, task: str, provider: str, model: str,
               score: float, cost: float = 0.0, latency_ms: int = 0,
               ok: bool = True) -> None:
        k = self._key(role, task, provider, model)
        e = self.data.setdefault(k, {
            "role": role, "task": task, "provider": provider, "model": model,
            "runs": 0, "ok": 0, "fail": 0, "scores": [], "cost": 0.0,
            "latency_ms_sum": 0, "first_seen": time.time(), "last_seen": time.time(),
        })
        e["runs"] += 1
        e["ok" if ok else "fail"] += 1
        e["scores"].append(round(float(score), 4))
        e["scores"] = e["scores"][-200:]
        e["cost"] += float(cost)
        e["latency_ms_sum"] += int(latency_ms)
        e["last_seen"] = time.time()
        self._save()

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2))

    def top(self, role: str, task: str, k: int = 5) -> list[dict]:
        cands = []
        for key, e in self.data.items():
            if e["role"] != role or e["task"] != task:
                continue
            n = e["runs"] or 1
            avg = sum(e["scores"]) / len(e["scores"]) if e["scores"] else 0.0
            avg_lat = e["latency_ms_sum"] / n
            score = avg * (e["ok"] / n)
            cands.append({
                "provider": e["provider"], "model": e["model"],
                "avg_score": round(avg, 4), "ok_rate": round(e["ok"] / n, 4),
                "composite": round(score, 4), "cost_total": round(e["cost"], 4),
                "avg_latency_ms": round(avg_lat, 1), "runs": e["runs"],
            })
        cands.sort(key=lambda x: (-x["composite"], x["cost_total"]))
        return cands[:k]

    def worst(self, role: str, task: str, k: int = 5) -> list[dict]:
        return list(reversed(self.top(role, task, k=len(self.data))))
