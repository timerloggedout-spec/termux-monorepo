from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from workspace.compression_sandbox.cedrlang.protocol import (
    A2AEnvelope,
    A2AValidationError,
    CanonicalRecord,
    CoverageError,
    GrimoireMapper,
    IntegrityError,
    MapperValidationError,
    classify_replay,
    decode_record,
    encode_record,
    validate_a2a_envelope,
)


def build_mapper() -> GrimoireMapper:
    return GrimoireMapper(
        mapper_id="test-grimoire",
        version="1.0.0",
        forward={
            "inspect": "§I§",
            "system": "§S§",
            "status": "§T§",
            "agent": "§A§",
            "send": "§N§",
            "message": "§M§",
            "verify": "§V§",
            "unit-test": "§U§",
        },
    )


def build_record() -> CanonicalRecord:
    return CanonicalRecord(
        schema_version="cedrlang.cir/v1",
        document_id="agent-instruction-001",
        purpose="inspect system status",
        directives=["agent send message", "verify status"],
        constraints=["human approval required"],
        inputs=["system status"],
        outputs=["verify status"],
        provenance="unit-test",
    )


def test_canonical_record_normalizes_and_hashes_deterministically():
    record = CanonicalRecord(
        schema_version="cedrlang.cir/v1",
        document_id="record-1",
        purpose=" inspect system\r\n",
        directives=["agent send message  "],
        constraints=[" human approval required\t"],
        inputs=[],
        outputs=[],
        provenance=" test ",
    )

    equivalent = CanonicalRecord(
        schema_version="cedrlang.cir/v1",
        document_id="record-1",
        purpose="inspect system\n",
        directives=["agent send message"],
        constraints=["human approval required"],
        inputs=[],
        outputs=[],
        provenance="test",
    )

    assert record.to_dict() == equivalent.to_dict()
    assert record.digest() == equivalent.digest()


def test_mapper_rejects_duplicate_symbol_handles():
    with pytest.raises(MapperValidationError):
        GrimoireMapper(
            mapper_id="invalid",
            version="1.0.0",
            forward={"inspect": "§D§", "system": "§D§"},
        )


def test_codec_encodes_multi_word_mapper_sources_deterministically():
    mapper = GrimoireMapper(
        mapper_id="phrase-grimoire",
        version="1.0.0",
        forward={"inspect system": "§IS§", "status": "§T§", "unit-test": "§U§"},
    )
    record = CanonicalRecord(
        schema_version="cedrlang.cir/v1",
        document_id="phrase-record",
        purpose="inspect system status",
        directives=[],
        constraints=[],
        inputs=[],
        outputs=[],
        provenance="unit-test",
    )

    encoded, report = encode_record(record, mapper, minimum_coverage=1.0)

    assert encoded["record"]["purpose"] == [{"symbol": "§IS§"}, {"text": " "}, {"symbol": "§T§"}]
    assert report.coverage_ratio == 1.0
    assert decode_record(encoded, mapper) == record


def test_codec_retains_mixed_case_tokens_when_mapper_cannot_reconstruct_case():
    mapper = build_mapper()
    record = CanonicalRecord(
        schema_version="cedrlang.cir/v1",
        document_id="mixed-case-record",
        purpose="Inspect system status",
        directives=[],
        constraints=[],
        inputs=[],
        outputs=[],
        provenance="unit-test",
    )

    encoded, _ = encode_record(record, mapper)
    decoded = decode_record(encoded, mapper)

    assert encoded["record"]["purpose"][0] == {"text": "Inspect "}
    assert decoded == record
    assert decoded.digest() == encoded["canonical_digest"]


def test_codec_is_lossless_deterministic_and_measures_eligible_coverage():
    mapper = build_mapper()
    record = build_record()

    encoded_one, report_one = encode_record(record, mapper, minimum_coverage=0.70)
    encoded_two, report_two = encode_record(record, mapper, minimum_coverage=0.70)

    assert encoded_one == encoded_two
    assert report_one.to_dict() == report_two.to_dict()
    assert report_one.replaced_eligible_tokens == report_one.total_eligible_tokens
    assert report_one.coverage_ratio == 1.0
    assert report_one.excluded_fields == ("constraints",)
    assert decode_record(encoded_one, mapper) == record


def test_codec_preserves_literal_symbol_text_without_collision():
    mapper = build_mapper()
    record = CanonicalRecord(
        schema_version="cedrlang.cir/v1",
        document_id="literal-handle",
        purpose="literal §I§ inspect",
        directives=[],
        constraints=[],
        inputs=[],
        outputs=[],
        provenance="unit-test",
    )

    encoded, _ = encode_record(record, mapper)
    assert decode_record(encoded, mapper) == record
    assert [segment for segment in encoded["record"]["purpose"] if "symbol" in segment] == [{"symbol": "§I§"}]


