"""Durable MSM event journal and integer paper-point accounting (CSV is a projection)."""
from __future__ import annotations
import csv, hashlib, json, os, threading, fcntl, io
from pathlib import Path
VERSION = 1
MAX = 2 ** 63 - 1
_ZERO = '0' * 64
_LOCK = threading.RLock()

class AccountingError(ValueError):
    pass

class CorruptJournal(AccountingError):
    pass

def _id(v, name):
    if not isinstance(v, str) or not v or len(v) > 256 or (v.strip() != v) or any((ord(c) < 32 or ord(c) == 127 for c in v)):
        raise AccountingError(f'{name} must be a nonempty bounded string')
    return v

def _canonical(v):
    return json.dumps(v, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def _validate_market(typ, value):
    expected = {'market_card': 'card', 'market_bet': 'bet', 'market_offer': 'offer'}[typ]
    if not isinstance(value, dict) or value.get('kind') != expected or (not isinstance(value.get('record'), dict)):
        raise AccountingError('invalid market event envelope')
    record = value['record']
    if expected == 'bet':
        for key in ('entry_id', 'actor_id', 'prediction'):
            _id(record.get(key), key)
        if record.get('actor_class') not in ('itself', 'others', 'job'):
            raise AccountingError('invalid market actor class')
        subject, stake = (record.get('subject'), record.get('stake'))
        if not isinstance(subject, dict) or subject.get('kind') not in ('model', 'engine', 'job', 'card') or (not isinstance(stake, dict)):
            raise AccountingError('invalid market subject or stake')
        _id(subject.get('id'), 'subject')
        units = stake.get('units')
        import math
        if type(units) not in (int, float) or not math.isfinite(units) or units <= 0 or (stake.get('unit_kind') not in ('observational', 'soft_quota_token')):
            raise AccountingError('invalid observational stake')
    else:
        _id(record.get('card_id'), 'card')
        if expected == 'card':
            _id(record.get('owner'), 'owner')
            _id(record.get('role'), 'role')
            if record.get('share') not in ('private', 'role', 'public'):
                raise AccountingError('invalid card share')
        else:
            offer = value.get('offer')
            if not isinstance(offer, dict) or offer.get('action') != 'offer':
                raise AccountingError('invalid market offer')
            for key in ('at', 'from', 'to'):
                _id(offer.get(key), 'offer ' + key)

class PaperMarket:

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._locked(False):
            self._replay()

    def _locked(self, exclusive=True):

        class Lock:

            def __enter__(inner):
                _LOCK.acquire()
                inner.f = self.path.with_suffix(self.path.suffix + '.lock').open('a+')
                fcntl.flock(inner.f, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
                return inner

            def __exit__(inner, *exc):
                fcntl.flock(inner.f, fcntl.LOCK_UN)
                inner.f.close()
                _LOCK.release()
        return Lock()

    @staticmethod
    def _amount(n):
        if type(n) is not int or not 0 < n <= MAX:
            raise AccountingError('amount must be positive bounded integer')

    def _replay(self):
        s = {'balances': {}, 'reserved': {}, 'events': {}, 'reservations': {}, 'rows': []}
        prev = _ZERO
        if not self.path.exists():
            return s
        try:
            with self.path.open('rb') as f:
                for num, raw in enumerate(f, 1):
                    if not raw.endswith(b'\n'):
                        raise CorruptJournal(f'torn journal tail at line {num}')
                    obj = json.loads(raw, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
                    if not isinstance(obj, dict) or not isinstance(obj.get('hash'), str):
                        raise ValueError('schema')
                    e = dict(obj)
                    digest = e.pop('hash')
                    schemas = {'issue': {'owner', 'amount', 'provenance'}, 'reserve': {'reservation', 'owner', 'amount', 'market_ref', 'expires_at'}, 'settle': {'reservation', 'recipient'}, 'release': {'reservation'}, 'void': {'reservation'}, 'expire': {'reservation'}, 'market_card': {'record'}, 'market_bet': {'record'}, 'market_offer': {'record'}}
                    if e.get('type') not in schemas or set(e) != {'version', 'key', 'type', 'prev_hash'} | schemas[e['type']] or type(e.get('version')) is not int or (e.get('version') != VERSION) or (e.get('prev_hash') != prev) or (hashlib.sha256(_canonical(e)).hexdigest() != digest):
                        raise ValueError('chain/schema')
                    _id(e['key'], 'key')
                    if e['key'] in s['events']:
                        raise ValueError('duplicate event key')
                    self._apply(s, e)
                    e['hash'] = digest
                    prev = digest
                    s['events'][e['key']] = e
                    s['rows'].append(e)
        except CorruptJournal:
            raise
        except Exception as ex:
            raise CorruptJournal('malformed or invalid journal') from ex
        return s

    @staticmethod
    def _apply(s, e):
        t = e['type']
        key = e['key']
        owner = e.get('owner')
        a = e.get('amount', 0)
        if t in ('issue', 'reserve'):
            PaperMarket._amount(a)
        if t == 'issue':
            _id(owner, 'owner')
            _id(e.get('provenance'), 'provenance')
            n = s['balances'].get(owner, 0) + a
            if n > MAX:
                raise AccountingError('balance overflow')
            s['balances'][owner] = n
        elif t == 'reserve':
            _id(owner, 'owner')
            _id(e.get('reservation'), 'reservation')
            _id(e.get('market_ref'), 'market_ref')
            expiry = e.get('expires_at')
            if expiry is not None and (type(expiry) is not int or not 0 <= expiry <= MAX):
                raise AccountingError('invalid reservation expiry')
            r = e['reservation']
            if r in s['reservations']:
                raise AccountingError('duplicate reservation')
            if s['balances'].get(owner, 0) - s['reserved'].get(owner, 0) < a:
                raise AccountingError('insufficient available paper points')
            n = s['reserved'].get(owner, 0) + a
            if n > MAX:
                raise AccountingError('reserve overflow')
            s['reserved'][owner] = n
            s['reservations'][r] = {'owner': owner, 'amount': a, 'status': 'reserved', 'market_ref': e['market_ref'], 'expires_at': e.get('expires_at')}
        elif t in ('settle', 'release', 'void', 'expire'):
            _id(e.get('reservation'), 'reservation')
            r = s['reservations'].get(e['reservation'])
            if not r or r['status'] != 'reserved':
                raise AccountingError('reservation absent or finalized')
            owner, a = (r['owner'], r['amount'])
            s['reserved'][owner] -= a
            if t == 'settle':
                recipient = _id(e.get('recipient'), 'recipient')
                if recipient != owner:
                    s['balances'][owner] -= a
                    n = s['balances'].get(recipient, 0) + a
                    if n > MAX:
                        raise AccountingError('recipient balance overflow')
                    s['balances'][recipient] = n
            r['status'] = t
        elif t in ('market_card', 'market_bet', 'market_offer'):
            _validate_market(t, e.get('record'))
            s.setdefault('market', []).append(e['record'])
        else:
            raise AccountingError('unknown event type')
        if any((type(v) != int or v < 0 or v > MAX for v in s['balances'].values())) or any((type(v) != int or v < 0 or v > MAX for v in s['reserved'].values())):
            raise AccountingError('accounting bounds violated')

    def _command(self, key, typ, **kwargs):
        _id(key, 'event key')
        with self._locked(True):
            s = self._replay()
            prior = s['events'].get(key)
            if prior:
                if prior['type'] != typ or any((prior.get(k) != v for k, v in kwargs.items())):
                    raise AccountingError('idempotency key conflict')
                return prior
            e = {'version': VERSION, 'key': key, 'type': typ, **kwargs}
            self._apply(s, e)
            prev = s['rows'][-1]['hash'] if s['rows'] else _ZERO
            e['prev_hash'] = prev
            e['hash'] = hashlib.sha256(_canonical(e)).hexdigest()
            if not self.path.exists():
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 384)
                os.close(fd)
                d = os.open(self.path.parent, os.O_RDONLY)
                os.fsync(d)
                os.close(d)
            with self.path.open('ab') as f:
                f.write(_canonical(e) + b'\n')
                f.flush()
                os.fsync(f.fileno())
            return e

    def issue(self, key, owner, amount, provenance):
        return self._command(key, 'issue', owner=owner, amount=amount, provenance=provenance)

    def reserve(self, key, reservation, owner, amount, market_ref, expires_at=None):
        if expires_at is not None and (type(expires_at) != int or not 0 <= expires_at <= MAX):
            raise AccountingError('expires_at must be bounded epoch seconds')
        return self._command(key, 'reserve', reservation=reservation, owner=owner, amount=amount, market_ref=market_ref, expires_at=expires_at)

    def settle(self, key, reservation, recipient):
        return self._command(key, 'settle', reservation=reservation, recipient=recipient)

    def release(self, key, reservation):
        return self._command(key, 'release', reservation=reservation)

    def void(self, key, reservation):
        return self._command(key, 'void', reservation=reservation)

    def expire(self, key, reservation, now):
        if type(now) != int or not 0 <= now <= MAX:
            raise AccountingError('explicit bounded clock required')
        with self._locked(False):
            r = self._replay()['reservations'].get(reservation)
        if not r or r['expires_at'] is None or now < r['expires_at']:
            raise AccountingError('reservation not expired at supplied clock')
        return self._command(key, 'expire', reservation=reservation)

    def market_event(self, key, typ, record):
        return self._command(key, typ, record=record)

    def snapshot(self):
        with self._locked(False):
            s = self._replay()
        return {'schema_version': VERSION, 'accounts': {k: {'balance': v, 'reserved': s['reserved'].get(k, 0), 'available': v - s['reserved'].get(k, 0)} for k, v in sorted(s['balances'].items())}, 'events': s['rows'], 'reservations': s['reservations'], 'market': s.get('market', []), 'head': s['rows'][-1]['hash'] if s['rows'] else _ZERO}

    def balances(self):
        return self.snapshot()['accounts']

    def export_csv(self, destination):
        from .paper_wallet import write_csv
        from .market import MarketGraph
        write_csv(MarketGraph.snapshot_from_accounting(self.snapshot()), destination)

    def csv_is_current(self, source):
        try:
            from .paper_wallet import write_csv
            from .market import MarketGraph
            actual = source.read()
            expected = io.StringIO()
            write_csv(MarketGraph.snapshot_from_accounting(self.snapshot()), expected)
            return actual == expected.getvalue()
        except (ValueError, TypeError, KeyError):
            return False

def _escape(value):
    return "'" + value if value[:1] in '=+-@\t\r\n' or value.lstrip()[:1] in '=+-@' else value
