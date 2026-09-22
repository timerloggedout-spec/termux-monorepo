"""Extensible System One adapter contracts.

Categories are transport-neutral: routing, security, agent, code, ops, etc. can
register engines without granting them execution authority. Jev uses the
TypeSafe HTTP contract only when TYPESAFE_API_KEY is explicitly configured.
"""
from __future__ import annotations
import json, os
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.request import Request, urlopen

@dataclass(frozen=True)
class DecisionRequest:
    state: dict[str, Any]
    questions: dict[str, Any]
    experiment_id: str
    lane_id: str
    category: str = "general"

@dataclass(frozen=True)
class DecisionResponse:
    engine: str
    status: str
    answers: dict[str, Any]
    confidence: float | None
    metadata: dict[str, Any]

class SystemOneAdapter(Protocol):
    engine: str
    categories: tuple[str, ...]
    def evaluate(self, request: DecisionRequest) -> DecisionResponse: ...

class UnavailableAdapter:
    engine="jev"
    categories=("routing","security","agent","code","ops","general")
    def evaluate(self, request: DecisionRequest) -> DecisionResponse:
        return DecisionResponse(self.engine,"UNAVAILABLE",{},None,{"failure_class":"ENGINE_UNAVAILABLE"})

class TypeSafeJevAdapter:
    """Small stdlib-only client for TypeSafe's POST /v1/systemone API."""
    engine="jev"
    categories=("routing","security","agent","code","ops","general")
    def __init__(self, api_key: str|None=None, base_url: str|None=None, model: str|None=None, timeout: float=30.0):
        self.api_key=api_key or os.getenv("TYPESAFE_API_KEY")
        self.base_url=(base_url or os.getenv("TYPESAFE_BASE_URL","https://api.typesafe.ai")).rstrip("/")
        self.model=model or os.getenv("TYPESAFE_MODEL","jev-latest")
        self.timeout=timeout
    @property
    def configured(self): return bool(self.api_key)
    def evaluate(self, request: DecisionRequest) -> DecisionResponse:
        if not self.api_key:
            return UnavailableAdapter().evaluate(request)
        payload={"model":self.model,"state":request.state,"questions":request.questions}
        req=Request(self.base_url+"/v1/systemone",data=json.dumps(payload).encode(),method="POST",
                    headers={"Authorization":"Bearer "+self.api_key,"Content-Type":"application/json"})
        try:
            with urlopen(req,timeout=self.timeout) as resp:
                body=json.loads(resp.read().decode())
            answers=body.get("answers",{})
            confidences=[float(v["confidence"]) for v in answers.values() if isinstance(v,dict) and v.get("confidence") is not None]
            return DecisionResponse(self.engine,"OK",answers,(sum(confidences)/len(confidences) if confidences else None),
                                    {"model":body.get("model",self.model),"usage":body.get("usage",{})})
        except Exception as exc:
            return DecisionResponse(self.engine,"FAILED",{},None,{"failure_class":"ENGINE_ERROR","error":type(exc).__name__})

def langchain_boundary() -> dict[str,str]:
    return {"contract":"DecisionRequest -> DecisionResponse","execution":"adapter only","authority":"no provider command, branch write, merge, or secret access","installation":"optional integration dependency"}

def engine_catalog() -> dict[str,dict[str,Any]]:
    return {
      "laya":{"kind":"local","categories":["routing","security","agent","code","ops","general"],"authority":"decision-only"},
      "jev":{"kind":"http","categories":["routing","security","agent","code","ops","general"],"authority":"decision-only"},
    }
