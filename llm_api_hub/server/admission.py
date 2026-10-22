"""Fail-closed admission backed by a durable, cross-process SQLite ledger."""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import sqlite3
import time
import uuid
from pathlib import Path


class AdmissionDenied(RuntimeError):
    """A request cannot safely be admitted."""


def _timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp required")
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timezone required")
    return parsed.astimezone(dt.timezone.utc)


def bind_canonical_observation(observation, *, account_id, provider, model,
                               remaining_field, reset_at, verified_account=False,
                               verified_free_account=False, provider_model_mapping=None):
    """Convert normalized private manager output into bound, admissible evidence.

    The credential-owning adapter must affirm the account and free-account
    entitlement. A mapping from the exact hub model to provider family is also
    required to prevent a caller-selected model/provider mismatch.
    """
    if verified_account is not True or verified_free_account is not True or not isinstance(account_id, str) or not 1 <= len(account_id.strip()) <= 160:
        raise AdmissionDenied("account_binding_unverified")
    if not isinstance(provider_model_mapping, dict) or provider_model_mapping.get(model) != provider:
        raise AdmissionDenied("provider_model_mapping_unverified")
    if not isinstance(observation, dict) or observation.get("status") != "observed":
        raise AdmissionDenied("quota_unknown")
    if observation.get("provider_family") != provider:
        raise AdmissionDenied("provider_signal_mismatch")
    if remaining_field not in {"remaining_requests", "remaining_requests_day", "free_model_daily_remaining", "ratelimit_remaining"}:
        raise AdmissionDenied("signal_is_not_request_quota")
    if observation.get("scope_status") not in (None, "caller_declared_unverified"):
        raise AdmissionDenied("quota_scope_invalid")
    values = observation.get("signals")
    remaining = values.get(remaining_field) if isinstance(values, dict) else None
    if isinstance(remaining, bool) or not isinstance(remaining, int) or remaining < 0:
        raise AdmissionDenied("quota_unknown_or_unusable_signal")
    scope = observation.get("scope")
    if not isinstance(scope, str) or not 1 <= len(scope.strip()) <= 256:
        raise AdmissionDenied("quota_scope_unknown")
    obs = _timestamp(observation.get("observed_at"))
    reset = _timestamp(reset_at)
    if reset <= obs:
        raise AdmissionDenied("quota_reset_window_invalid")
    bound = {"account": account_id.strip(), "provider": provider, "model": model,
            "evidence_status": "confirmed", "horizon": "H0",
            "free_account_verified": True, "observed_at": obs.isoformat(),
            "reset_at": reset.isoformat(), "remaining": remaining,
            "scope": scope.strip()}
    token_count = values.get("remaining_tokens")
    if type(token_count) is int and token_count >= 0:
        bound["remaining_tokens"] = token_count
    return bound


