"""Deterministic, non-executing CEDRlang codec and local A2A envelope validator.

This module deliberately has no filesystem mutation, subprocess, network, CEDARscript,
or CID dependency. A production mapper is supplied by an authorized caller; the repository
contains only synthetic test mappings.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import re
from types import MappingProxyType
import unicodedata
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID


CIR_SCHEMA_VERSION = "cedrlang.cir/v1"
A2A_PROTOCOL_VERSION = "cedrlang.a2a/v1"
A2A_ENVELOPE_FIELDS = frozenset(
    {
        "protocol_version",
        "message_id",
        "sender_role",
        "recipient_role",
        "correlation_id",
        "intent",
        "mapper_id",
        "mapper_version",
        "payload",
        "canonical_digest",
        "issued_at",
        "ttl_seconds",
        "state",
        "acknowledgement_id",
        "error_code",
    }
)
ALLOWED_RECORD_FIELDS = (
    "purpose",
    "directives",
    "constraints",
    "inputs",
    "outputs",
    "provenance",
)
ELIGIBLE_RECORD_FIELDS = ("purpose", "directives", "inputs", "outputs", "provenance")
EXCLUDED_RECORD_FIELDS = ("constraints",)
TOKEN_PATTERN = re.compile(r"\b[\w-]+\b", re.UNICODE)
HANDLE_PATTERN = re.compile(r"^§[A-Za-z0-9:_-]+§$")
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
ROLE_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
MAX_PAYLOAD_BYTES = 65_536


class CedrLangError(ValueError):
    """Base typed error for a rejected CEDRlang value."""


class RecordValidationError(CedrLangError):
    """Raised when a canonical record is malformed."""


class MapperValidationError(CedrLangError):
    """Raised when a mapper is malformed, ambiguous, or incompatible."""


class CoverageError(CedrLangError):
    """Raised when an enforced eligible-token coverage target is not met."""


class IntegrityError(CedrLangError):
    """Raised when an encoded record fails integrity verification."""


class A2AValidationError(CedrLangError):
    """Raised when a local A2A envelope is malformed or invalid."""


def _normalize_text(value: str) -> str:
    if not isinstance(value, str):
        raise RecordValidationError("record fields must contain only text values")
    normalized = unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n"))
    if any(ord(char) < 32 and char not in "\n\t" for char in normalized):
        raise RecordValidationError("record text contains unsupported control characters")
    return "\n".join(line.rstrip() for line in normalized.split("\n")).strip()


def _normalize_identifier(value: str, label: str) -> str:
    normalized = _normalize_text(value)
    if not ID_PATTERN.fullmatch(normalized):
        raise RecordValidationError(f"{label} must be a stable identifier")
    return normalized


def _normalize_literal_segment(value: str) -> str:
    """Validate a literal payload segment without stripping semantic whitespace."""
    if not isinstance(value, str):
        raise IntegrityError("literal encoded segments must contain text")
    normalized = unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n"))
    if any(ord(char) < 32 and char not in "\n\t" for char in normalized):
        raise IntegrityError("literal encoded segment contains unsupported control characters")
    return normalized


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _tokens(text: str) -> Tuple[str, ...]:
    return tuple(match.group(0).lower() for match in TOKEN_PATTERN.finditer(text))


def _freeze_json(value: Any) -> Any:
    """Return a deeply immutable representation of a JSON-native value."""
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze_json(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    return value


def _thaw_json(value: Any) -> Any:
    """Return a detached, mutable JSON-compatible copy of a frozen snapshot."""
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


def _snapshot_json_object(value: Mapping[str, Any]) -> Mapping[str, Any]:
    """Canonicalize, validate, and deeply freeze an object for envelope storage."""
    try:
        snapshot = json.loads(_canonical_json(_thaw_json(value)))
    except (TypeError, ValueError) as exc:
        raise A2AValidationError("payload must be JSON-serializable") from exc
    if not isinstance(snapshot, dict):
        raise A2AValidationError("payload must be an encoded record object")
    return _freeze_json(snapshot)


@dataclass(frozen=True)
class CanonicalRecord:
    """The authoritative normalized form for a CEDRlang instruction record."""

    schema_version: str
    document_id: str
    purpose: str
    directives: Sequence[str]
    constraints: Sequence[str]
    inputs: Sequence[str]
    outputs: Sequence[str]
    provenance: str

    def __post_init__(self) -> None:
        if self.schema_version != CIR_SCHEMA_VERSION:
            raise RecordValidationError(f"unsupported CIR schema version: {self.schema_version}")
        object.__setattr__(self, "document_id", _normalize_identifier(self.document_id, "document_id"))
        for field_name in ALLOWED_RECORD_FIELDS:
            value = getattr(self, field_name)
            if field_name in {"purpose", "provenance"}:
                object.__setattr__(self, field_name, _normalize_text(value))
            else:
                if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
                    raise RecordValidationError(f"{field_name} must be an ordered sequence of text")
                object.__setattr__(self, field_name, tuple(_normalize_text(item) for item in value))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "document_id": self.document_id,
            "purpose": self.purpose,
            "directives": list(self.directives),
            "constraints": list(self.constraints),
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
            "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "CanonicalRecord":
        if set(value) != {"schema_version", "document_id", *ALLOWED_RECORD_FIELDS}:
            raise RecordValidationError("CIR record has missing or unknown fields")
        return cls(**dict(value))

    def canonical_json(self) -> str:
        return _canonical_json(self.to_dict())

    def digest(self) -> str:
        return _sha256_text(self.canonical_json())


@dataclass(frozen=True)
class GrimoireMapper:
    """Immutable bijective symbolic mapper supplied by an authorized caller."""

    mapper_id: str
    version: str
    forward: Mapping[str, str]
    private: bool = False
    content_hash: str = field(init=False)
    reverse: Mapping[str, str] = field(init=False)

    def __post_init__(self) -> None:
        mapper_id = _normalize_identifier(self.mapper_id, "mapper_id")
        version = _normalize_text(self.version)
        if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?", version):
            raise MapperValidationError("mapper version must be semantic-version shaped")
        if not self.forward:
            raise MapperValidationError("mapper must contain at least one mapping")

        normalized_forward: Dict[str, str] = {}
        normalized_reverse: Dict[str, str] = {}
        for source, handle in self.forward.items():
            source_key = _normalize_text(source).lower()
            handle_value = _normalize_text(handle)
            if not source_key or not re.fullmatch(r"[\w-]+(?:[ \t]+[\w-]+)*", source_key, re.UNICODE):
                raise MapperValidationError("mapper sources must be normalized tokens or whitespace-separated phrases")
            if not HANDLE_PATTERN.fullmatch(handle_value):
                raise MapperValidationError("mapper entries require a well-formed symbolic handle")
            if source_key in normalized_forward:
                raise MapperValidationError("mapper contains duplicate normalized source tokens")
            if handle_value in normalized_reverse:
                raise MapperValidationError("mapper contains duplicate symbolic handles")
            normalized_forward[source_key] = handle_value
            normalized_reverse[handle_value] = source_key

        material = _canonical_json({"mapper_id": mapper_id, "version": version, "forward": normalized_forward})
        object.__setattr__(self, "mapper_id", mapper_id)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "forward", MappingProxyType(dict(normalized_forward)))
        object.__setattr__(self, "reverse", MappingProxyType(dict(normalized_reverse)))
        object.__setattr__(self, "content_hash", _sha256_text(material))


@dataclass(frozen=True)
class CoverageReport:
    mapper_id: str
    mapper_version: str
    mapper_content_hash: str
    canonical_digest: str
    replaced_eligible_tokens: int
    total_eligible_tokens: int
    excluded_fields: Tuple[str, ...]

    @property
    def coverage_ratio(self) -> float:
        if self.total_eligible_tokens == 0:
            return 1.0
        return self.replaced_eligible_tokens / self.total_eligible_tokens

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mapper_id": self.mapper_id,
            "mapper_version": self.mapper_version,
            "mapper_content_hash": self.mapper_content_hash,
            "canonical_digest": self.canonical_digest,
            "replaced_eligible_tokens": self.replaced_eligible_tokens,
            "total_eligible_tokens": self.total_eligible_tokens,
            "coverage_ratio": self.coverage_ratio,
            "excluded_fields": list(self.excluded_fields),
        }


def _encode_text(text: str, mapper: GrimoireMapper, eligible: bool) -> Tuple[List[Dict[str, str]], int, int]:
    """Encode exact-case mapper tokens or phrases while retaining non-lossless literals."""
    if not eligible:
        return [{"text": text}], 0, 0

    source_keys = sorted(mapper.forward, key=lambda source: (-len(_tokens(source)), -len(source), source))
    phrase_pattern = re.compile(
        r"(?<![\w-])(?:" + "|".join(re.escape(source) for source in source_keys) + r")(?![\w-])",
        re.UNICODE,
    )
    segments: List[Dict[str, str]] = []
    cursor = 0
    replaced = 0
    for match in phrase_pattern.finditer(text):
        if match.start() > cursor:
            segments.append({"text": text[cursor:match.start()]})
        phrase = match.group(0)
        # A lower-cased mapper key cannot reconstruct mixed-case source text. Retain
        # that literal rather than silently changing the canonical digest on decode.
        if phrase in mapper.forward:
            segments.append({"symbol": mapper.forward[phrase]})
            replaced += len(_tokens(phrase))
        else:
            segments.append({"text": phrase})
        cursor = match.end()
    if cursor < len(text) or not segments:
        segments.append({"text": text[cursor:]})
    return segments, replaced, len(_tokens(text))


def _decode_text(segments: Any, mapper: GrimoireMapper) -> str:
    if not isinstance(segments, Sequence) or isinstance(segments, (str, bytes)):
        raise IntegrityError("encoded text must be a list of literal or symbolic segments")
    decoded: List[str] = []
    for segment in segments:
        if not isinstance(segment, Mapping) or set(segment) not in ({"text"}, {"symbol"}):
            raise IntegrityError("encoded segment has an invalid shape")
        if "text" in segment:
            decoded.append(_normalize_literal_segment(segment["text"]))
        else:
            handle = segment["symbol"]
            if handle not in mapper.reverse:
                raise IntegrityError("encoded record references an unknown symbolic handle")
            decoded.append(mapper.reverse[handle])
    return "".join(decoded)


def _encoded_record_from_canonical(record: CanonicalRecord, mapper: GrimoireMapper) -> Tuple[Dict[str, Any], int, int]:
    encoded: Dict[str, Any] = {"schema_version": record.schema_version, "document_id": record.document_id}
    replaced = 0
    total = 0
    for field_name in ALLOWED_RECORD_FIELDS:
        value = getattr(record, field_name)
        eligible = field_name in ELIGIBLE_RECORD_FIELDS
        if field_name in {"purpose", "provenance"}:
            segments, field_replaced, field_total = _encode_text(value, mapper, eligible)
            encoded[field_name] = segments
            replaced += field_replaced
            total += field_total
        else:
            encoded_values: List[List[Dict[str, str]]] = []
            for item in value:
                segments, field_replaced, field_total = _encode_text(item, mapper, eligible)
                encoded_values.append(segments)
                replaced += field_replaced
                total += field_total
            encoded[field_name] = encoded_values
    return encoded, replaced, total


def encode_record(
    record: CanonicalRecord,
    mapper: GrimoireMapper,
    *,
    minimum_coverage: Optional[float] = None,
) -> Tuple[Dict[str, Any], CoverageReport]:
    """Encode a CIR record and produce integrity and coverage evidence."""
    if not isinstance(record, CanonicalRecord):
        raise RecordValidationError("encode_record requires a CanonicalRecord")
    encoded_record, replaced, total = _encoded_record_from_canonical(record, mapper)
    report = CoverageReport(
        mapper_id=mapper.mapper_id,
        mapper_version=mapper.version,
        mapper_content_hash=mapper.content_hash,
        canonical_digest=record.digest(),
        replaced_eligible_tokens=replaced,
        total_eligible_tokens=total,
        excluded_fields=EXCLUDED_RECORD_FIELDS,
    )
    if minimum_coverage is not None:
        if not 0.0 <= minimum_coverage <= 1.0:
            raise CoverageError("minimum coverage must be in the inclusive range [0, 1]")
        if report.coverage_ratio < minimum_coverage:
            raise CoverageError(
                f"eligible-token coverage {report.coverage_ratio:.3f} is below required {minimum_coverage:.3f}"
            )
    return (
        {
            "codec_version": CIR_SCHEMA_VERSION,
            "mapper": {
                "mapper_id": mapper.mapper_id,
                "version": mapper.version,
                "content_hash": mapper.content_hash,
                "private": mapper.private,
            },
            "canonical_digest": record.digest(),
            "record": encoded_record,
        },
        report,
    )


def decode_record(encoded: Mapping[str, Any], mapper: GrimoireMapper) -> CanonicalRecord:
    """Decode an authorized record and fail closed on mapper or integrity mismatch."""
    if not isinstance(encoded, Mapping):
        raise IntegrityError("encoded record must be an object")
    expected_fields = {"codec_version", "mapper", "canonical_digest", "record"}
    if set(encoded) != expected_fields:
        raise IntegrityError("encoded record has missing or unknown top-level fields")
    if encoded["codec_version"] != CIR_SCHEMA_VERSION:
        raise IntegrityError("unsupported codec version")
    mapper_info = encoded["mapper"]
    if not isinstance(mapper_info, Mapping):
        raise IntegrityError("encoded mapper metadata is invalid")
    if (
        mapper_info.get("mapper_id") != mapper.mapper_id
        or mapper_info.get("version") != mapper.version
        or mapper_info.get("content_hash") != mapper.content_hash
    ):
        raise IntegrityError("authorized mapper does not match encoded record metadata")
    raw = encoded["record"]
    if not isinstance(raw, Mapping) or set(raw) != {"schema_version", "document_id", *ALLOWED_RECORD_FIELDS}:
        raise IntegrityError("encoded CIR record has missing or unknown fields")
    decoded: Dict[str, Any] = {"schema_version": raw["schema_version"], "document_id": raw["document_id"]}
    for field_name in ALLOWED_RECORD_FIELDS:
        if field_name in {"purpose", "provenance"}:
            decoded[field_name] = _decode_text(raw[field_name], mapper)
        else:
            if not isinstance(raw[field_name], Sequence) or isinstance(raw[field_name], (str, bytes)):
                raise IntegrityError(f"encoded {field_name} must be a list")
            decoded[field_name] = [_decode_text(item, mapper) for item in raw[field_name]]
    record = CanonicalRecord.from_dict(decoded)
    if record.digest() != encoded["canonical_digest"]:
        raise IntegrityError("canonical digest mismatch")
    return record


def _parse_utc(value: str) -> datetime:
    if not isinstance(value, str):
        raise A2AValidationError("issued_at must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise A2AValidationError("issued_at is not an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise A2AValidationError("issued_at must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _validate_uuid(value: str, label: str) -> str:
    try:
        return str(UUID(value))
    except (TypeError, ValueError, AttributeError) as exc:
        raise A2AValidationError(f"{label} must be a UUID") from exc


@dataclass(frozen=True)
class A2AEnvelope:
    """Local-only A2A envelope carrying an encoded and integrity-bound CIR record."""

    protocol_version: str
    message_id: str
    sender_role: str
    recipient_role: str
    correlation_id: str
    intent: str
    mapper_id: str
    mapper_version: str
    payload: Mapping[str, Any]
    canonical_digest: str
    issued_at: str
    ttl_seconds: int
    state: str = "PENDING"
    acknowledgement_id: Optional[str] = None
    error_code: Optional[str] = None

    def __post_init__(self) -> None:
        if self.protocol_version != A2A_PROTOCOL_VERSION:
            raise A2AValidationError(f"unsupported A2A protocol version: {self.protocol_version}")
        object.__setattr__(self, "message_id", _validate_uuid(self.message_id, "message_id"))
        object.__setattr__(self, "correlation_id", _validate_uuid(self.correlation_id, "correlation_id"))
        try:
            for field_name in ("sender_role", "recipient_role"):
                value = _normalize_text(getattr(self, field_name))
                if not ROLE_PATTERN.fullmatch(value):
                    raise A2AValidationError(f"{field_name} must be a bounded role identifier")
                object.__setattr__(self, field_name, value)
            object.__setattr__(self, "intent", _normalize_identifier(self.intent, "intent"))
            object.__setattr__(self, "mapper_id", _normalize_identifier(self.mapper_id, "mapper_id"))
            object.__setattr__(self, "mapper_version", _normalize_text(self.mapper_version))
        except RecordValidationError as exc:
            raise A2AValidationError("envelope text fields are invalid") from exc
        if not isinstance(self.payload, Mapping):
            raise A2AValidationError("payload must be an encoded record object")
        if not isinstance(self.canonical_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", self.canonical_digest):
            raise A2AValidationError("canonical_digest must be a SHA-256 hexadecimal digest")
        if type(self.ttl_seconds) is not int or not 1 <= self.ttl_seconds <= 86_400:
            raise A2AValidationError("ttl_seconds must be between 1 and 86400")
        if self.state not in {"PENDING", "ACK", "NACK"}:
            raise A2AValidationError("state must be PENDING, ACK, or NACK")
        try:
            if self.state == "PENDING":
                if self.acknowledgement_id is not None or self.error_code is not None:
                    raise A2AValidationError("PENDING envelopes cannot include acknowledgement or error metadata")
            elif self.state == "ACK":
                if self.error_code is not None or not isinstance(self.acknowledgement_id, str):
                    raise A2AValidationError("ACK envelopes require only a string acknowledgement_id")
                object.__setattr__(
                    self,
                    "acknowledgement_id",
                    _normalize_identifier(self.acknowledgement_id, "acknowledgement_id"),
                )
            else:
                if self.acknowledgement_id is not None or not isinstance(self.error_code, str):
                    raise A2AValidationError("NACK envelopes require only a string error_code")
                object.__setattr__(self, "error_code", _normalize_identifier(self.error_code, "error_code"))
        except RecordValidationError as exc:
            raise A2AValidationError("envelope acknowledgement or error metadata is invalid") from exc
        payload_snapshot = _snapshot_json_object(self.payload)
        payload_bytes = len(_canonical_json(_thaw_json(payload_snapshot)).encode("utf-8"))
        if payload_bytes > MAX_PAYLOAD_BYTES:
            raise A2AValidationError("payload exceeds the local A2A size limit")
        object.__setattr__(self, "payload", payload_snapshot)
        _parse_utc(self.issued_at)

    def to_dict(self) -> Dict[str, Any]:
        """Return a transport-safe, explicit representation of this local envelope."""
        return {
            "protocol_version": self.protocol_version,
            "message_id": self.message_id,
            "sender_role": self.sender_role,
            "recipient_role": self.recipient_role,
            "correlation_id": self.correlation_id,
            "intent": self.intent,
            "mapper_id": self.mapper_id,
            "mapper_version": self.mapper_version,
            "payload": _thaw_json(self.payload),
            "canonical_digest": self.canonical_digest,
            "issued_at": self.issued_at,
            "ttl_seconds": self.ttl_seconds,
            "state": self.state,
            "acknowledgement_id": self.acknowledgement_id,
            "error_code": self.error_code,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "A2AEnvelope":
        """Parse only an exact serialized local-envelope schema; reject extras and omissions."""
        if not isinstance(value, Mapping) or set(value) != A2A_ENVELOPE_FIELDS:
            raise A2AValidationError("A2A envelope has missing or unknown fields")
        return cls(**dict(value))

    def transition(
        self,
        state: str,
        *,
        acknowledgement_id: Optional[str] = None,
        error_code: Optional[str] = None,
    ) -> "A2AEnvelope":
        if self.state != "PENDING":
            raise A2AValidationError("only PENDING envelopes may transition")
        if state not in {"ACK", "NACK"}:
            raise A2AValidationError("PENDING envelopes may transition only to ACK or NACK")
        return A2AEnvelope(
            protocol_version=self.protocol_version,
            message_id=self.message_id,
            sender_role=self.sender_role,
            recipient_role=self.recipient_role,
            correlation_id=self.correlation_id,
            intent=self.intent,
            mapper_id=self.mapper_id,
            mapper_version=self.mapper_version,
            payload=self.payload,
            canonical_digest=self.canonical_digest,
            issued_at=self.issued_at,
            ttl_seconds=self.ttl_seconds,
            state=state,
            acknowledgement_id=acknowledgement_id,
            error_code=error_code,
        )


def validate_a2a_envelope(
    envelope: A2AEnvelope,
    mapper: GrimoireMapper,
    *,
    now: Optional[datetime] = None,
) -> CanonicalRecord:
    """Validate an envelope locally and return its integrity-verified canonical record."""
    if envelope.mapper_id != mapper.mapper_id or envelope.mapper_version != mapper.version:
        raise A2AValidationError("envelope mapper metadata does not match the authorized mapper")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise A2AValidationError("validation time must include a UTC offset")
    issued = _parse_utc(envelope.issued_at)
    now_utc = now.astimezone(timezone.utc)
    if now_utc < issued:
        raise A2AValidationError("envelope issued_at is in the future")
    if (now_utc - issued).total_seconds() >= envelope.ttl_seconds:
        raise A2AValidationError("envelope TTL has expired")
    record = decode_record(envelope.payload, mapper)
    if record.digest() != envelope.canonical_digest:
        raise A2AValidationError("envelope canonical digest does not match payload")
    return record


def classify_replay(seen_messages: Mapping[str, str], envelope: A2AEnvelope) -> str:
    """Classify a message ID without any persistence or side effects."""
    observed = seen_messages.get(envelope.message_id)
    if observed is None:
        return "new"
    if observed == envelope.canonical_digest:
        return "idempotent_duplicate"
    return "conflict"
