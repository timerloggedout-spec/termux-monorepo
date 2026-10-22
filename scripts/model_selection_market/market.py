#!/usr/bin/env python3
"""MSM-005 — trading cards, observational bets, total graph stub."""

from __future__ import annotations

import hashlib
import json
import math
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
        raw = f"{self.actor_class}|{self.actor_id}|{self.subject_kind}|{self.subject_id}|{self.prediction}"
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
    def __init__(self, journal: str | None = None) -> None:
        self.cards: dict[str, dict[str, Any]] = {}
        self.bets: list[dict[str, Any]] = []
        self.edges: list[dict[str, str]] = []
        self._accounting = None
        if journal is not None:
            from .accounting import PaperMarket
            self._accounting = PaperMarket(journal)
            self._load_market(self._accounting.snapshot())

    def _load_market(self, accounting: dict[str, Any]) -> None:
        """Refresh the in-memory projection from one authoritative journal snapshot."""
        projected = self.snapshot_from_accounting(accounting)
        self.cards = {row['card_id']: row for row in projected['cards']}
        self.bets, self.edges = projected['bets'], projected['edges']

    @staticmethod
    def snapshot_from_accounting(accounting: dict[str, Any]) -> dict[str, Any]:
        """Build a detached graph snapshot from a single already-read journal state."""
        import copy
        cards: dict[str, dict[str, Any]] = {}
        bets: list[dict[str, Any]] = []
        edges: list[dict[str, str]] = []
        offers: list[dict[str, Any]] = []
        for event in accounting.get('market', []):
            kind, record = event.get('kind'), event.get('record')
            if kind == 'card':
                row = copy.deepcopy(record)
                cards[row['card_id']] = row
                edges.append({'type': 'owns', 'from': row['owner'], 'to': row['card_id']})
            elif kind == 'bet':
                row = copy.deepcopy(record)
                bets.append(row)
                subject = row['subject']
                edges.append({'type': 'stakes', 'from': row['actor_class'], 'to': f"{subject['kind']}:{subject['id']}"})
            elif kind == 'offer' and event.get('offer'):
                offers.append((record['card_id'], event['offer']))
        for card_id, offer in offers:
            if card_id in cards:
                cards[card_id].setdefault('trade_log', []).append(copy.deepcopy(offer))
        return {"schema_version": 1, "policy": "observational_until_promote",
                "cards": list(cards.values()), "bets": bets, "edges": edges,
                "accounting": copy.deepcopy(accounting),
                "note": "Settlement does not bypass dual-gate"}

    def issue_paper_points(self, key, owner, amount, provenance):
        if self._accounting is None: raise ValueError("journal is required")
        return self._accounting.issue(key, owner, amount, provenance)

    def reserve_bet(self, key, reservation, owner, amount, entry_id):
        persisted = self._accounting.snapshot()['market'] if self._accounting is not None else []
        rows = [x['record'] for x in persisted if x.get('kind') == 'bet'] if self._accounting is not None else self.bets
        row = next((b for b in rows if b.get("entry_id") == entry_id), None)
        if row is None: raise ValueError("bet reference must identify an existing MarketGraph bet")
        if row.get("actor_id") != owner: raise ValueError("bet owner must match market actor")
        if self._accounting is None: raise ValueError("journal is required")
        return self._accounting.reserve(key, reservation, owner, amount, "bet:" + entry_id)

    def offer_trade(self, key, card_id, to_owner, *, sha=None, at=None):
        from datetime import datetime, timezone
        if self._accounting is None: raise ValueError("journal is required")
        snap = self._accounting.snapshot()
        card=next((x['record'] for x in snap['market'] if x.get('kind')=='card' and x['record'].get('card_id')==card_id),None)
        if card is None: raise ValueError("unknown card")
        prior = next((e for e in snap['events'] if e.get('key') == 'market:offer:' + key), None)
        if prior:
            offer = prior['record']['offer']
            if (prior['record']['record'].get('card_id'), offer.get('from'), offer.get('to'), offer.get('sha')) != (card_id, card['owner'], to_owner, sha):
                from .accounting import AccountingError
                raise AccountingError('idempotency key conflict')
            return offer
        offer={'at':at or datetime.now(timezone.utc).isoformat(),'from':card['owner'],'to':to_owner,'action':'offer','sha':sha}
        self._accounting.market_event('market:offer:'+key,'market_offer',record={'kind':'offer','record':{'card_id':card_id},'offer':offer})
        self._load_market(self._accounting.snapshot())
        return offer

    def reserve_offer(self, key, reservation, owner, amount, card_id, offer_at):
        card = self.cards.get(card_id)
        if self._accounting is not None:
            snap=self._accounting.snapshot(); cards=[x['record'] for x in snap['market'] if x.get('kind')=='card']
            card=next((x for x in cards if x.get('card_id')==card_id),None)
            offers=[x['offer'] for x in snap['market'] if x.get('kind')=='offer' and x.get('record',{}).get('card_id')==card_id]
        else: offers=card.get('trade_log',[]) if card else []
        if card is None or not any(t.get("action") == "offer" and t.get("at") == offer_at for t in offers):
            raise ValueError("offer reference must identify an existing card offer")
        if card.get("owner") != owner: raise ValueError("offer owner must match card owner")
        if self._accounting is None: raise ValueError("journal is required")
        return self._accounting.reserve(key, reservation, owner, amount, "offer:" + card_id + ":" + offer_at)

    def settle(self, key, reservation, recipient):
        if self._accounting is None: raise ValueError("journal is required")
        return self._accounting.settle(key, reservation, recipient)

    def release(self, key, reservation):
        if self._accounting is None: raise ValueError("journal is required")
        return self._accounting.release(key, reservation)

    def void(self, key, reservation):
        if self._accounting is None: raise ValueError("journal is required")
        return self._accounting.void(key, reservation)

    def accounting_snapshot(self):
        if self._accounting is None: return {"schema_version": 1, "accounts": {}, "events": [], "reservations": {}}
        return self._accounting.snapshot()

    def add_card(self, card: TradingCard) -> dict[str, Any]:
        d = card.to_dict()
        if self._accounting is not None:
            self._accounting.market_event('market:card:'+d['card_id'],'market_card',record={'kind':'card','record':d})
            snap = self._accounting.snapshot()
            self._load_market(snap)
            return self.cards[d['card_id']]
        self.cards[d["card_id"]] = d
        self.edges.append({"type": "owns", "from": card.owner, "to": d["card_id"]})
        return d

    def place_bet(self, bet: BetEntry) -> dict[str, Any]:
        if bet.unit_kind not in ("observational", "soft_quota_token"):
            raise ValueError("invalid stake unit")
        if isinstance(bet.units, bool) or not isinstance(bet.units, (int, float)) or not math.isfinite(bet.units) or bet.units <= 0:
            raise ValueError("stake units must be a finite positive number")
        d = bet.to_dict()
        if self._accounting is not None:
            snap = self._accounting.snapshot()
            prior = next((e['record'] for e in snap['market'] if e.get('kind') == 'bet' and e['record'].get('entry_id') == d['entry_id']), None)
            if prior is not None:
                logical = lambda row: {k:v for k,v in row.items() if k != 'created_at'}
                if logical(prior) != logical(d):
                    from .accounting import AccountingError
                    raise AccountingError('idempotency key conflict')
                self._load_market(snap)
                return prior
            self._accounting.market_event('market:bet:'+d['entry_id'],'market_bet',record={'kind':'bet','record':d})
            self._load_market(self._accounting.snapshot())
            return self.bets[-1]
        self.bets.append(d)
        self.edges.append(
            {"type": "stakes", "from": bet.actor_class, "to": f"{bet.subject_kind}:{bet.subject_id}"}
        )
        return d

    def snapshot(self) -> dict[str, Any]:
        if self._accounting is not None:
            accounting = self._accounting.snapshot()
            return self.snapshot_from_accounting(accounting)
        else:
            accounting = self.accounting_snapshot()
        import copy
        return {
            "schema_version": 1,
            "policy": "observational_until_promote",
            "cards": copy.deepcopy(list(self.cards.values())),
            "bets": copy.deepcopy(self.bets),
            "edges": copy.deepcopy(self.edges),
            "accounting": copy.deepcopy(accounting),
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
