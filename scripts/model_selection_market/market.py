#!/usr/bin/env python3
"""MSM-005 — trading cards, observational bets, total graph stub."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

ActorClass = Literal["itself", "others", "job"]
ShareLevel = Literal["private", "role", "public"]


@dataclass
class TradingCard:
    role: str
    owner: str
    share: ShareLevel = "role"
    artifact_path: str | None = None
    opt_script_path: str | None = None
    elo: float = 1200.0
    n: int = 0
    last_sha: str | None = None
    confidence: float = 0.0
    trade_log: list[dict[str, Any]] = field(default_factory=list)

    def card_id(self) -> str:
        raw = f"{self.role}|{self.owner}|{self.artifact_path or ''}|{self.opt_script_path or ''}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["card_id"] = self.card_id()
        d["metrics"] = {
            "elo": self.elo,
            "n": self.n,
            "last_sha": self.last_sha,
            "confidence": self.confidence,
        }
        return d

    def offer_trade(self, to_owner: str, *, sha: str | None = None) -> None:
        self.trade_log.append(
            {
                "at": datetime.now(timezone.utc).isoformat(),
                "from": self.owner,
                "to": to_owner,
                "action": "offer",
                "sha": sha,
            }
        )


@dataclass
class BetEntry:
    actor_class: ActorClass
    subject_kind: str  # model|engine|job|card
    subject_id: str
    actor_id: str = "observer"
    role: str | None = None
    prediction: str = "success"
    unit_kind: str = "observational"
    units: float = 1.0
    card_id: str | None = None
    head_sha: str | None = None
    status: str = "open"

    def entry_id(self) -> str:
        raw = f"{self.actor_class}|{self.subject_kind}|{self.subject_id}|{self.prediction}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id(),
            "actor_class": self.actor_class,
            "actor_id": self.actor_id,
            "subject": {"kind": self.subject_kind, "id": self.subject_id, "role": self.role},
            "stake": {"units": self.units, "unit_kind": self.unit_kind},
            "prediction": self.prediction,
            "outcome": None,
            "card_id": self.card_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": self.status,
            "head_sha": self.head_sha,
        }


class MarketGraph:
    def __init__(self) -> None:
        self.cards: dict[str, dict[str, Any]] = {}
        self.bets: list[dict[str, Any]] = []
        self.edges: list[dict[str, str]] = []

    def add_card(self, card: TradingCard) -> dict[str, Any]:
        d = card.to_dict()
        self.cards[d["card_id"]] = d
        self.edges.append({"type": "owns", "from": card.owner, "to": d["card_id"]})
        return d

    def place_bet(self, bet: BetEntry) -> dict[str, Any]:
        if bet.unit_kind not in ("observational", "soft_quota_token"):
            raise ValueError("invalid stake unit")
        d = bet.to_dict()
        self.bets.append(d)
        self.edges.append(
            {"type": "stakes", "from": bet.actor_class, "to": f"{bet.subject_kind}:{bet.subject_id}"}
        )
        return d

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "policy": "observational_until_promote",
            "cards": list(self.cards.values()),
            "bets": self.bets,
            "edges": self.edges,
            "note": "Settlement does not bypass dual-gate",
        }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--demo", action="store_true")
    args = p.parse_args()
    g = MarketGraph()
    if args.demo:
        c = TradingCard(role="triage", owner="ox-alpha-card", opt_script_path="scripts/model_selection_market/dspy_doe.py")
        g.add_card(c)
        g.place_bet(
            BetEntry(
                actor_class="itself",
                subject_kind="model",
                subject_id="stealth/ox-alpha",
                role="triage",
                card_id=c.card_id(),
            )
        )
    print(json.dumps(g.snapshot(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
