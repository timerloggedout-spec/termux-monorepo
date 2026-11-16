"""Session identity for this extract. Not a pulse PR."""
from __future__ import annotations

from dataclasses import dataclass

from ml.pipelines.command_center.constants import AGENT, MASTER_PRODUCT_SHA, VERSION

SESSION_ID = "20260926-2115Z-ml-command-center"


@dataclass(frozen=True)
class Session:
    session_id: str
    agent: str
    version: str
    product_sha: str
    intent: str = "upgrade keep-alive DAG + operator board; dual-gate this SHA"


def current() -> Session:
    return Session(
        session_id=SESSION_ID,
        agent=AGENT,
        version=VERSION,
        product_sha=MASTER_PRODUCT_SHA,
    )