class QuotaAdmission:
    def __init__(self, records_path=None, db_path=None, *, max_age=300):
        configured = records_path or os.environ.get("LLM_API_HUB_QUOTA_RECORDS")
        self.records_path = Path(configured) if configured else None
        self.db_path = Path(db_path or os.environ.get("LLM_API_HUB_QUOTA_DB", str(Path.home()/".cache/termux-hub-quota.sqlite3")))
        if isinstance(max_age, bool) or not isinstance(max_age, (int, float)) or not math.isfinite(max_age) or max_age < 0:
            raise ValueError("max_age must be finite and nonnegative")
        self.max_age = float(max_age)

    def _connect(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        # PRAGMA journal_mode can race on a brand-new database even with SQLite's
        # busy timeout. Serialize schema/WAL initialization, not the transactions.
        import fcntl
        flags = os.O_WRONLY | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
        lock_fd = os.open(str(self.db_path) + ".init.lock", flags, 0o600)
        db = None
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            fd = os.open(self.db_path, flags, 0o600)
            os.close(fd)
            os.chmod(self.db_path, 0o600)
            db = sqlite3.connect(str(self.db_path), timeout=20, isolation_level=None)
            db.execute("PRAGMA busy_timeout=20000")
            if db.execute("PRAGMA journal_mode").fetchone()[0] != "wal":
                db.execute("PRAGMA journal_mode=WAL")
            db.execute("""CREATE TABLE IF NOT EXISTS reservations (
                id TEXT PRIMARY KEY, attempt_id TEXT UNIQUE, account TEXT NOT NULL,
                provider TEXT NOT NULL, bucket TEXT NOT NULL, model TEXT NOT NULL,
                amount INTEGER NOT NULL, token_budget INTEGER NOT NULL, actual_tokens INTEGER,
                state TEXT NOT NULL, sent INTEGER NOT NULL DEFAULT 0,
                reset_at REAL NOT NULL, created REAL NOT NULL)""")
            db.execute("CREATE INDEX IF NOT EXISTS reservation_bucket ON reservations(account,provider,bucket,reset_at,state)")
            db.execute("""CREATE TABLE IF NOT EXISTS cooldowns (
                account TEXT NOT NULL, provider TEXT NOT NULL, bucket TEXT NOT NULL,
                until REAL NOT NULL, PRIMARY KEY(account,provider,bucket))""")
            db.execute("""CREATE TABLE IF NOT EXISTS quota_windows (
                account TEXT NOT NULL, provider TEXT NOT NULL, bucket TEXT NOT NULL,
                reset_at REAL NOT NULL, request_cap INTEGER, token_cap INTEGER,
                PRIMARY KEY(account,provider,bucket))""")
            columns = {row[1] for row in db.execute("PRAGMA table_info(quota_windows)")}
            for column in ("request_cap", "token_cap"):
                if column not in columns:
                    db.execute("ALTER TABLE quota_windows ADD COLUMN " + column + " INTEGER")
        except BaseException:
            if db is not None:
                db.close()
            raise
        finally:
            os.close(lock_fd)
        return db

    def _record(self, provider, model):
        if not self.records_path or not self.records_path.is_file():
            raise AdmissionDenied("quota_unknown")
        try:
            doc = json.loads(self.records_path.read_text(encoding="utf-8"))
            if not isinstance(doc, dict) or doc.get("schema_version") != 1 or not isinstance(doc.get("records"), list):
                raise ValueError("unsupported records schema")
            matches = [r for r in doc["records"] if isinstance(r, dict) and r.get("provider") == provider and r.get("model") == model]
            if len(matches) != 1:
                raise ValueError("record not unique")
            r = matches[0]
            obs, reset = _timestamp(r.get("observed_at")), _timestamp(r.get("reset_at"))
            now = dt.datetime.now(dt.timezone.utc)
            if r.get("evidence_status") != "confirmed" or r.get("horizon") != "H0" or r.get("free_account_verified") is not True or not isinstance(r.get("account"), str) or not r["account"].strip():
                raise ValueError("unverified binding")
            if obs > now or (now - obs).total_seconds() > self.max_age:
                raise AdmissionDenied("quota_stale")
            if reset <= now:
                raise AdmissionDenied("quota_reset_refresh_required")
            if r.get("cooldown_until") and _timestamp(r["cooldown_until"]) > now:
                raise AdmissionDenied("cooldown_active")
            remaining = r.get("remaining")
            if isinstance(remaining, bool) or not isinstance(remaining, int) or remaining < 0:
                raise AdmissionDenied("quota_exhausted_or_unknown")
            scope = r.get("scope")
            if not isinstance(scope, str) or not scope.strip():
                raise ValueError("scope missing")
            r = dict(r)
            for peer in doc["records"]:
                if not isinstance(peer, dict) or any(peer.get(key) != r.get(key) for key in ("provider", "account", "scope")):
                    continue
                count = peer.get("remaining")
                if type(count) is not int or count < 0:
                    raise ValueError("malformed shared-account request quota")
                remaining = min(remaining, count)
                count_tokens = peer.get("remaining_tokens")
                if count_tokens is not None:
                    if type(count_tokens) is not int or count_tokens < 0:
                        raise ValueError("malformed shared-account token quota")
                    r["remaining_tokens"] = min(r.get("remaining_tokens", count_tokens), count_tokens)
            return r, obs, reset, remaining, scope.strip()
        except AdmissionDenied:
            raise
        except Exception as exc:
            raise AdmissionDenied("quota_unknown_or_malformed") from exc

    def reserve(self, provider, model, amount=1, attempt_id=None, token_budget=0):
        for name, value, allow_zero in (("amount", amount, False), ("token_budget", token_budget, True)):
            if type(value) is not int or not 0 <= value <= 2**31 - 1 or (not allow_zero and value == 0):
                raise AdmissionDenied("invalid_" + name)
        if attempt_id is not None and (not isinstance(attempt_id, str) or not attempt_id.strip()):
            raise AdmissionDenied("invalid_attempt_id")
        r, obs, reset, remaining, scope = self._record(provider, model)
        token = uuid.uuid4().hex
        account, bucket, reset_epoch = r["account"].strip(), provider + ":" + scope, reset.timestamp()
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            now = time.time()
            cooldown = db.execute("SELECT until FROM cooldowns WHERE account=? AND provider=? AND bucket=?", (account, provider, bucket)).fetchone()
            if cooldown and cooldown[0] > now:
                raise AdmissionDenied("cooldown_active")
            if attempt_id and db.execute("SELECT 1 FROM reservations WHERE attempt_id=?", (attempt_id,)).fetchone():
                raise AdmissionDenied("duplicate_attempt")
            token_cap = r.get("remaining_tokens")
            if token_cap is not None and (type(token_cap) is not int or token_cap < 0):
                raise AdmissionDenied("token_quota_unknown_or_malformed")
            window = db.execute("SELECT reset_at,request_cap,token_cap FROM quota_windows WHERE account=? AND provider=? AND bucket=?", (account, provider, bucket)).fetchone()
            if window and window[0] > now:
                # Relative-reset headers and separately refreshed model rows may
                # drift. A refreshed timestamp is NOT a new spendable allowance.
                reset_epoch = window[0]
                remaining = min(remaining, window[1]) if window[1] is not None else remaining
                if window[2] is not None:
                    token_cap = min(token_cap, window[2]) if token_cap is not None else window[2]
            elif window and obs.timestamp() < window[0]:
                raise AdmissionDenied("quota_reset_refresh_required")
            db.execute("INSERT INTO quota_windows(account,provider,bucket,reset_at,request_cap,token_cap) VALUES(?,?,?,?,?,?) ON CONFLICT(account,provider,bucket) DO UPDATE SET reset_at=excluded.reset_at,request_cap=excluded.request_cap,token_cap=excluded.token_cap", (account, provider, bucket, reset_epoch, remaining, token_cap))
            used = db.execute("SELECT COALESCE(SUM(amount),0) FROM reservations WHERE account=? AND provider=? AND bucket=? AND reset_at=? AND state IN ('reserved','charged')", (account, provider, bucket, reset_epoch)).fetchone()[0]
            tokens = db.execute("SELECT COALESCE(SUM(CASE WHEN actual_tokens IS NULL THEN token_budget ELSE actual_tokens END),0) FROM reservations WHERE account=? AND provider=? AND bucket=? AND reset_at=? AND state IN ('reserved','charged')", (account, provider, bucket, reset_epoch)).fetchone()[0]
            if used + amount > remaining:
                raise AdmissionDenied("quota_exhausted")
            if token_cap is not None and tokens + token_budget > token_cap:
                raise AdmissionDenied("token_quota_exhausted")
            db.execute("INSERT INTO reservations(id,attempt_id,account,provider,bucket,model,amount,token_budget,state,reset_at,created) VALUES(?,?,?,?,?,?,?,?,?,?,?)", (token, attempt_id, account, provider, bucket, model, amount, token_budget, "reserved", reset_epoch, now))
            db.execute("COMMIT")
            return token
        except AdmissionDenied:
            # New conservative evidence remains authoritative even if no request
            # fits it; denying must not undo a lower shared-account ceiling.
            if db.in_transaction:
                db.execute("COMMIT")
            raise
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def mark_sent(self, token):
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT state FROM reservations WHERE id=?", (token,)).fetchone()
            if not row:
                db.execute("ROLLBACK")
                raise AdmissionDenied("reservation_unknown")
            if row[0] != "reserved":
                db.execute("ROLLBACK")
                raise AdmissionDenied("reservation_not_active")
            db.execute("UPDATE reservations SET sent=1 WHERE id=?", (token,))
            db.execute("COMMIT")
        return "sent"

    def reconcile(self, token, actual=1, actual_tokens=None, ambiguous=False):
        if actual is not None and (type(actual) is not int or not 0 <= actual <= 2**31 - 1):
            raise AdmissionDenied("invalid_actual")
        if actual_tokens is not None and (type(actual_tokens) is not int or not 0 <= actual_tokens <= 2**31 - 1):
            raise AdmissionDenied("invalid_actual_tokens")
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT state,sent,token_budget FROM reservations WHERE id=?", (token,)).fetchone()
            if not row:
                raise AdmissionDenied("reservation_unknown")
            state, sent, budget = row
            if state != "reserved":
                db.execute("COMMIT")
                return state
            if not sent and not ambiguous and actual == 0:
                state = "released"
            elif not sent:
                raise AdmissionDenied("reservation_not_sent")
            else:
                state = "charged"
            db.execute("UPDATE reservations SET state=?,actual_tokens=? WHERE id=? AND state='reserved'", (state, actual_tokens if actual_tokens is not None else (None if ambiguous or actual is None else (budget if actual > 0 else 0)), token))
            db.execute("COMMIT")
            return state
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def add_cooldown(self, token, seconds):
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds < 0:
            raise AdmissionDenied("invalid_cooldown")
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT account,provider,bucket,reset_at FROM reservations WHERE id=?", (token,)).fetchone()
            if not row:
                raise AdmissionDenied("reservation_unknown")
            account, provider, bucket, reset_at = row
            until = time.time() + seconds
            db.execute("INSERT INTO cooldowns VALUES(?,?,?,?) ON CONFLICT(account,provider,bucket) DO UPDATE SET until=MAX(until,excluded.until)", (account, provider, bucket, until))
            db.execute("COMMIT")
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()
        return until


# Construction is side-effect free; SQLite opens only for admitted execution.
admission = QuotaAdmission()