def test_codec_rejects_insufficient_coverage_and_integrity_tampering():
    mapper = build_mapper()
    record = CanonicalRecord(
        schema_version="cedrlang.cir/v1",
        document_id="coverage-record",
        purpose="unmapped prose",
        directives=[],
        constraints=[],
        inputs=[],
        outputs=[],
        provenance="unit-test",
    )

    with pytest.raises(CoverageError):
        encode_record(record, mapper, minimum_coverage=0.70)

    encoded, _ = encode_record(build_record(), mapper)
    tampered = deepcopy(encoded)
    tampered["record"]["purpose"][0] = {"text": "corrupted "}

    with pytest.raises(IntegrityError):
        decode_record(tampered, mapper)


def test_a2a_envelope_validates_digest_ttl_state_and_replay_behavior():
    mapper = build_mapper()
    record = build_record()
    encoded, _ = encode_record(record, mapper)
    now = datetime(2026, 8, 20, 0, 0, tzinfo=timezone.utc)
    envelope = A2AEnvelope(
        protocol_version="cedrlang.a2a/v1",
        message_id=str(uuid4()),
        sender_role="linguist",
        recipient_role="reviewer",
        correlation_id=str(uuid4()),
        intent="instruction-transfer",
        mapper_id=mapper.mapper_id,
        mapper_version=mapper.version,
        payload=encoded,
        canonical_digest=record.digest(),
        issued_at=now.isoformat(),
        ttl_seconds=60,
    )

    decoded = validate_a2a_envelope(envelope, mapper, now=now + timedelta(seconds=30))
    assert decoded == record
    assert classify_replay({}, envelope) == "new"
    assert classify_replay({envelope.message_id: envelope.canonical_digest}, envelope) == "idempotent_duplicate"
    assert classify_replay({envelope.message_id: "different"}, envelope) == "conflict"

    with pytest.raises(A2AValidationError):
        validate_a2a_envelope(envelope, mapper, now=now + timedelta(seconds=60))

    with pytest.raises(A2AValidationError):
        validate_a2a_envelope(envelope, mapper, now=now + timedelta(seconds=61))

    with pytest.raises(A2AValidationError):
        validate_a2a_envelope(envelope, mapper, now=now - timedelta(seconds=1))

    acknowledged = envelope.transition("ACK", acknowledgement_id="ack-001")
    assert acknowledged.state == "ACK"
    with pytest.raises(A2AValidationError):
        acknowledged.transition("NACK", error_code="not-allowed")


def test_a2a_envelope_serialization_rejects_unknown_missing_and_malformed_payloads():
    mapper = build_mapper()
    record = build_record()
    encoded, _ = encode_record(record, mapper)
    envelope = A2AEnvelope(
        protocol_version="cedrlang.a2a/v1",
        message_id=str(uuid4()),
        sender_role="linguist",
        recipient_role="reviewer",
        correlation_id=str(uuid4()),
        intent="instruction-transfer",
        mapper_id=mapper.mapper_id,
        mapper_version=mapper.version,
        payload=encoded,
        canonical_digest=record.digest(),
        issued_at=datetime(2026, 8, 20, tzinfo=timezone.utc).isoformat(),
        ttl_seconds=60,
    )

    source_payload = deepcopy(encoded)
    isolated = A2AEnvelope(
        protocol_version="cedrlang.a2a/v1",
        message_id=str(uuid4()),
        sender_role="linguist",
        recipient_role="reviewer",
        correlation_id=str(uuid4()),
        intent="instruction-transfer",
        mapper_id=mapper.mapper_id,
        mapper_version=mapper.version,
        payload=source_payload,
        canonical_digest=record.digest(),
        issued_at=datetime(2026, 8, 20, tzinfo=timezone.utc).isoformat(),
        ttl_seconds=60,
    )
    source_payload["record"]["purpose"][0] = {"text": "mutated source"}
    detached = isolated.to_dict()
    detached["payload"]["record"]["purpose"][0] = {"text": "mutated serialization"}
    assert isolated.to_dict()["payload"] == encoded
    assert isolated.transition("ACK", acknowledgement_id="ack-001").to_dict()["payload"] == encoded

    serialized = envelope.to_dict()
    assert A2AEnvelope.from_dict(serialized) == envelope
    assert set(serialized) == {
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

    missing = dict(serialized)
    missing.pop("payload")
    with pytest.raises(A2AValidationError):
        A2AEnvelope.from_dict(missing)

    unknown = dict(serialized)
    unknown["unexpected"] = "value"
    with pytest.raises(A2AValidationError):
        A2AEnvelope.from_dict(unknown)

    malformed = dict(serialized)
    malformed["payload"] = ["not", "an", "object"]
    with pytest.raises(A2AValidationError):
        A2AEnvelope.from_dict(malformed)
