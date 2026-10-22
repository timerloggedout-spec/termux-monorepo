#!/usr/bin/env python3
"""MSM-005 — trading cards, observational bets, and optional paper accounting."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

try:
    from .accounting import EventStore, MAX_UNITS, _Already, append, digest, ensure_durable, replay
except ImportError:  # direct script execution
    from accounting import EventStore, MAX_UNITS, _Already, append, digest, ensure_durable, replay

ActorClass = Literal["itself", "others", "job"]
ShareLevel = Literal["private", "role", "public"]
TERMINAL_REASONS = {"cancelled", "expired", "void", "rejected", "unresolved", "tie"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _owner(value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("owner must be a non-empty string")


def _units(value: Any) -> None:
    if type(value) is not int or not 0 < value <= MAX_UNITS:
        raise ValueError("units must be a positive integer <= 2**63-1")


def _provenance(value: Any) -> None:
    if (not isinstance(value, dict) or set(value) != {"issuer", "source", "reference"}
            or any(not isinstance(value[k], str) or not value[k].strip() for k in value)):
        raise ValueError("provenance requires non-empty issuer, source, and reference strings")


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
        return hashlib.sha256(f"{self.role}|{self.owner}|{self.artifact_path or ''}|{self.opt_script_path or ''}".encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["card_id"] = self.card_id()
        result["metrics"] = {"elo": self.elo, "n": self.n, "last_sha": self.last_sha, "confidence": self.confidence}
        return result

    def offer_trade(self, to_owner: str, *, sha: str | None = None) -> None:
        self.trade_log.append({"at": _now(), "from": self.owner, "to": to_owner, "action": "offer", "sha": sha})


@dataclass
class BetEntry:
    actor_class: ActorClass
    subject_kind: str
    subject_id: str
    actor_id: str = "observer"
    role: str | None = None
    prediction: str = "success"
    unit_kind: str = "observational"
    units: float = 1.0
    card_id: str | None = None
    head_sha: str | None = None
    status: str = "open"
    created_at: str | None = None

    def entry_id(self) -> str:
        return hashlib.sha256(f"{self.actor_class}|{self.subject_kind}|{self.subject_id}|{self.prediction}".encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {"entry_id": self.entry_id(), "actor_class": self.actor_class, "actor_id": self.actor_id,
                "subject": {"kind": self.subject_kind, "id": self.subject_id, "role": self.role},
                "stake": {"units": self.units, "unit_kind": self.unit_kind}, "prediction": self.prediction,
                "outcome": None, "card_id": self.card_id, "created_at": self.created_at or _now(),
                "status": self.status, "head_sha": self.head_sha}


class MarketGraph:
    def __init__(self, event_path=None) -> None:
        self.event_path = event_path
        self._mutex = threading.RLock()
        self._store = EventStore(event_path) if event_path is not None else None
        self.cards: dict[str, dict[str, Any]] = {}
        self.bets: list[dict[str, Any]] = []
        self.edges: list[dict[str, str]] = []
        self._events: list[dict[str, Any]] = []
        self._accounts: dict[str, int] = {}
        self._reservations: dict[str, dict[str, Any]] = {}
        self._ids: dict[str, dict[str, Any]] = {}
        if self._store:
            with self._store.locked():
                self._refresh()

    @staticmethod
    def _empty():
        return {"cards": {}, "bets": [], "edges": [], "accounts": {}, "reservations": {}, "ids": {}}

    def _reduce(self, events):
        state = self._empty()
        seen = set()
        for index, event in enumerate(events, 1):
            self._validate_envelope(event, index)
            if event["event_id"] in seen:
                raise ValueError("duplicate event id in stream")
            seen.add(event["event_id"])
            self._transition(state, event)
            payload = event["payload"]
            correlation = (payload["reservation"]["reservation_id"] if event["type"] == "reserve"
                           else payload["reservation_id"] if event["type"] in ("settle", "release")
                           else event["event_id"])
            if event["correlation_id"] != correlation:
                raise ValueError("event correlation does not match its market operation")
            state["ids"][event["event_id"]] = copy.deepcopy(event)
        return state

    @staticmethod
    def _validate_envelope(event, index=None):
        where = f" at event {index}" if index else ""
        expected = {"event_id", "type", "payload", "timestamp", "correlation_id"}
        if not isinstance(event, dict) or set(event) != expected | {"version", "seq"}:
            raise ValueError("invalid event fields" + where)
        if type(event["version"]) is not int or event["version"] != 1:
            raise ValueError("unsupported event version" + where)
        if type(event["seq"]) is not int or (index is not None and event["seq"] != index):
            raise ValueError("invalid event sequence" + where)
        for key in ("event_id", "type", "timestamp", "correlation_id"):
            if not isinstance(event[key], str) or not event[key].strip():
                raise ValueError(f"invalid {key}" + where)
        try:
            dt = datetime.fromisoformat(event["timestamp"])
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid timestamp" + where) from exc
        if dt.tzinfo is None or not isinstance(event["payload"], dict):
            raise ValueError("invalid timestamp or payload" + where)

    @staticmethod
    def _keys(payload, keys):
        if not isinstance(payload, dict) or set(payload) != set(keys):
            raise ValueError("invalid event payload fields")

    @staticmethod
    def _bet_valid(bet):
        keys = {"entry_id", "actor_class", "actor_id", "subject", "stake", "prediction", "outcome", "card_id", "created_at", "status", "head_sha"}
        if not isinstance(bet, dict) or set(bet) != keys:
            raise ValueError("invalid bet fields")
        if bet["actor_class"] not in ("itself", "others", "job"):
            raise ValueError("invalid bet actor")
        _owner(bet["actor_id"])
        for group, required in ((bet["subject"], {"kind", "id", "role"}), (bet["stake"], {"units", "unit_kind"})):
            if not isinstance(group, dict) or set(group) != required:
                raise ValueError("invalid bet structure")
        for value in (bet["subject"]["kind"], bet["subject"]["id"], bet["prediction"], bet["stake"]["unit_kind"], bet["status"], bet["created_at"]):
            if not isinstance(value, str) or not value:
                raise ValueError("invalid bet string field")
        if bet["subject"]["kind"] not in ("model", "engine", "job", "card") or bet["status"] != "open" or bet["outcome"] is not None:
            raise ValueError("new bet must be open with a supported subject and no outcome")
        expected_id = hashlib.sha256(f'{bet["actor_class"]}|{bet["subject"]["kind"]}|{bet["subject"]["id"]}|{bet["prediction"]}'.encode()).hexdigest()[:16]
        if bet["entry_id"] != expected_id:
            raise ValueError("bet entry_id does not match its market identity")
        try:
            created = datetime.fromisoformat(bet["created_at"])
        except ValueError as exc:
            raise ValueError("invalid bet creation timestamp") from exc
        if created.tzinfo is None:
            raise ValueError("bet creation timestamp needs a timezone")
        if bet["subject"]["role"] is not None and not isinstance(bet["subject"]["role"], str):
            raise ValueError("invalid bet role")
        if bet["card_id"] is not None and not isinstance(bet["card_id"], str):
            raise ValueError("invalid bet card")
        if bet["head_sha"] is not None and not isinstance(bet["head_sha"], str):
            raise ValueError("invalid bet head_sha")
        amount = bet["stake"]["units"]
        if bet["stake"]["unit_kind"] == "paper_point":
            _units(amount)
        elif bet["stake"]["unit_kind"] in ("observational", "soft_quota_token"):
            try:
                valid = type(amount) in (int, float) and math.isfinite(amount) and amount > 0
            except OverflowError:
                valid = False
            if not valid:
                raise ValueError("invalid observational stake")
        else:
            raise ValueError("invalid stake unit")

    def _transition(self, s, event):
        typ, p = event["type"], event["payload"]
        if typ == "card":
            self._keys(p, {"card"}); card = p["card"]
            expected = {"role", "owner", "share", "artifact_path", "opt_script_path", "elo", "n", "last_sha", "confidence", "trade_log", "card_id", "metrics"}
            self._keys(card, expected)
            _owner(card["owner"])
            if not isinstance(card["role"], str) or not card["role"].strip() or card["share"] not in ("private", "role", "public"):
                raise ValueError("invalid card role or sharing level")
            for key in ("artifact_path", "opt_script_path", "last_sha"):
                if card[key] is not None and not isinstance(card[key], str):
                    raise ValueError("invalid card reference")
            expected_id = hashlib.sha256(f'{card["role"]}|{card["owner"]}|{card["artifact_path"] or ""}|{card["opt_script_path"] or ""}'.encode()).hexdigest()[:16]
            if card["card_id"] != expected_id:
                raise ValueError("card_id does not match its market identity")
            if type(card["n"]) is not int or card["n"] < 0 or not isinstance(card["trade_log"], list) or any(not isinstance(t, dict) for t in card["trade_log"]):
                raise ValueError("invalid card metrics or trade log")
            for key in ("elo", "confidence"):
                try:
                    valid = type(card[key]) in (int, float) and math.isfinite(card[key])
                except OverflowError:
                    valid = False
                if not valid:
                    raise ValueError("invalid card metric")
            if card["metrics"] != {key: card[key] for key in ("elo", "n", "last_sha", "confidence")}:
                raise ValueError("inconsistent card metrics")
            if card["card_id"] in s["cards"]: raise ValueError("duplicate card")
            s["cards"][card["card_id"]] = copy.deepcopy(card)
            s["edges"].append({"type": "owns", "from": card["owner"], "to": card["card_id"]})
        elif typ == "bet":
            self._keys(p, {"bet"}); bet = p["bet"]; self._bet_valid(bet)
            if bet["stake"]["unit_kind"] == "paper_point":
                raise ValueError("paper bets require a reservation event")
            key = (bet["actor_id"], bet["entry_id"])
            if any((b["actor_id"], b["entry_id"]) == key for b in s["bets"]): raise ValueError("duplicate bet operation")
            if bet["card_id"] is not None and bet["card_id"] not in s["cards"]: raise ValueError("unknown bet card")
            s["bets"].append(copy.deepcopy(bet))
            s["edges"].append({"type": "stakes", "from": bet["actor_class"], "to": f'{bet["subject"]["kind"]}:{bet["subject"]["id"]}'})
        elif typ == "open_account":
            self._keys(p, {"owner", "provenance"}); _owner(p["owner"]); _provenance(p["provenance"])
            if p["owner"] in s["accounts"]: raise ValueError("account already open")
            s["accounts"][p["owner"]] = 0
        elif typ == "issue":
            self._keys(p, {"owner", "units", "provenance"}); _owner(p["owner"]); _units(p["units"]); _provenance(p["provenance"])
            if p["owner"] not in s["accounts"]: raise ValueError("account is not open")
            if s["accounts"][p["owner"]] + p["units"] > MAX_UNITS: raise ValueError("account balance overflow")
            s["accounts"][p["owner"]] += p["units"]
        elif typ == "reserve":
            if not isinstance(p, dict) or "reservation" not in p: raise ValueError("invalid reservation payload")
            r = p["reservation"]
            if not isinstance(r, dict): raise ValueError("invalid reservation")
            kind = r.get("kind")
            if kind not in ("bet", "offer"):
                raise ValueError("unknown reservation kind")
            self._keys(r, {"reservation_id", "owner", "units", "status", "kind", "entry_id"} if kind == "bet" else {"reservation_id", "owner", "units", "status", "kind", "card_id", "to_owner"} if kind == "offer" else set())
            _owner(r["owner"]); _units(r["units"])
            if not isinstance(r["reservation_id"], str) or not r["reservation_id"] or r["status"] != "reserved": raise ValueError("invalid reservation identity or status")
            if r["reservation_id"] in s["reservations"]: raise ValueError("duplicate reservation")
            if r["owner"] not in s["accounts"]: raise ValueError("reservation owner account is not open")
            active = sum(x["units"] for x in s["reservations"].values() if x["owner"] == r["owner"] and x["status"] == "reserved")
            if s["accounts"][r["owner"]] - active < r["units"]: raise ValueError("insufficient available balance")
            if kind == "bet":
                self._keys(p, {"reservation", "bet"}); bet = p["bet"]; self._bet_valid(bet)
                if bet["stake"]["unit_kind"] != "paper_point" or bet["stake"]["units"] != r["units"] or bet["actor_id"] != r["owner"] or bet["entry_id"] != r["entry_id"]: raise ValueError("bet does not match reservation")
                key = (bet["actor_id"], bet["entry_id"])
                if any((b["actor_id"], b["entry_id"]) == key for b in s["bets"]): raise ValueError("duplicate bet operation")
                if bet["card_id"] is not None and bet["card_id"] not in s["cards"]: raise ValueError("unknown bet card")
                s["bets"].append(copy.deepcopy(bet)); s["edges"].append({"type": "stakes", "from": bet["actor_class"], "to": f'{bet["subject"]["kind"]}:{bet["subject"]["id"]}'})
            else:
                self._keys(p, {"reservation", "card_id", "payer", "to_owner", "units"})
                _owner(r["card_id"])
                _units(p["units"])
                if p["card_id"] != r["card_id"] or p["payer"] != r["owner"] or p["to_owner"] != r["to_owner"] or p["units"] != r["units"]: raise ValueError("offer does not match reservation")
                _owner(r["to_owner"])
                if r["to_owner"] not in s["accounts"] or r["card_id"] not in s["cards"] or s["cards"][r["card_id"]]["owner"] != r["to_owner"]: raise ValueError("invalid offer card owner")
                if any(x.get("kind") == "offer" and x.get("card_id") == r["card_id"] and x["owner"] == r["owner"] and x["to_owner"] == r["to_owner"] for x in s["reservations"].values()): raise ValueError("offer operation already used")
                s["edges"].append({"type": "offers", "from": r["owner"], "to": r["card_id"]})
            s["reservations"][r["reservation_id"]] = copy.deepcopy(r)
        elif typ in ("settle", "release"):
            self._keys(p, {"reservation_id", "recipient"} if typ == "settle" else {"reservation_id", "reason"})
            rid = p["reservation_id"]
            if not isinstance(rid, str) or rid not in s["reservations"]: raise ValueError("unknown reservation")
            r = s["reservations"][rid]
            if r["status"] != "reserved": raise ValueError("terminal reservation")
            if typ == "settle":
                recipient = p["recipient"]; _owner(recipient)
                if r["kind"] == "offer" and recipient != r["to_owner"]: raise ValueError("offer must settle to its card owner")
                if recipient not in s["accounts"]: raise ValueError("unknown recipient")
                if recipient != r["owner"] and s["accounts"][recipient] + r["units"] > MAX_UNITS: raise ValueError("account balance overflow")
                if recipient != r["owner"]: s["accounts"][r["owner"]] -= r["units"]; s["accounts"][recipient] += r["units"]
                r["recipient"] = recipient; r["status"] = "settled"
                for bet in s["bets"]:
                    if bet["entry_id"] == r.get("entry_id") and bet["actor_id"] == r["owner"]: bet["status"] = "settled"
            else:
                if not isinstance(p["reason"], str) or p["reason"] not in TERMINAL_REASONS: raise ValueError("invalid release reason")
                r["status"] = "released"; r["reason"] = p["reason"]
                for bet in s["bets"]:
                    if bet["entry_id"] == r.get("entry_id") and bet["actor_id"] == r["owner"]: bet["status"] = "released"
        else:
            raise ValueError(f"unknown event type: {typ}")

    def _install(self, events, state):
        self._events = copy.deepcopy(events)
        self.cards, self.bets, self.edges = state["cards"], state["bets"], state["edges"]
        self._accounts, self._reservations, self._ids = state["accounts"], state["reservations"], state["ids"]

    def _refresh(self):
        events = replay(self._store.path)
        state = self._reduce(events)
        self._install(events, state)

    def _mutate(self, typ, event_id, payload):
        with self._mutex:
            return self._mutate_locked(typ, event_id, payload)

    def _mutate_locked(self, typ, event_id, payload):
        if not isinstance(event_id, str) or not event_id.strip(): raise ValueError("event_id must be non-empty")
        candidate = {"event_id": event_id, "type": typ, "payload": copy.deepcopy(payload), "timestamp": _now(), "correlation_id": payload.get("reservation", {}).get("reservation_id") or payload.get("reservation_id") or event_id}
        if self._store:
            with self._store.locked():
                events = replay(self._store.path)
                state = self._reduce(events)
                prior = state["ids"].get(event_id)
                if prior:
                    if prior["type"] != typ or self._intent(prior["payload"]) != self._intent(payload): raise ValueError("event_id already used with different intent")
                    ensure_durable(self._store.path)
                    self._install(events, state); return prior
                trial = copy.deepcopy(events) + [dict(candidate, version=1, seq=len(events) + 1)]
                new_state = self._reduce(trial)  # validate the complete transition before durable append
                try: append(self._store.path, events, candidate)
                except _Already as existing:
                    self._refresh(); return existing.event
                self._install(events, new_state)
        else:
            prior = self._ids.get(event_id)
            if prior:
                if prior["type"] != typ or self._intent(prior["payload"]) != self._intent(payload): raise ValueError("event_id already used with different intent")
                return prior
            framed = dict(candidate, version=1, seq=len(self._events) + 1)
            self._validate_envelope(framed, len(self._events) + 1)
            # Ephemeral mode preserves legacy live card/observational views.
            # Durable mode above always reconstructs from the single event stream.
            state = copy.deepcopy({"cards": self.cards, "bets": self.bets, "edges": self.edges,
                                   "accounts": self._accounts, "reservations": self._reservations,
                                   "ids": self._ids})
            self._transition(state, framed)
            state["ids"][event_id] = copy.deepcopy(framed)
            events = copy.deepcopy(self._events) + [framed]
            self._install(events, state)
        return candidate

    @staticmethod
    def _intent(payload):
        normalized = copy.deepcopy(payload)
        bet = normalized.get("bet") if isinstance(normalized, dict) else None
        if isinstance(bet, dict):
            bet.pop("created_at", None)
        return normalized

    def add_card(self, card: TradingCard) -> dict[str, Any]:
        data = card.to_dict(); self._mutate("card", "card:" + data["card_id"], {"card": data}); return data

    def place_bet(self, bet: BetEntry) -> dict[str, Any]:
        data = bet.to_dict()
        if data["stake"]["unit_kind"] not in ("observational", "soft_quota_token"): raise ValueError("invalid stake unit")
        self._bet_valid(data)
        self._mutate("bet", "bet:" + data["actor_id"] + ":" + data["entry_id"], {"bet": data})
        return data

    def open_account(self, owner, *, event_id, provenance):
        _owner(owner); _provenance(provenance); self._mutate("open_account", event_id, {"owner": owner, "provenance": copy.deepcopy(provenance)}); return {"owner": owner, "balance": 0}

    def issue_points(self, owner, units, *, event_id, provenance):
        _owner(owner); _units(units); _provenance(provenance)
        self._mutate("issue", event_id, {"owner": owner, "units": units, "provenance": copy.deepcopy(provenance)})
        return {"owner": owner, "units": units, "provenance": copy.deepcopy(provenance)}

    def reserve_bet(self, bet: BetEntry, *, event_id, reservation_id):
        data = bet.to_dict()
        if data["stake"]["unit_kind"] != "paper_point": raise ValueError("reserve_bet requires paper_point")
        _units(data["stake"]["units"]); _owner(data["actor_id"])
        reservation = {"reservation_id": reservation_id, "owner": data["actor_id"], "units": data["stake"]["units"], "status": "reserved", "entry_id": data["entry_id"], "kind": "bet"}
        self._mutate("reserve", event_id, {"reservation": reservation, "bet": data})
        return copy.deepcopy(self._reservations[reservation_id])

    def reserve_offer(self, card_id, payer, to_owner, units, *, event_id, reservation_id):
        _owner(payer); _owner(to_owner); _units(units)
        reservation = {"reservation_id": reservation_id, "owner": payer, "units": units, "status": "reserved", "card_id": card_id, "to_owner": to_owner, "kind": "offer"}
        payload = {"reservation": reservation, "card_id": card_id, "payer": payer, "to_owner": to_owner, "units": units}
        self._mutate("reserve", event_id, payload)
        return copy.deepcopy(self._reservations[reservation_id])

    def settle(self, reservation_id, *, event_id, recipient):
        _owner(recipient); self._mutate("settle", event_id, {"reservation_id": reservation_id, "recipient": recipient})
        return copy.deepcopy(self._reservations[reservation_id])

    def release(self, reservation_id, *, event_id, reason="cancelled"):
        if not isinstance(reason, str) or reason not in TERMINAL_REASONS: raise ValueError("invalid release reason")
        self._mutate("release", event_id, {"reservation_id": reservation_id, "reason": reason})
        return copy.deepcopy(self._reservations[reservation_id])

    def _refresh_if_needed(self):
        with self._mutex:
            if self._store:
                with self._store.locked():
                    self._refresh()

    def accounting_snapshot(self):
        with self._mutex:
            if self._store:
                with self._store.locked():
                    self._refresh()
                    return self._accounting_view()
            return self._accounting_view()

    def _accounting_view(self):
        reserved = {owner: 0 for owner in self._accounts}
        for reservation in self._reservations.values():
            if reservation["status"] == "reserved": reserved[reservation["owner"]] += reservation["units"]
        accounts = [{"owner": owner, "balance": balance, "reserved": reserved[owner], "available": balance - reserved[owner]} for owner, balance in sorted(self._accounts.items())]
        reservations = [copy.deepcopy(r) for _, r in sorted(self._reservations.items())]
        return {"schema_version": 1, "asset": "paper_point", "event_count": len(self._events), "source_digest": digest(self._events), "accounts": accounts, "reservations": reservations, "events": copy.deepcopy(self._events)}

    def snapshot(self) -> dict[str, Any]:
        with self._mutex:
            if self._store:
                with self._store.locked():
                    self._refresh()
                    return self._snapshot_view()
            return self._snapshot_view()

    def _snapshot_view(self):
        result = {"schema_version": 1, "policy": "observational_until_promote", "cards": copy.deepcopy(list(self.cards.values())), "bets": copy.deepcopy(self.bets), "edges": copy.deepcopy(self.edges), "note": "Settlement does not bypass dual-gate"}
        if any(e["type"] in ("open_account", "issue", "reserve", "settle", "release") for e in self._events):
            result["paper_accounting"] = self._accounting_view()
        return result


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--demo", action="store_true"); args = parser.parse_args(); graph = MarketGraph()
    if args.demo:
        card = TradingCard(role="triage", owner="ox-alpha-card", opt_script_path="scripts/model_selection_market/dspy_doe.py"); graph.add_card(card)
        graph.place_bet(BetEntry(actor_class="itself", subject_kind="model", subject_id="stealth/ox-alpha", role="triage", card_id=card.card_id()))
    print(json.dumps(graph.snapshot(), indent=2, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
